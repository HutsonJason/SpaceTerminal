import space as s
from rich.markdown import Markdown
from textual.app import App, ComposeResult
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


class LoginScreen(ModalScreen[str]):
    def compose(self) -> ComposeResult:
        yield LoginContainer()


class LoginContainer(Container):
    def compose(self) -> ComposeResult:
        yield Static(Markdown(LOGIN_MD))
        yield Input(placeholder="Access Token", id="input-access-token")
        yield Button("Login", id="button-login", variant="success")
        yield Button("Create account", id="button-create-account", variant="primary")


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
        ("ctrl+t", "app.toggle_dark", "Toggle dark mode"),
        ("ctrl+c,ctrl+q", "app.quit", "Quit"),
        ("q", "request_quit", "Test Modal"),
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

    def action_request_quit(self) -> None:
        """Action to display the quit dialog."""

        def check_quit(quit: bool) -> None:
            """Called when QuitScreen is dismissed."""
            if quit:
                self.exit()

        self.push_screen(LoginScreen(), check_quit)


if __name__ == "__main__":
    app = SpaceApp()
    app.run()
