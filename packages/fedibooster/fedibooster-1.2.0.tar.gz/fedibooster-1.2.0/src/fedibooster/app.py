"""High level logic for lemmy2feed."""

import asyncio
import json
import re
import sys
from datetime import UTC
from datetime import datetime
from datetime import timedelta
from hashlib import sha256
from pathlib import Path
from typing import Annotated
from typing import Optional
from urllib.parse import urlparse

import msgspec.toml
import stamina
import typer
from httpx import AsyncClient
from loguru import logger as log
from minimal_activitypub import SearchType
from minimal_activitypub import Status
from minimal_activitypub.client_2_server import ActivityPub
from minimal_activitypub.client_2_server import NetworkError
from minimal_activitypub.client_2_server import RatelimitError
from stamina import retry

from fedibooster import __version__
from fedibooster.config import Configuration
from fedibooster.config import Fediverse
from fedibooster.config import create_default_config
from fedibooster.control import PostRecorder

stamina.instrumentation.set_on_retry_hooks([])


@log.catch
async def main(config_path: Path, max_posts: int | None) -> None:
    """Read communities and post to fediverse account."""
    log.info(f"Welcome to fedibooster({__version__})")

    if config_path.exists():
        with config_path.open(mode="rb") as config_file:
            config_content = config_file.read()
            config = msgspec.toml.decode(config_content, type=Configuration)

    else:
        config = await create_default_config()
        log.debug(f"{config=}")
        with config_path.open(mode="wb") as config_file:
            config_file.write(msgspec.toml.encode(config))
        print("Please review your config file, adjust as needed, and run fedibooster again.")
        sys.exit(0)

    async with AsyncClient(http2=True, timeout=30) as client:
        try:
            instance: ActivityPub
            my_username: str
            instance, my_username = await connect(auth=config.fediverse, client=client)
        except NetworkError as error:
            log.info(f"Unable to connect to your Fediverse account with {error=}")
            log.opt(colors=True).info("<red><bold>Can't continue!</bold></red> ... Exiting")
            sys.exit(1)

        with PostRecorder(history_db_path=config.history_db_path) as recorder:
            while True:
                # Boost timeline posts
                max_reblogs = min(max_posts, config.fediverse.max_reblog) if max_posts else config.fediverse.max_reblog
                try:
                    await boost_statuses_with_hashtags(
                        instance=instance,
                        my_username=my_username,
                        recorder=recorder,
                        max_boosts=max_reblogs,
                        no_reblog_tags=config.fediverse.no_reblog_tags,
                        no_reblog_users=config.fediverse.no_reblog_users,
                        post_recorder=recorder,
                        client=client,
                        search_instance=config.fediverse.search_instance,
                        tags=config.fediverse.search_tags,
                        reblog_sensitive=config.reblog_sensitive,
                    )
                except NetworkError as error:
                    log.warning(f"We've encountered the following error when boosting statuses: {error}")

                recorder.prune(max_age_in_days=config.history_prune_age)

                if not config.run_continuously:
                    break

                wait_until = datetime.now(tz=UTC) + timedelta(seconds=config.delay_between_posts)
                log.opt(colors=True).info(
                    f"<dim>Waiting until {wait_until:%Y-%m-%d %H:%M:%S %z} "
                    f"({config.delay_between_posts}s) before checking again.</>"
                )
                await asyncio.sleep(delay=config.delay_between_posts)


