import requests

api_url = "https://api.spacetraders.io/v2/"
factions_url = f"{api_url}factions/"
my_ships_url = f"{api_url}my/ships/"
my_contracts_url = f"{api_url}my/contracts/"


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
