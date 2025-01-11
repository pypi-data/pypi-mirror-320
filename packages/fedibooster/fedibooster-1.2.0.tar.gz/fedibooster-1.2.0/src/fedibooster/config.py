"""Classes and methods to control configuration of fedibooster."""

import msgspec
from httpx import AsyncClient
from minimal_activitypub.client_2_server import ActivityPub

from fedibooster import USER_AGENT


class Fediverse(msgspec.Struct):
    """Config values for Fediverse account to cross post to."""

    domain_name: str
    api_token: str
    max_reblog: int = 5
    no_reblog_tags: list[str] = []
    no_reblog_users: list[str] = []
    search_instance: str = ""
    search_tags: list[str] = []


class Configuration(msgspec.Struct):
    """Config for bot."""

    fediverse: Fediverse
    run_continuously: bool
    delay_between_posts: int
    history_db_path: str
    history_prune_age: int = 30  # Prune history records older than this in days
    reblog_sensitive: bool = False


async def create_default_config() -> Configuration:
    """Create default configuration."""
    domain_name = input("Please enter the url for your Fediverse instance: ")

    async with AsyncClient(http2=True, timeout=30) as client:
        client_id, client_secret = await ActivityPub.create_app(
            instance_url=domain_name,
            user_agent=USER_AGENT,
            client=client,
        )
        auth_url = await ActivityPub.generate_authorization_url(
            instance_url=domain_name,
            client_id=client_id,
            user_agent=USER_AGENT,
        )

        print("Please go to the following URL and follow the prompts to authorize fedibooster to use your account:")
        print(f"{auth_url}")
        auth_code = input("Please provide the authorization token provided by your instance: ")

        auth_token = await ActivityPub.validate_authorization_code(
            client=client,
            instance_url=domain_name,
            authorization_code=auth_code,
            client_id=client_id,
            client_secret=client_secret,
        )

    return Configuration(
        fediverse=Fediverse(
            domain_name=domain_name,
            api_token=auth_token,
            max_reblog=5,
            no_reblog_tags=["no-reblog"],
            no_reblog_users=["bad_user", "spammer"],
            search_instance="mastodon.social",
            search_tags=["tag1", "tag2"],
        ),
        run_continuously=False,
        delay_between_posts=300,
        history_db_path="history.sqlite",
    )
