import json

import requests

api_url = "https://api.spacetraders.io/v2/"
agent_url = f"{api_url}my/agent/"


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
