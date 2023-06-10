from spaceterminal.client import Client


def test_client():
    """Tests that client will update authentication when access token is assigned."""
    old_token = "old-token"
    new_token = "new-token"

    client = Client(old_token)
    assert client.auth.access_token == old_token
    assert client.session.auth.access_token == old_token
    assert client.session.headers == {
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    client.access_token = new_token
    assert client.auth.access_token == new_token
    assert client.session.auth.access_token == new_token
