# ruff: noqa: D100, D103, S101


from fedibooster.config import Configuration
from fedibooster.config import Fediverse


def test_fediverse() -> None:
    fediverse = Fediverse(domain_name="fediverse.instance", api_token="token")  # noqa: S106

    assert fediverse.max_reblog == 5
    assert fediverse.no_reblog_tags == []
    assert fediverse.no_reblog_users == []
    assert fediverse.search_instance == ""
    assert fediverse.search_tags == []


def test_configuration() -> None:
    fediverse = Fediverse(domain_name="fediverse.instance", api_token="token")  # noqa: S106

    config = Configuration(
        fediverse=fediverse,
        run_continuously=False,
        delay_between_posts=3600,
        history_db_path="/tmp/history.sqlite",  # noqa: S108
    )

    assert config.history_prune_age == 30
    assert not config.reblog_sensitive
