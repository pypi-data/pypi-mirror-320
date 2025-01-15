from typing import Any, Callable

from typer import Typer


def main(name: str):
    print(f"Hello {name}")


def run(function: Callable[..., Any]) -> None:
    app = Typer(add_completion=False)
    app.command(context_settings={"help_option_names": ["-h", "--help"]})(function)
    app()


if __name__ == "__main__":
    run(main)
