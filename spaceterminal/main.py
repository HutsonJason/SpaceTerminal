import json
import os

import contracts as con
import jsonTree as jt
import space as s
from client import Client
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Horizontal
from textual.screen import ModalScreen, Screen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    Markdown,
    Placeholder,
    Static,
    TabbedContent,
    TabPane,
    Tree,
)

client = Client()

LOGIN_MD = """

# SpaceTerminal

A SpaceTrader API interface. Enter access token to start, or create new account.
"""

REGISTER_MD = f"""

Players are called agents, and each agent is identified by a unique call sign, such as ZER0_SH0T or SP4CE_TR4DER. All of your ships, contracts, credits, and other game assets will be associated with your agent identity.

Your starting faction will determine which system you start in, but the default faction should be fine for now.

Available recruiting factions: {s.get_factions_list()}
"""


class LoginScreen(ModalScreen[str]):
    BINDINGS = [("escape", "app.pop_screen", "Close Login")]

    def compose(self) -> ComposeResult:
        modal = LoginContainer(id="modal-login")
        modal.border_title = "Login"
        yield modal


class LoginContainer(Container):
    """Container to login with access token, or create new account."""

    def compose(self) -> ComposeResult:
        yield Markdown(LOGIN_MD)
        yield Input(placeholder="Access Token", id="input-access-token")
        yield Button("Login", id="button-login", variant="success")
        yield Button("Create account", id="button-create-account", variant="primary")


class RegisterScreen(ModalScreen[str]):
    BINDINGS = [("escape", "app.pop_screen", "Close Register")]

    def compose(self) -> ComposeResult:
        modal = RegisterContainer(id="modal-login")
        modal.border_title = "Register new agent"
        yield modal


class RegisterContainer(Container):
    """Container to register new account."""

    register_markdown = Markdown()

    def on_mount(self):
        self.register_markdown.update(REGISTER_MD)

    def compose(self) -> ComposeResult:
        yield self.register_markdown
        yield Input(placeholder="Call Sign", id="input-symbol")
        yield Input(placeholder="Starting Faction", value="COSMIC", id="input-faction")
        yield Button(
            "Register account", id="button-register-account", variant="success"
        )

    def update_register_markdown(self, response):
        """Update the markdown to give the error code and message."""
        reason_key = [key for key in response.json()["error"]["data"]][0]
        register_md = f"""
Code: {response.json()["error"]["code"]}

{response.json()["error"]["message"]}

Reason: {response.json()["error"]["data"][reason_key][0]}
"""
        self.register_markdown.update(register_md)


class RegisterResultsScreen(ModalScreen):
    BINDINGS = [("escape", "app.pop_screen", "Close Popup")]

    def compose(self) -> ComposeResult:
        modal = RegisterResultsContainer(id="modal-login")
        modal.border_title = "Register Successful!"
        yield modal


class RegisterResultsContainer(Container):
    """Container with results from new account register."""

    token_markdown = Markdown()
    save_location_markdown = Markdown()

    def on_mount(self) -> None:
        self.update_token_markdown()

    def update_token_markdown(self) -> None:
        token_md = f"""
Access token is:

{client.access_token}
"""
        self.token_markdown.update(token_md)

    def update_save_location_markdown(self, save_location) -> None:
        location_md = f"""
Save location of access token is:

{save_location}
"""
        self.save_location_markdown.update(location_md)

    def compose(self) -> ComposeResult:
        yield self.token_markdown
        yield self.save_location_markdown
        yield Button(
            "Save access token to file",
            id="button-save-access-token",
            variant="primary",
        )
        yield Button("Close", id="button-close-register-success", variant="error")


