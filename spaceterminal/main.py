import json
import os

import space as s
from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container
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
)

account = s.Account()

LOGIN_MD = """

# Trading Space

A SpaceTrader API interface. Enter access token to start, or create new account.
"""

REGISTER_MD = """

Players are called agents, and each agent is identified by a unique call sign, such as ZER0_SH0T or SP4CE_TR4DER. All of your ships, contracts, credits, and other game assets will be associated with your agent identity.

Your starting faction will determine which system you start in, but the default faction should be fine for now.
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

    def compose(self) -> ComposeResult:
        yield Markdown(REGISTER_MD)
        yield Input(placeholder="Call Sign", id="input-symbol")
        yield Input(placeholder="Starting Faction", value="COSMIC", id="input-faction")
        yield Button(
            "Register account", id="button-register-account", variant="success"
        )


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

{account.access_token}
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
        agent = s.get_agent(account.header)
        if "error" in agent:
            agent_md = f"""
{agent['error']['message']}

Code: {agent['error']['code']}"""
            self.agent_markdown.update(agent_md)
        else:
            agent = s.get_agent(account.header)["data"]
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


class SpaceApp(App):
    CSS_PATH = "style.css"
    TITLE = "Trading Space"
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
                    yield Static("Ships")
            yield Footer()

    def on_mount(self):
        self.push_screen(self.MainScreen())
        self.push_screen(LoginScreen())

    @on(Button.Pressed, "#button-login")
    def button_login(self) -> None:
        input_widget = self.query_one("#input-access-token", Input)
        account.access_token = input_widget.value
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
        account.access_token = response.json()["data"]["token"]

        self.pop_screen()
        await self.push_screen(RegisterResultsScreen())
        self.query_one(RegisterResultsContainer).update_token_markdown()

    @on(Button.Pressed, "#button-save-access-token")
    def button_copy_access_token(self):
        save_file = os.path.abspath(
            os.path.join(os.path.dirname(__file__), "token.json")
        )
        token = {
            "token": account.access_token,
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

    def action_login(self) -> None:
        """Action to display the login modal."""

        self.push_screen(LoginScreen())


if __name__ == "__main__":
    app = SpaceApp()
    app.run()
