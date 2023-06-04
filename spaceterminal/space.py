import requests

api_url = "https://api.spacetraders.io/v2/"
register_url = f"{api_url}register/"
agent_url = f"{api_url}my/agent/"
factions_url = f"{api_url}factions/"
my_ships_url = f"{api_url}my/ships/"
my_contracts_url = f"{api_url}my/contracts/"


# def get_agent(client):
#     """Gets My Agent info.
#
#     https://api.spacetraders.io/v2/my/agent
#
#     Args:
#         client: The Client object with session.
#
#     Returns:
#         {
#           "data": {
#             "accountId": "string",
#             "symbol": "string",
#             "headquarters": "string",
#             "credits": 0,
#             "startingFaction": "string"
#           }
#         }
#     """
#     return client.session.get(agent_url).json()


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


def get_my_ships(client):
    """Gets response of agent ships."""
    return client.session.get(my_ships_url)


def get_my_contracts(client):
    """Gets response of my contracts."""
    return client.session.get(my_contracts_url)
