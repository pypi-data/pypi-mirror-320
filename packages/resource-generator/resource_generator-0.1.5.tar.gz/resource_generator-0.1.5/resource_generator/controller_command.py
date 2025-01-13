import typer
from resource_generator.cli_factory import __create_file

app = typer.Typer(no_args_is_help=True)


@app.command()
def name(controller_name: str):
    """Create a new controller file."""
    template = f"""import uuid

from typing import Annotated
from fastapi import APIRouter, Depends

router = APIRouter()
    """

    __create_file("controllers", f"{controller_name.lower()}", "_controller.py", template)
