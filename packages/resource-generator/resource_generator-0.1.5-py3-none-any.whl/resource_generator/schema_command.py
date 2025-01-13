import typer
from resource_generator.cli_factory import __create_file

app = typer.Typer(no_args_is_help=True)

@app.command()
def name(schema_name: str):
    template = f"""from typing import Optional

from app.models.{schema_name.lower()}_model import {schema_name.capitalize()}Base, {schema_name.capitalize()}Model
from pydantic import BaseModel


class {schema_name.capitalize()}Request({schema_name.capitalize()}Base):
    pass


class {schema_name.capitalize()}Update(BaseModel):
    pass


class {schema_name.capitalize()}Response({schema_name.capitalize()}Model):
    pass
    """

    __create_file("schemas", f"{schema_name.lower()}", "_schema.py", template)