async def boost_statuses_with_hashtags(  # noqa: PLR0913
    instance: ActivityPub,
    my_username: str,
    recorder: PostRecorder,
    max_boosts: int,
    no_reblog_tags: list[str],
    no_reblog_users: list[str],
    post_recorder: PostRecorder,
    client: AsyncClient,
    search_instance: str,
    tags: list[str],
    reblog_sensitive: bool,
) -> None:
    """Boost posts on home timeline."""
    retry_caller = stamina.AsyncRetryingCaller(attempts=3)
    max_id: str = recorder.get_setting(key="max-boosted-id")

    search_on: str = search_instance if search_instance else instance.instance

    statuses = await get_statuses_with_tags(search_instance=search_on, tags=tags)

    number_boosted: int = 0

    if not statuses:
        return

    for status in reversed(statuses):
        status_id = status.get("id")

        # Check for any reason to skip reblogging this status
        if recorder.is_duplicate(identifiers=[status_id, status.get("url"), status.get("ap_id")]):
            continue
        if (
            bot_status(status=status)
            or sensitive_status_blocked(status=status, reblog_sensitive=reblog_sensitive)
            or my_own_status(status=status, my_username=my_username)
            or no_attachments(status=status)
            or has_no_reblog_tag(status=status, no_reblog_tags=no_reblog_tags)
            or by_no_reblog_user(status=status, no_reblog_users=no_reblog_users, search_host=search_instance)
        ):
            recorder.log_post(id=status_id, url=status.get("url"), ap_id=status.get("ap_id"))
            continue

        # Check Attachments haven't been boosted / rebloged yet
        attachment_hash: Optional[str] = None
        for attachment in status.get("media_attachments", []):
            attachment_hash = await determine_attachment_hash(url=attachment.get("url"), client=client)
            if post_recorder.is_duplicate(identifiers=[attachment_hash]):
                log.opt(colors=True).info(
                    f"<dim><red>Not Boosting:</red> At least one attachment of status at "
                    f"<cyan>{status.get('url')}</cyan> has already been boosted or posted.</dim>"
                )
                recorder.log_post(id=status_id, url=status.get("url"), ap_id=status.get("ap_id"))
                break

        # Do the actual reblog
        status_url = status.get("url")
        search_result = await instance.search(query=status_url, query_type=SearchType.STATUSES, resolve=True)
        status_to_reblog = search_result.get("statuses")[0] if search_result.get("statuses") else None
        if status_to_reblog:
            reblog_id = status_to_reblog.get("id")
            await retry_caller(NetworkError, instance.reblog, status_id=reblog_id)
            number_boosted += 1
            log.opt(colors=True).info(f"Boosted <cyan>{status_url}</>")
            recorder.log_post(
                attachment_hash=attachment_hash,
                id=status_id,
                url=status.get("url"),
                ap_id=status.get("ap_id"),
            )

            max_id = status_id

        if number_boosted >= max_boosts:
            break

    recorder.save_setting(key="max-boosted-id", value=max_id)


async def get_statuses_with_tags(search_instance: str, tags: list[str]) -> list[Status]:
    """Get statuses found on search_instance with tags."""
    statuses: list[Status] = []

    retry_caller = stamina.AsyncRetryingCaller(attempts=3)
    try:
        statuses = await retry_caller(NetworkError, get_hashtag_timeline, search_instance=search_instance, tags=tags)
    except NetworkError as error:
        log.opt(colors=True).info(f"<dim>encountered {error=}</dim>")
    except RatelimitError:
        log.opt(colors=True).info("<dim>We've been rate limited... waiting for 30 minutes</dim>")
        await asyncio.sleep(1800)

    return statuses


def by_no_reblog_user(status: Status, no_reblog_users: list[str], search_host: str) -> bool:
    """Check if status was posted by a user in the no_reblog_users list."""
    username = status.get("account", {}).get("acct")
    if "@" not in username:
        username = expand_local_user(username=username, search_host=search_host)

    for no_reblog_user in no_reblog_users:
        if re.search(rf"{no_reblog_user}", username):
            log.opt(colors=True).info(
                f"<dim><red>Not Boosting</red> <cyan>{status.get('url', '')}</cyan> "
                f"because it was posted by a '{username}' who is a match in for {no_reblog_user} "
                f"in the no_reblog_users list</dim>"
            )
            return True

    return False


def expand_local_user(username: str, search_host: str) -> str:
    """Expand username that don't contain a hostname."""
    hostname = search_host
    parsed = urlparse(url=search_host)
    if parsed.hostname:
        hostname = parsed.hostname
    expanded_username = f"{username}@{hostname}"
    log.debug(f"Expanded {username} to {expanded_username}")

    return expanded_username


