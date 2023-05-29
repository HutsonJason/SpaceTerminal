import json

import requests

api_url = "https://api.spacetraders.io/v2/"
register_url = f"{api_url}register/"
agent_url = f"{api_url}my/agent/"
factions_url = f"{api_url}factions/"
my_ships_url = f"{api_url}my/ships/"


class Account:
    """Holds the account access token and the header for API calls."""

    def __init__(self, access_token: str = None):
        self.access_token = access_token

    @property
    def header(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.access_token}",
        }

    @property
    def access_token(self):
        return self._access_token

    @access_token.setter
    def access_token(self, access_token):
        self._access_token = access_token


def get_agent(header):
    """Gets My Agent info.

    https://api.spacetraders.io/v2/my/agent

    Args:
        header: The API request header with the access token.

    Returns:
        {
          "data": {
            "accountId": "string",
            "symbol": "string",
            "headquarters": "string",
            "credits": 0,
            "startingFaction": "string"
          }
        }
    """
    return requests.get(agent_url, headers=header).json()


def register_agent(symbol: str = "", faction: str = "COSMIC"):
    """Registers a new agent.

    https://api.spacetraders.io/v2/register

    Args:
        symbol: The unique call sign associated with agent identity.
        faction: The starting faction, which determines which system you start in.

    Returns:
        json data with all the new account details.

    """
    header = {
        "Content-Type": "application/json",
    }
    payload = {"symbol": symbol, "faction": faction}

    return requests.post(register_url, json=payload, headers=header)


def get_status():
    return requests.get(api_url)


def get_factions():
    return requests.get(factions_url)


def get_factions_list() -> list:
    """Gets a list of the faction names that are recruiting."""
    factions = []
    response = get_factions().json()

    for faction in response["data"]:
        if faction["isRecruiting"]:
            factions.append(faction["symbol"])

    return factions


def get_my_ships(header):
    """Gets response of agent ships."""
    return requests.get(my_ships_url, headers=header)
