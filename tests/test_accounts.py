from datetime import datetime, timedelta

from gardena_smartsystem_prometheus_exporter.iapi.accounts import Account, AccountStore


def make_account(expires: datetime) -> Account:
    return Account(
        user_id="user-1",
        location_id="loc-1",
        client_id="client-1",
        client_secret="secret",
        token="token-abc",
        expires=expires,
    )


def test_account_not_expired():
    account = make_account(expires=datetime.now() + timedelta(minutes=10))
    assert account.expires > datetime.now()


def test_account_expired():
    account = make_account(expires=datetime.now() - timedelta(seconds=1))
    assert account.expires < datetime.now()


def test_accountstore_refreshes_when_expired():
    AccountStore._account = make_account(expires=datetime.now() - timedelta(seconds=1))
    assert AccountStore._account.expires < datetime.now()


def test_accountstore_reuses_valid_account():
    account = make_account(expires=datetime.now() + timedelta(minutes=10))
    AccountStore._account = account
    assert AccountStore._account is account