def has_no_reblog_tag(status: Status, no_reblog_tags: list[str]) -> bool:
    """Check if status contains any tag in the no_reblog_tags list."""
    status_tags: list[str] = [x["name"].casefold() for x in status.get("tags", [])]
    if any(no_reblog.casefold() in status_tags for no_reblog in no_reblog_tags):
        log.opt(colors=True).info(
            f"<dim><red>Not Boosting</red> <cyan>{status.get('url', '')}</cyan> "
            f"because it contains tags that are in the no_reblog_tags list</dim>"
        )
        return True

    return False


def no_attachments(status: Status) -> bool:
    """Check if the status as NO attachments."""
    if not len(status.get("media_attachments", [])):
        log.opt(colors=True).info(
            f"<dim><red>Not Boosting</red> <cyan>{status.get('url', '')}</cyan> "
            f"because it has no attachments / media</dim>"
        )
        return True

    return False


def my_own_status(status: Status, my_username: str) -> bool:
    """Check if the status was posted by myself."""
    if status.get("account", {}).get("username") == my_username:
        log.opt(colors=True).debug(
            f"<dim><red>Skipping</red> post from myself - <cyan>{status.get('url', '')}</cyan></dim>"
        )
        return True

    return False


def sensitive_status_blocked(status: Status, reblog_sensitive: bool) -> bool:
    """Check if the status is marked as sensitive and if check if we allow rebloging sensitve statuses."""
    status_sensitive: bool = status.get("sensitive", False)
    if status_sensitive and not reblog_sensitive:
        log.opt(colors=True).debug(
            f"<dim><red>Not Boosting</red> sensitive status - <cyan>{status.get('url', '')}</cyan></dim>"
        )
        return True

    return False


def bot_status(status: Status) -> bool:
    """Check if status has been made by a bot account."""
    if status.get("account", {}).get("bot"):
        log.opt(colors=True).info(
            f"<dim><red>Not Boosting</red> <cyan>{status.get('url', '')}</cyan> because it was posted by a bot</dim>"
        )
        return True

    return False


def async_shim(
    config_path: Annotated[Path, typer.Argument(help="path to config file")],
    logging_config_path: Annotated[
        Optional[Path], typer.Option("-l", "--logging-config", help="Full Path to logging config file")
    ] = None,
    max_posts: Annotated[
        Optional[int], typer.Option(help="maximum number of posts and reblogs before quitting")
    ] = None,
) -> None:
    """Start async part."""
    if logging_config_path and logging_config_path.is_file():
        with logging_config_path.open(mode="rb") as log_config_file:
            logging_config = msgspec.toml.decode(log_config_file.read())

        for handler in logging_config.get("handlers"):
            if handler.get("sink") == "sys.stdout":
                handler["sink"] = sys.stdout

        log.configure(**logging_config)

    asyncio.run(main(config_path=config_path, max_posts=max_posts))


def typer_shim() -> None:
    """Run actual code."""
    try:
        typer.run(async_shim)
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    typer.run(async_shim)


@retry(on=NetworkError, attempts=3)
async def connect(auth: Fediverse, client: AsyncClient) -> tuple[ActivityPub, str]:
    """Connect to fediverse instance server and initialise some values."""
    activity_pub = ActivityPub(
        instance=auth.domain_name,
        access_token=auth.api_token,
        client=client,
    )
    await activity_pub.determine_instance_type()

    user_info = await activity_pub.verify_credentials()

    log.info(f"Successfully authenticated as @{user_info['username']} on {auth.domain_name}")

    return activity_pub, user_info["username"]


@stamina.retry(on=NetworkError, attempts=3)
async def get_hashtag_timeline(search_instance: str, tags: list[str]) -> list[Status]:
    """Search for statuses with 'tags' on 'search_instance'."""
    first_tag = tags[0]
    any_other_tags = tags[1:] if len(tags) > 1 else None
    async with AsyncClient(http2=True, timeout=30) as client:
        search_on = ActivityPub(instance=search_instance, client=client)
        results: list[Status] = await search_on.get_hashtag_timeline(
            hashtag=first_tag,
            any_tags=any_other_tags,
            only_media=True,
            limit=40,
        )

    log.debug(f"results={json.dumps(results, indent=4)}")

    return results


async def determine_attachment_hash(url: str, client: AsyncClient) -> str:
    """Determine attachment hash."""
    response = await client.get(url=url)
    url_hash = sha256(response.content).hexdigest()
    return url_hash
