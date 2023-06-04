import datetime

import requests
from client import Client
from constants import URL


class Agent:
    """Holds my agent information."""

    def __init__(self, client: Client):
        self.client = client
        self.account_id: str = None
        self.symbol: str = None
        self.headquarters: str = None
        self.my_credits: int = None
        self.starting_faction: str = None
        self.last_updated: datetime.datetime = None
        self.error = None

    def get_agent_response(self) -> requests.Response:
        return self.client.session.get(URL.AGENT)

    def update_agent(self, response: requests.Response = None) -> None:
        """Update my agent information."""
        if response is None:
            response = self.get_agent_response()
        # TODO Error checking

        if response.status_code == requests.codes.ok:
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

    def register_agent(
        self, symbol: str = "", faction: str = "COSMIC"
    ) -> requests.Response:
        """Registers a new agent.

        https://api.spacetraders.io/v2/register

        Args:
            symbol: The unique call sign associated with agent identity.
            faction: The starting faction, which determines which system you start in.

        Returns:
            Response data with all the new account details.

        """
        payload = {"symbol": symbol, "faction": faction.upper()}
        response = self.client.session.post(URL.REGISTER, json=payload)

        if response.status_code == requests.codes.ok:
            self.client.access_token = response.json()["data"]["token"]
            self.update_agent(response)
            # TODO The response from register contains contract, faction, and ship data too.
            # That should be updated here as well.

        # Not sure if I have need to return a response here.
        return response