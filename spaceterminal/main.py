import space as s
from rich.markdown import Markdown
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Container, Grid, ScrollableContainer
from textual.screen import ModalScreen
from textual.widgets import (
    Button,
    Footer,
    Header,
    Input,
    Label,
    Placeholder,
    Static,
    TabbedContent,
    TabPane,
)

account = s.Account()

LOGIN_MD = """

## Trading Space

A SpaceTrader API interface. Enter access token to start, or create new account.
"""

REGISTER_MD = """

## Register new agent

Players are called agents, and each agent is identified by a unique call sign, such as ZER0_SH0T or SP4CE_TR4DER. All of your ships, contracts, credits, and other game assets will be associated with your agent identity.

Your starting faction will determine which system you start in, but the default faction should be fine for now.
"""


class LoginScreen(ModalScreen[str]):
    BINDINGS = [("escape", "app.pop_screen", "Close Login")]

    def compose(self) -> ComposeResult:
        yield LoginContainer(id="modal-login")


class LoginContainer(Container):
    """Container to login with access token, or create new account."""

    def compose(self) -> ComposeResult:
        yield Static(Markdown(LOGIN_MD))
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
        yield Static(Markdown(REGISTER_MD))
        yield Input(placeholder="Call Sign", id="input-symbol")
        yield Input(placeholder="Starting Faction", value="COSMIC", id="input-faction")
        yield Button(
            "Register account", id="button-register-account", variant="success"
        )


class AgentInfo(Static):
    def on_mount(self) -> None:
        self.update_agent_info()

    def update_agent_info(self) -> None:
        agent = s.get_agent(account.header)
        if "error" in agent:
            self.update(f"{agent['error']['message']}\nCode: {agent['error']['code']}")
        else:
            agent = s.get_agent(account.header)["data"]
            agent_md = f"""
            Account ID: {agent["accountId"]}
            Symbol: {agent["symbol"]}
            Headquarters: {agent["headquarters"]}
            Credits: {agent["credits"]}
            Starting Faction: {agent["startingFaction"]}"""
            self.update(Markdown(agent_md))


class AgentContainer(Container):
    def compose(self) -> ComposeResult:
        yield AgentInfo()


class SpaceApp(App):
    CSS_PATH = "style.css"
    TITLE = "Trading Space"
    BINDINGS = [
        Binding("ctrl+c", "app.quit", "Quit", priority=True),
        Binding("ctrl+t", "app.toggle_dark", "Toggle dark mode"),
        Binding("l", "login", "Login"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent(initial="agent"):
            with TabPane("Login", id="login"):
                # yield LoginContainer()
                yield Static("Old Login")
            with TabPane("Agent", id="agent"):
                yield AgentContainer()
            with TabPane("Ships", id="ships"):
                yield Static("Ships")
        yield Footer()

    def on_mount(self):
        self.push_screen(LoginScreen())

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button_id = event.button.id
        if button_id == "button-login":
            input_widget = self.query_one("#input-access-token", Input)
            account.access_token = input_widget.value
            self.pop_screen()
            self.query_one(AgentInfo).update_agent_info()
        elif button_id == "button-create-account":
            self.pop_screen()
            self.push_screen(RegisterScreen())

    def action_login(self) -> None:
        """Action to display the login modal."""

        self.push_screen(LoginScreen())


if __name__ == "__main__":
    app = SpaceApp()
    app.run()
