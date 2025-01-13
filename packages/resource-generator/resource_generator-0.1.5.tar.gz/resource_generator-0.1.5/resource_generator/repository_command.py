import os
from pathlib import Path

import typer
from rich.console import Console
from resource_generator.cli_factory import __create_file, BASE_DIR, __format


app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command()
def name(repo_name: str):
    """Create a new repository file."""
    template = f"""from typing import Annotated

from app.core.database.context import get_db
from app.models.{repo_name.lower()}_model import {repo_name.capitalize()}Model
from app.schemas.{repo_name.lower()}_schema import {repo_name.capitalize()}Request, {repo_name.capitalize()}Update
from app.repository.base_repo import BaseRepo
from fastapi import Depends
from sqlmodel import Session

class {repo_name.capitalize()}Repository(BaseRepo[{repo_name.capitalize()}Model, {repo_name.capitalize()}Request, {repo_name.capitalize()}Update]):
    def __init__(self, db: Annotated[Session, Depends(get_db)]):
        super().__init__({repo_name.capitalize()}Model, db)
    """

    created = __create_file("repository", f"{repo_name.lower()}", "_repository.py", template)

    if created:
        content_top = f"""from fastapi import Depends
from typing import Annotated
        """

        content_bottom = f"""
from app.repository.{repo_name.lower()}_repository import {repo_name.capitalize()}Repository

{repo_name.capitalize()}RepositoryDep = Annotated[{repo_name.capitalize()}Repository, Depends({repo_name.capitalize()}Repository)]
        """

        repository_initializer = Path(f"{BASE_DIR}/repository/__init__.py")
        if repository_initializer.exists():
            with repository_initializer.open('a') as file:
                file.write(content_bottom)

            __format(file_path=repository_initializer)
        else:
            with repository_initializer.open('w') as file:
                file.write(content_top)
                file.write(content_bottom)

            __format(file_path=repository_initializer)
