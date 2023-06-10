import datetime

import requests

from spaceterminal.client import Client
from spaceterminal.constants import URL


class Agent:
    """Holds my agent information."""

    def __init__(self, client: Client):
        self.client = client
        self.account_id: str = "Not loaded yet"
        self.symbol: str = "Not loaded yet"
        self.headquarters: str = "Not loaded yet"
        self.my_credits: int = 0
        self.starting_faction: str = "Not loaded yet"
        self.last_updated: datetime.datetime = datetime.datetime.now()
        self.error = None

    def get_agent_response(self) -> requests.Response:
        """Gets my agent status.

        https://api.spacetraders.io/v2/my/agent
        """
        return self.client.session.get(URL.AGENT)

    def update_agent(self, response: requests.Response = None) -> None:
        """Updates my agent information.

        Updates all of the my agent information pulled from the response. The response
        can come directly from the my agent endpoint, or from the register agent endpoint.
        The response from the register agent endpoint also contains other data like
        contract, faction, ship, and token.

        Args:
            response: The requests response supplied either from registering response,
            or directly from the my agent endpoint.
        """
        if response is None:
            response = self.get_agent_response()
        # TODO Error checking

        if (
            response.status_code == requests.codes.ok
            or response.status_code == requests.codes.created
        ):
            # This accounts for the response when creating account having different json.
            if "agent" in response.json()["data"]:
                agent = response.json()["data"]["agent"]
            else:
                agent = response.json()["data"]

            self.account_id = agent["accountId"]
            self.symbol = agent["symbol"]
            self.headquarters = agent["headquarters"]
            self.my_credits = agent["credits"]
            self.starting_faction = agent["startingFaction"]
            self.last_updated = datetime.datetime.now()
            self.error = None
        elif "error" in response.json():
            self.error = response.json()["error"]

    def register_agent(self, symbol: str = "", faction: str = "COSMIC") -> None:
        """Registers a new agent.

        https://api.spacetraders.io/v2/register

        Args:
            symbol: The unique call sign associated with agent identity.
            faction: The starting faction, which determines which system you start in.
        """
        payload = {"symbol": symbol, "faction": faction.upper()}
        response = self.client.session.post(URL.REGISTER, json=payload)

        if response.status_code == requests.codes.created:
            self.client.access_token = response.json()["data"]["token"]
            self.update_agent(response)
            # TODO The response from register contains contract, faction, and ship data too.
            # That should be updated here as well.
        elif "error" in response.json():
            self.error = response.json()["error"]
