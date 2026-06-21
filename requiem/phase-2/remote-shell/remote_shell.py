#!/usr/bin/env python3

import asyncio
import hmac
import os
import signal
import sys
from textual.app import App, ComposeResult
from textual.binding import Binding
from textual.containers import Center, Vertical
from textual.screen import Screen
from textual.widgets import Footer, Header, Input, Label, Static

PASSWORD = os.environ.get("REMOTE_SHELL_PASSWORD")
MAGIC_COMMAND = os.environ.get("MAGIC_COMMAND")

ASCII_ART = r"""
██████╗ ███████╗ ██████╗ ██╗   ██╗██╗███████╗███╗   ███╗
██╔══██╗██╔════╝██╔═══██╗██║   ██║██║██╔════╝████╗ ████║
██████╔╝█████╗  ██║   ██║██║   ██║██║█████╗  ██╔████╔██║
██╔══██╗██╔══╝  ██║▄▄ ██║██║   ██║██║██╔══╝  ██║╚██╔╝██║
██║  ██║███████╗╚██████╔╝╚██████╔╝██║███████╗██║ ╚═╝ ██║
╚═╝  ╚═╝╚══════╝ ╚══▀▀═╝  ╚═════╝ ╚═╝╚══════╝╚═╝     ╚═╝
"""


class AppState:
    authenticated = False


def clear_terminal() -> None:
    sys.stdout.write("[2J[H")
    sys.stdout.flush()


def validate_configuration() -> bool:
    return bool(PASSWORD and MAGIC_COMMAND)


def authenticate(password: str) -> bool:
    return bool(PASSWORD) and hmac.compare_digest(password, PASSWORD)


class PasswordScreen(Screen):
    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
        Binding("escape", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Center():
            with Vertical(id="login-box"):
                yield Static(ASCII_ART, id="logo")
                yield Label("SECURE REMOTE ACCESS NODE", id="title")
                yield Label("AUTHORIZED PERSONNEL ONLY", id="subtitle")
                yield Input(
                    password=True,
                    placeholder="Enter access key...",
                    id="password",
                    max_length=128,
                )
                yield Label(
                    "Press ENTER to authenticate",
                    id="hint",
                )

        yield Footer()

    async def on_mount(self) -> None:
        self.query_one(Input).focus()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        password = event.value
        event.input.value = ""

        if not validate_configuration():
            await self.app.push_screen(
                StatusScreen(
                    title="CONFIGURATION ERROR",
                    subtitle="SYSTEM MISCONFIGURATION DETECTED",
                    success=False,
                )
            )
            return

        if authenticate(password):
            await self.app.push_screen(
                StatusScreen(
                    title="ACCESS GRANTED",
                    subtitle="INITIALIZING REMOTE SESSION",
                    success=True,
                )
            )
        else:
            await self.app.push_screen(
                StatusScreen(
                    title="ACCESS DENIED",
                    subtitle="INVALID AUTHORIZATION KEY",
                    success=False,
                )
            )


class StatusScreen(Screen):
    def __init__(self, title: str, subtitle: str, success: bool):
        super().__init__()
        self.title = title
        self.subtitle = subtitle
        self.success = success

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Center():
            with Vertical(id="message-box"):
                yield Static(ASCII_ART, id="logo")
                yield Label("SECURE REMOTE ACCESS NODE", id="title")
                yield Label("AUTHORIZED PERSONNEL ONLY", id="subtitle")
                yield Static(self.title, classes="message-title")
                yield Static(self.subtitle, classes="message-subtitle")
                yield Static("■ □ □ □ □", id="loader")

        yield Footer()

    async def on_mount(self) -> None:
        loader = self.query_one("#loader", Static)

        frames = [
            "■ □ □ □ □",
            "■ ■ □ □ □",
            "■ ■ ■ □ □",
            "■ ■ ■ ■ □",
            "■ ■ ■ ■ ■",
        ]

        for _ in range(2):
            for frame in frames:
                loader.update(frame)
                await asyncio.sleep(0.12)

        await asyncio.sleep(0.4)

        if self.success:
            self.app.exit(result="launch")
        else:
            self.app.exit(result="deny")


class GoodbyeScreen(Screen):
    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)

        with Center():
            with Vertical(id="message-box"):
                yield Static(ASCII_ART, id="logo")
                yield Label("SECURE REMOTE ACCESS NODE", id="title")
                yield Label("SESSION CLOSED", id="subtitle")
                yield Static(
                    "REMOTE SESSION TERMINATED",
                    classes="message-title",
                )
                yield Static(
                    "THANK YOU FOR USING REMOTE SHELL",
                    classes="message-subtitle",
                )
                yield Static("GOODBYE.", id="loader")

        yield Footer()

    async def on_mount(self) -> None:
        await asyncio.sleep(2.5)
        self.app.exit()


class RemoteShellApp(App):
    enable_command_palette = False
    TITLE = "Remote Shell"
    SUB_TITLE = "Secure Access Gateway"

    CSS = """
    Screen {
        background: #081008;
        color: #8cff8c;
    }

    Header {
        background: #111611;
        color: #9dff9d;
    }

    Footer {
        background: #111611;
        color: #9dff9d;
    }

    #login-box, #message-box {
        width: 90%;
        max-width: 100;
        min-width: 40;
        border: tall #466446;
        background: #111611;
        padding: 2 4;
    }

    #logo {
        color: #7dff7d;
        text-style: bold;
        margin-bottom: 1;
        content-align: center middle;
    }

    #title {
        color: #d6ff72;
        text-style: bold;
        content-align: center middle;
        margin-bottom: 1;
    }

    #subtitle {
        color: #d0a85c;
        content-align: center middle;
        margin-bottom: 2;
    }

    #hint {
        color: #6c9f6c;
        margin-top: 1;
        content-align: center middle;
    }

    Input {
        border: round #4d7a4d;
        background: #081008;
        color: #9dff9d;
    }

    Input:focus {
        border: round #d6ff72;
    }

    .message-title {
        color: #d6ff72;
        text-style: bold;
        content-align: center middle;
        margin-bottom: 1;
    }

    .message-subtitle {
        color: #c59c55;
        content-align: center middle;
        margin-bottom: 2;
    }

    #loader {
        color: #7dff7d;
        content-align: center middle;
        text-style: bold;
    }
    """

    BINDINGS = [
        Binding("ctrl+c", "quit", "Quit"),
    ]

    def on_mount(self) -> None:
        self.push_screen(PasswordScreen())


async def show_goodbye() -> None:
    app = RemoteShellApp()
    app.push_screen(GoodbyeScreen())
    await app.run_async()


async def launch_magic_command() -> int:
    clear_terminal()
    proc = await asyncio.create_subprocess_shell(MAGIC_COMMAND)
    return await proc.wait()


async def run_interface() -> str | None:
    app = RemoteShellApp()
    return await app.run_async()


async def main() -> None:
    result = await run_interface()

    if result == "launch":
        exit_code = await launch_magic_command()
        await show_goodbye()
        raise SystemExit(exit_code)

    await show_goodbye()


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        clear_terminal()
