"""
Headless UI tests for remote_shell.py using Textual Pilot.
Run with: /tmp/rs-dev-env/bin/python test_remote_shell.py
"""
import asyncio
import os
import sys

os.environ["REMOTE_SHELL_PASSWORD"] = "testpass"
os.environ["MAGIC_COMMAND"] = "echo MAGIC_OK"

import remote_shell as rs
from remote_shell import RemoteShellApp, PasswordScreen, StatusScreen

PASS = "\033[32mPASS\033[0m"
FAIL = "\033[31mFAIL\033[0m"

results = []


def check(name: str, condition: bool) -> None:
    tag = PASS if condition else FAIL
    print(f"  [{tag}] {name}")
    results.append((name, condition))


async def type_text(pilot, text: str) -> None:
    for ch in text:
        await pilot.press(ch)


def screen_text(app, selector: str) -> str:
    """Get text content of first matching widget in current screen."""
    try:
        return str(app.screen.query_one(selector).content)
    except Exception:
        return ""


async def test_password_screen_renders() -> None:
    print("test_password_screen_renders")
    rs.PASSWORD = "testpass"
    app = RemoteShellApp()
    async with app.run_test(headless=True, size=(120, 40)) as pilot:
        await pilot.pause(0.2)
        check("PasswordScreen is active", isinstance(app.screen, PasswordScreen))
        check("logo present", len(app.screen.query("#logo")) > 0)
        check("password input present", len(app.screen.query("#password")) > 0)
        check("hint label present", len(app.screen.query("#hint")) > 0)


async def test_wrong_password_shows_denied() -> None:
    print("test_wrong_password_shows_denied")
    rs.PASSWORD = "testpass"
    app = RemoteShellApp()
    async with app.run_test(headless=True, size=(120, 40)) as pilot:
        await pilot.pause(0.2)
        await type_text(pilot, "wrongpassword")
        await pilot.press("enter")
        await pilot.pause(0.3)
        check("StatusScreen shown", isinstance(app.screen, StatusScreen))
        title = screen_text(app, ".message-title")
        check("ACCESS DENIED shown", "ACCESS DENIED" in title)


async def test_correct_password_shows_granted() -> None:
    print("test_correct_password_shows_granted")
    rs.PASSWORD = "testpass"
    app = RemoteShellApp()
    async with app.run_test(headless=True, size=(120, 40)) as pilot:
        await pilot.pause(0.2)
        await type_text(pilot, "testpass")
        await pilot.press("enter")
        await pilot.pause(0.3)
        check("StatusScreen shown", isinstance(app.screen, StatusScreen))
        title = screen_text(app, ".message-title")
        check("ACCESS GRANTED shown", "ACCESS GRANTED" in title)


async def test_missing_env_shows_config_error() -> None:
    print("test_missing_env_shows_config_error")
    rs.PASSWORD = None
    app = RemoteShellApp()
    async with app.run_test(headless=True, size=(120, 40)) as pilot:
        await pilot.pause(0.2)
        await pilot.press("enter")
        await pilot.pause(0.3)
        check("StatusScreen shown", isinstance(app.screen, StatusScreen))
        title = screen_text(app, ".message-title")
        check("CONFIGURATION ERROR shown", "CONFIGURATION ERROR" in title)
    rs.PASSWORD = "testpass"


async def test_escape_quits_without_crash() -> None:
    print("test_escape_quits_without_crash")
    rs.PASSWORD = "testpass"
    app = RemoteShellApp()
    raised = False
    try:
        async with app.run_test(headless=True, size=(120, 40)) as pilot:
            await pilot.pause(0.2)
            await pilot.press("escape")
            await pilot.pause(0.1)
    except Exception:
        raised = True
    check("no exception on escape", not raised)


async def main() -> None:
    tests = [
        test_password_screen_renders,
        test_wrong_password_shows_denied,
        test_correct_password_shows_granted,
        test_missing_env_shows_config_error,
        test_escape_quits_without_crash,
    ]

    for t in tests:
        try:
            await t()
        except Exception as e:
            print(f"  [{FAIL}] EXCEPTION in {t.__name__}: {e}")
            results.append((t.__name__, False))
        print()

    passed = sum(1 for _, ok in results if ok)
    total = len(results)
    color = "\033[32m" if passed == total else "\033[31m"
    print(f"{color}{passed}/{total} checks passed\033[0m")
    sys.exit(0 if passed == total else 1)


if __name__ == "__main__":
    asyncio.run(main())
