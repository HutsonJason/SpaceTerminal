import requests
import requests_mock

from spaceterminal.agent import Agent
from spaceterminal.client import Client
from spaceterminal.constants import URL

ACCESS_TOKEN = "old-token"
CLIENT = Client(ACCESS_TOKEN)
JSON_GET_PASS = {
    "data": {
        "accountId": "test-account1234",
        "symbol": "TEST-SYMBOL",
        "headquarters": "TEST-1234-5678",
        "credits": 123456,
        "startingFaction": "COSMIC",
    }
}
JSON_GET_FAIL = {"error": {"message": "A failed response", "code": 4103}}
JSON_POST_PASS = {
    "data": {
        "agent": {
            "accountId": "test-account1234",
            "symbol": "TEST-SYMBOL",
            "headquarters": "TEST-1234-5678",
            "credits": 123456,
            "startingFaction": "COSMIC",
        },
        "token": "new-token",
    }
}
JSON_POST_FAIL = {
    "error": {
        "message": "Request could not be processed due to an invalid payload.",
        "code": 422,
        "data": {"symbol": ["Agent symbol has already been claimed."]},
    }
}


@requests_mock.Mocker()
def mock_get_agent_response_pass(m):
    """Creates a successful mock response for a normal update_agent call."""
    m.get(URL.AGENT, json=JSON_GET_PASS, status_code=200)
    return requests.get(URL.AGENT)


def test_update_agent_ok_pass():
    """Tests update_agent when status code is 'ok'."""
    j = JSON_GET_PASS["data"]
    test_agent = Agent(CLIENT)
    test_agent.update_agent(mock_get_agent_response_pass())
    assert test_agent.account_id == j["accountId"]
    assert test_agent.symbol == j["symbol"]
    assert test_agent.headquarters == j["headquarters"]
    assert test_agent.my_credits == j["credits"]
    assert test_agent.starting_faction == j["startingFaction"]
    assert test_agent.error is None


@requests_mock.Mocker()
def mock_create_agent_response_pass(m):
    """Creates a successful mock response for a create account update_agent call."""
    m.post(URL.REGISTER, json=JSON_POST_PASS, status_code=201)
    return requests.post(URL.REGISTER)


def test_update_agent_create_pass():
    """Tests update_agent when status code is 'created'."""
    j = JSON_POST_PASS["data"]["agent"]
    test_agent = Agent(CLIENT)
    test_agent.update_agent(mock_create_agent_response_pass())
    assert test_agent.account_id == j["accountId"]
    assert test_agent.symbol == j["symbol"]
    assert test_agent.headquarters == j["headquarters"]
    assert test_agent.my_credits == j["credits"]
    assert test_agent.starting_faction == j["startingFaction"]
    assert test_agent.error is None


@requests_mock.Mocker()
def mock_get_agent_response_fail(m):
    """Creates an error mock response for a normal update_agent call."""
    m.get(URL.AGENT, json=JSON_GET_FAIL, status_code=401)
    return requests.get(URL.AGENT)


def test_update_agent_fail():
    """Tests update_agent updating Agent.error with error json."""
    test_agent = Agent(CLIENT)
    test_agent.update_agent(mock_get_agent_response_fail())
    assert test_agent.error == JSON_GET_FAIL["error"]


def test_register_agent_pass():
    """Tests a successful agent registration.

    Verifies that not only is the agent data updated successfully, but the client
    access token as well."""
    with requests_mock.Mocker() as m:
        j = JSON_POST_PASS["data"]["agent"]
        m.post(URL.REGISTER, json=JSON_POST_PASS, status_code=201)
        test_agent = Agent(CLIENT)
        test_agent.register_agent(j["symbol"], j["startingFaction"])
        assert test_agent.account_id == j["accountId"]
        assert test_agent.symbol == j["symbol"]
        assert test_agent.headquarters == j["headquarters"]
        assert test_agent.my_credits == j["credits"]
        assert test_agent.starting_faction == j["startingFaction"]
        assert test_agent.error is None
        assert CLIENT.access_token == JSON_POST_PASS["data"]["token"]
        # TODO Add other response data as the register agent is updated with it.


def test_register_agent_fail():
    """Tests register_agent failing and updating Agent.error with error json."""
    with requests_mock.Mocker() as m:
        m.post(URL.REGISTER, json=JSON_POST_FAIL, status_code=422)
        test_agent = Agent(CLIENT)
        test_agent.register_agent("as", "INVALID")
        assert test_agent.error == JSON_POST_FAIL["error"]
