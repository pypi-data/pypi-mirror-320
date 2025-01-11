# ruff: noqa: D100, D103, S101


from minimal_activitypub import Status

from fedibooster.app import bot_status
from fedibooster.app import by_no_reblog_user
from fedibooster.app import expand_local_user
from fedibooster.app import has_no_reblog_tag
from fedibooster.app import my_own_status
from fedibooster.app import no_attachments
from fedibooster.app import sensitive_status_blocked


def test_no_reblog_user() -> None:
    status: Status = {"account": {"acct": "reblog"}}
    no_reblog_users = ["no_reblog", "SPAMMER@mastodon.social", "@threads.net", "zuck@meta$"]
    result = by_no_reblog_user(status=status, no_reblog_users=no_reblog_users, search_host="https://mastodon.social")
    assert not result

    status = {"account": {"acct": "SPAMMER"}}
    result = by_no_reblog_user(status=status, no_reblog_users=no_reblog_users, search_host="https://mastodon.social")
    assert result

    status = {"account": {"acct": "zuck@meta.net"}}
    result = by_no_reblog_user(status=status, no_reblog_users=no_reblog_users, search_host="https://mastodon.social")
    assert not result

    status = {"account": {"acct": "zuck@threads.net"}}
    result = by_no_reblog_user(status=status, no_reblog_users=no_reblog_users, search_host="https://mastodon.social")
    assert result


def test_has_no_reblog_tag() -> None:
    status: Status = {
        "tags": [
            {"name": "cats", "url": "https..."},
            {"name": "kittens", "url": "https..."},
        ]
    }
    no_reblog_tags = ["dogs", "art"]
    result = has_no_reblog_tag(status=status, no_reblog_tags=no_reblog_tags)
    assert not result

    status = {
        "tags": [
            {"name": "dogs", "url": "https..."},
            {"name": "kittens", "url": "https..."},
        ]
    }
    result = has_no_reblog_tag(status=status, no_reblog_tags=no_reblog_tags)
    assert result


def test_no_attachments() -> None:
    status: Status = {
        "media_attachments": [
            {"id": "1265234521", "type": "image"},
            {"id": "6978123765", "type": "video"},
        ]
    }
    result = no_attachments(status=status)
    assert not result

    status = {"account": {"acct": "reblog"}}
    result = no_attachments(status=status)
    assert result


def test_my_own_status() -> None:
    status: Status = {"account": {"username": "username123"}}
    result = my_own_status(status=status, my_username="me_myself_and_i")
    assert not result

    result = my_own_status(status=status, my_username="username123")
    assert result


def test_sensitive_status_blocked() -> None:
    status: Status = {"account": {"username": "username123"}}
    result = sensitive_status_blocked(status=status, reblog_sensitive=False)
    assert not result

    status = {"account": {"username": "username123"}, "sensitive": True}
    result = sensitive_status_blocked(status=status, reblog_sensitive=True)
    assert not result

    result = sensitive_status_blocked(status=status, reblog_sensitive=False)
    assert result


def test_bot_status() -> None:
    status: Status = {"account": {"username": "username123"}}
    result = bot_status(status=status)
    assert not result

    status = {"account": {"username": "username123", "bot": False}}
    result = bot_status(status=status)
    assert not result

    status = {"account": {"username": "username123", "bot": True}}
    result = bot_status(status=status)
    assert result


def test_expand_user() -> None:
    username = "brainpilgrim"
    search_instance = "https://mastodon.social"
    result = expand_local_user(username=username, search_host=search_instance)
    assert result == "brainpilgrim@mastodon.social"

    username = "brainpilgrim"
    search_instance = "mastodon.social"
    result = expand_local_user(username=username, search_host=search_instance)
    assert result == "brainpilgrim@mastodon.social"
