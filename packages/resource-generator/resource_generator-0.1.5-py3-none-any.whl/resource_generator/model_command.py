import os.path
from typing import Annotated

import typer
from resource_generator.cli_factory import __create_file
from resource_generator.schema_command import name as create_schema
from resource_generator.controller_command import name as create_controller
from resource_generator.service_command import name as create_service
from resource_generator.repository_command import name as create_repository

app = typer.Typer(no_args_is_help=True)

@app.command()
def name(
        model_name: Annotated[str, typer.Argument(help="Model name")],
        schema: Annotated[bool, typer.Option()] = False,
        controller: Annotated[bool, typer.Option()] = False,
        service: Annotated[bool, typer.Option()] = False,
        repository: Annotated[bool, typer.Option()] = False,
):
    """Command to generate a file model."""
    template = f"""from app.models.base_model import IDModel, TimestampModel
from pydantic import BaseModel


class {model_name.capitalize()}Base(BaseModel):
    pass
    # Add your field for table here

class {model_name.capitalize()}Model({model_name.capitalize()}Base, IDModel, TimestampModel, table=True):
    __table__ = '{model_name.lower()}s'
    """

    __create_file("models", f"{model_name.lower()}", "_model.py", template)

    if schema:
        create_schema(model_name)

    if controller:
        create_controller(model_name)

    if service:
        create_service(model_name)

    if repository:
        create_repository(model_name)

    if not os.path.exists("app/models/base_model.py"):
        base_model()

def base_model():
    """Create base model"""
    template = """from datetime import datetime, timezone
import uuid
from typing import Optional

from sqlmodel import SQLModel, Field


class IDModel(SQLModel):
    id: uuid.UUID = Field(
        default_factory=uuid.uuid4,
        primary_key=True,
        index=True,
        nullable=False,
    )


class TimestampModel(SQLModel):
    created_by: Optional[uuid.UUID] = Field(
        nullable=True
    )
    updated_by: Optional[uuid.UUID] = Field(
        nullable=True
    )
    created_at: datetime = Field(
        default_factory=datetime.now,
    )
    updated_at: Optional[datetime] = Field(
        sa_column_kwargs={"onupdate": datetime.now(timezone.utc)},
    )
"""

    __create_file("models", "base", "_model.py", template)
