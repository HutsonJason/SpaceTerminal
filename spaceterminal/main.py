import space as s
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, ScrollableContainer
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

# Register new agent

Players are called agents, and each agent is identified by a unique call sign, such as ZER0_SH0T or SP4CE_TR4DER. All of your ships, contracts, credits, and other game assets will be associated with your agent identity.

Your starting faction will determine which system you start in, but the default faction should be fine for now.
"""


class MainTabContainer(Container):
    pass


class LoginScreen(ModalScreen[str]):
    BINDINGS = [("escape", "app.pop_screen", "Close Login")]

    def compose(self) -> ComposeResult:
        yield LoginContainer(id="modal-login")


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
        yield RegisterContainer(id="modal-login")


class RegisterContainer(Container):
    """Container to register new account."""

    def compose(self) -> ComposeResult:
        yield Markdown(REGISTER_MD)
        yield Input(placeholder="Call Sign", id="input-symbol")
        yield Input(placeholder="Starting Faction", value="COSMIC", id="input-faction")
        yield Button(
            "Register account", id="button-register-account", variant="success"
        )


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


class AgentContainer(MainTabContainer):
    def compose(self) -> ComposeResult:
        yield AgentBody()


class StatusContainer(MainTabContainer):
    """Holds the main container of the Status tab."""

    def compose(self) -> ComposeResult:
        yield StatusBody()


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
                    yield StatusContainer()
                with TabPane("Agent", id="agent"):
                    yield AgentContainer()
                with TabPane("Ships", id="ships"):
                    yield Static("Ships")
            yield Footer()

    def on_mount(self):
        self.push_screen(self.MainScreen())
        self.push_screen(LoginScreen())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "button-login":
            input_widget = self.query_one("#input-access-token", Input)
            account.access_token = input_widget.value
            self.pop_screen()
            self.query_one(AgentBody).update_agent_info()
        elif button_id == "button-create-account":
            self.pop_screen()
            self.push_screen(RegisterScreen())

    def action_login(self) -> None:
        """Action to display the login modal."""

        self.push_screen(LoginScreen())


if __name__ == "__main__":
    app = SpaceApp()
    app.run()
