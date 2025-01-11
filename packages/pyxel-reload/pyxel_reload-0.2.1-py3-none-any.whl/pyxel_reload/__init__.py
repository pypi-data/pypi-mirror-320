import argparse
import importlib
import importlib.util
import os
import sys
import textwrap
import traceback
from threading import Thread
from types import ModuleType
from typing import Callable

import pyxel
from watchfiles import watch

app_module: ModuleType | None = None
error: bool = False


__all__ = ["main"]


def watch_for_changes() -> None:
    """
    Watch for changes to main module or any asset files and reload the module.

    Errors are caught and displayed in the pyxel window and console.
    """
    global app_module, error

    for changes in watch("."):
        if not app_module:
            continue

        for _, filename in changes:
            if filename == app_module.__file__ or filename.endswith(".pyxres"):
                try:
                    if hasattr(app_module, "on_unload"):
                        app_module.on_unload()
                    app_module = importlib.reload(app_module)
                    handle_successful_reload()
                except Exception as e:
                    handle_error(e)


def handle_successful_reload() -> None:
    global error
    error = False

    print("\033[H\033[J")
    print("✨ Refresh successful")

    pyxel.stop()


def handle_error(exc: BaseException) -> None:
    """
    Show error on console and in game.
    """
    global error
    error = True

    if isinstance(exc, SyntaxError):
        line_number = exc.lineno
    else:
        frame = traceback.extract_tb(exc.__traceback__)[-1]
        line_number = frame.lineno

    print("\033[H\033[J")
    print("⚠️ Error during refresh")
    print(textwrap.indent("".join(traceback.format_exception(exc)), "\t"))

    pyxel.cls(0)
    pyxel.text(10, 10, "Error", 8, None)
    pyxel.text(
        10, 20, f"{exc.__class__.__name__} at line number {line_number}", 8, None
    )


def catch_errors(func: Callable[[], None]) -> Callable[[], None]:
    """
    Catch errors when updating/drawing. Reloading the code might be
    syntactically correct, but this catches runtime errors.
    """

    def wrapper():
        global error
        if error:
            return

        try:
            func()
        except Exception as e:
            handle_error(e)

    return wrapper


@catch_errors
def update():
    if app_module:
        app_module.update()


@catch_errors
def draw():
    if app_module:
        app_module.draw()


def main():
    global app_module

    parser = argparse.ArgumentParser()
    parser.add_argument("module", help="python module", type=str)
    args = parser.parse_args()

    patch_pyxel()
    sys.path.append(os.getcwd())
    app_module = importlib.import_module(args.module)

    thread = Thread(target=watch_for_changes)
    thread.start()
    pyxel._run_original(update, draw)  # type: ignore
    thread.join()


def patch_pyxel():
    """
    Patch pyxel to avoid issues with reloading.
    """

    def wrap_init(func: Callable) -> Callable:
        """
        Protect pyxel.init from being called after the first time, it panics otherwise.

        pyxel.init also does some CWD modification based on the stack, we need to
        restore CWD because the stack information is wrong because we introduce our
        wrapper.
        """

        def wrapper(*args, **kwargs):
            if not getattr(pyxel, "initialized", False):
                cwd = os.getcwd()
                func(*args, **kwargs)
                os.chdir(cwd)
                setattr(pyxel, "initialized", True)

        return wrapper  # type: ignore

    pyxel.init = wrap_init(pyxel.init)

    def noop_run(*args, **kwargs):
        """
        We run the game loop in our own way, so we don't want pyxel to run it.
        """
        pass

    setattr(pyxel, "_run_original", pyxel.run)
    pyxel.run = noop_run
