import os
import subprocess
from pathlib import Path

from rich.console import Console
from rich.text import Text
from dotenv import load_dotenv


load_dotenv()

APP_DIR = os.getenv("APP_DIR") or "app"

BASE_DIR = Path(os.getenv("PROJECT_ROOT", Path(__file__).resolve().parent.parent)) / APP_DIR
console = Console()

console.print(f"Current working directory: {os.getcwd()}")
console.print(f"BASE_DIR: {BASE_DIR}")

def __create_file(
        directory: str,
        name: str,
        suffix: str,
        template: str
) -> bool:
    """
       Create a file based on the given parameters.

       Args:
           directory (str): Subdirectory to place the file (e.g., "models", "controllers").
           name (str): The base name of the file (e.g., "user").
           suffix (str): File extension (e.g., ".py").
           template (str): Content of the file.
       """
    try:
        dir_path = BASE_DIR / directory
        dir_path.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists
        file_path = dir_path / f"{name.lower()}{suffix}"

        if file_path.exists():
            raise FileExistsError(f"{directory.capitalize()} {file_path.name} already exists!")

        file_path.write_text(template)
        __format(file_path=file_path)
        success_message = Text(f"🎉 A {directory.capitalize()} {name.capitalize()} created successfully!", style="bold green")
        console.print(success_message)
        return True

    except FileExistsError as e:
        error_message = Text(f"😵‍💫 {e}", style="bold yellow")
        console.print(error_message)
        return False

    except Exception as e:
        error_message = Text(f"😭😭 Failed to create {directory.capitalize()}: {e}", style="bold red")
        console.print(error_message)
        return False


def __format(file_path: Path):
    # Format the file using Black
    try:
        subprocess.run(["black", str(file_path)], check=True)
        subprocess.run(["isort", "--profile", "black", str(file_path)], check=True)
    except FileNotFoundError:
        console.print("Black formatter is not installed or accessible. Please install it with 'pip install black'.")
    except subprocess.CalledProcessError as e:
        console.print(f"Error occurred while formatting: {e}")