class AgentBody(Static):
    agent_markdown = Markdown()

    def on_mount(self) -> None:
        self.update_agent_info()

    def compose(self) -> ComposeResult:
        yield self.agent_markdown

    def update_agent_info(self) -> None:
        agent = s.get_agent(client)
        if "error" in agent:
            agent_md = f"""
{agent["error"]["message"]}

Code: {agent["error"]["code"]}"""
            self.agent_markdown.update(agent_md)
        else:
            agent = agent["data"]
            agent_md = f"""
Account ID: {agent["accountId"]}

Symbol: {agent["symbol"]}

Headquarters: {agent["headquarters"]}

Credits: {agent["credits"]}

Starting Faction: {agent["startingFaction"]}"""
            self.agent_markdown.update(agent_md)


class StatusBody(Static):
    """Body content of the status tab."""

    status_markdown = Markdown()

    def on_mount(self):
        self.update_status()

    def compose(self) -> ComposeResult:
        yield self.status_markdown

    def update_status(self):
        response = s.get_status()
        response_code = response.status_code
        status = s.get_status().json()

        if response_code == 200:
            self.status_markdown.add_class("online")
            status_md = f"""
# Status: {status["status"]}

Version: {status["version"]}

Description: {status["description"]}

#### Stats

Agents: {status["stats"]["agents"]}

Ships: {status["stats"]["ships"]}

Systems: {status["stats"]["systems"]}

Waypoints: {status["stats"]["waypoints"]}

#### Server Resets

Reset Date: {status["resetDate"]}

Next: {status["serverResets"]["next"]}

Frequency: {status["serverResets"]["frequency"]}
"""
            self.status_markdown.update(status_md)

        else:
            self.status_markdown.add_class("offline")
            status_md = f"""
# {status["error"]["message"]}

{status["error"]["code"]}
"""
            self.status_markdown.update(status_md)


class ShipsBody(Static):
    BINDINGS = [
        ("e", "expand_all_tree", "Expand all"),
        ("c", "collapse_all_tree", "Collapse all"),
    ]

    ships_markdown = Markdown()

    def action_expand_all_tree(self):
        node = self.query_one(Tree).get_node_at_line(0)
        node.expand_all()

    def action_collapse_all_tree(self):
        node = self.query_one(Tree).get_node_at_line(0)
        node.collapse_all()

    def compose(self) -> ComposeResult:
        yield self.ships_markdown
        yield Tree("Root", id="tree-ships")

    def update_my_ships_info(self):
        ships = s.get_my_ships(client).json()

        if "error" in ships:
            ships_md = f"""
Code: {ships["error"]["code"]}

{ships["error"]["message"]}
"""
            self.ships_markdown.update(ships_md)

        else:
            tree = self.query_one("#tree-ships")
            tree.show_root = False
            tree.reset("#tree-ships")
            json_node = tree.root.add("Ships")
            ships = ships["data"]
            jt.add_json(json_node, ships)
            tree.root.expand()

            ships_md = f"""# Available Ships"""
            self.ships_markdown.update(ships_md)


class ContractsBody(Static):
    BINDINGS = [
        ("e", "expand_all_tree", "Expand all"),
        ("c", "collapse_all_tree", "Collapse all"),
    ]

    contracts_markdown = Markdown()
    is_contract_selected = False
    contract_selected_id = None
    contract_selected_markdown = Markdown(
        "Select a contract to accept.", id="markdown-contracts-selected"
    )

    def action_expand_all_tree(self):
        node = self.query_one(Tree).get_node_at_line(0)
        node.expand_all()

    def action_collapse_all_tree(self):
        node = self.query_one(Tree).get_node_at_line(0)
        node.collapse_all()

    @on(Tree.NodeSelected)
    def get_node_selected(self, event: Tree.NodeSelected) -> None:
        """Gets the contract id of selected node in the contracts tree."""
        node_label = str(event.node.label)
        if "id" in node_label:
            self.contract_selected_id = node_label.removeprefix("id='").removesuffix(
                "'"
            )
            md = f"""Contract selected: {self.contract_selected_id}"""
            self.contract_selected_markdown.update(md)

    def compose(self) -> ComposeResult:
        yield self.contracts_markdown
        with Horizontal(id="horizontal-contracts"):
            yield self.contract_selected_markdown
            yield Button(
                "Accept Contract", id="button-accept-contract", variant="success"
            )
        yield Tree("Root", id="tree-contracts")

    def update_my_contracts_info(self):
        contracts = s.get_my_contracts(client).json()

        if "error" in contracts:
            contracts_md = f"""
Code: {contracts["error"]["code"]}

{contracts["error"]["message"]}
"""
            self.contracts_markdown.update(contracts_md)

        else:
            tree = self.query_one("#tree-contracts")
            tree.show_root = False
            tree.reset("#tree-contracts")
            json_node = tree.root.add("Contracts")
            contracts = contracts["data"]
            con.create_contract_tree(json_node, contracts)
            tree.root.expand()

            contracts_md = f"""# Available Contracts"""
            self.contracts_markdown.update(contracts_md)


class SpaceApp(App):
    CSS_PATH = "style.css"
    TITLE = "SpaceTerminal"
    BINDINGS = [Binding("ctrl+c", "app.quit", "Quit", priority=True, show=False)]

    class MainScreen(Screen):
        BINDINGS = [
            ("escape", "app.quit", "Quit"),
            ("ctrl+t", "app.toggle_dark", "Toggle dark mode"),
            ("l", "login", "Login"),
        ]

        def compose(self) -> ComposeResult:
            yield Header(show_clock=True)
            with TabbedContent(initial="status"):
                with TabPane("Status", id="status"):
                    yield StatusBody()
                with TabPane("Agent", id="agent"):
                    yield AgentBody()
                with TabPane("Ships", id="ships"):
                    yield ShipsBody()
                with TabPane("Contracts", id="tab-contracts"):
                    yield ContractsBody()
            yield Footer()

    def on_mount(self):
        self.push_screen(self.MainScreen())
        self.push_screen(LoginScreen())

    def action_login(self) -> None:
        """Action to display the login modal."""
        self.push_screen(LoginScreen())

    @on(Button.Pressed, "#button-login")
    def button_login(self) -> None:
        input_widget = self.query_one("#input-access-token", Input)
        client.access_token = input_widget.value
        self.pop_screen()
        self.query_one(AgentBody).update_agent_info()

    @on(Button.Pressed, "#button-create-account")
    def button_create_account(self) -> None:
        self.pop_screen()
        self.push_screen(RegisterScreen())

    @on(Button.Pressed, "#button-register-account")
    async def button_register_account(self):
        input_symbol = self.query_one("#input-symbol", Input).value
        input_faction = self.query_one("#input-faction", Input).value
        response = s.register_agent(input_symbol, input_faction)

        if "error" in response.json():
            self.query_one(RegisterContainer).update_register_markdown(response)
        else:
            client.access_token = response.json()["data"]["token"]
            self.pop_screen()
            await self.push_screen(RegisterResultsScreen())
            self.query_one(RegisterResultsContainer).update_token_markdown()

    @on(Button.Pressed, "#button-save-access-token")
    def button_save_access_token(self):
        save_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "token.json")
        )
        token = {
            "token": client.access_token,
        }
        with open(save_file, "w") as file:
            json.dump(token, file)
        self.query_one(RegisterResultsContainer).update_save_location_markdown(
            save_file
        )

    @on(Button.Pressed, "#button-close-register-success")
    def button_close_register_success(self):
        self.pop_screen()
        self.query_one(AgentBody).update_agent_info()

    @on(TabbedContent.TabActivated, tab="#ships")
    def tab_ships_activated(self):
        self.query_one(ShipsBody).update_my_ships_info()
        # This will focus on the tree immediately, so the bindings show in the footer.
        self.set_focus(self.query_one("#tree-ships"))

    @on(TabbedContent.TabActivated, tab="#tab-contracts")
    def tab_contracts_activated(self):
        self.query_one(ContractsBody).update_my_contracts_info()
        # This will focus on the tree immediately, so the bindings show in the footer.
        self.set_focus(self.query_one("#tree-contracts"))


if __name__ == "__main__":
    app = SpaceApp()
    app.run()
