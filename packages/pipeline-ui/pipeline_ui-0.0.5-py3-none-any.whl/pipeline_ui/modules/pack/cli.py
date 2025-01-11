import shutil
import subprocess
from pathlib import Path
from typing import Optional

import git
import questionary
import typer
from rich import print
from rich.console import Console

console = Console()

def check_uv_installed():
    """Check if uv is installed."""
    try:
        subprocess.check_call(["uv", "--version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except subprocess.CalledProcessError:
        console.print("✗ uv is not installed. Please install uv before proceeding. Look here for installation steps: https://docs.astral.sh/uv/getting-started/installation/", style="red")
        return False

def create_directory_structure(base_path: Path, is_custom_pack: bool):
    """Create the basic directory structure for the project."""
    directories = [
        "workflow",
        "node",
        "_imported_pack",
    ]

    default_readme_path = Path(__file__).parent / "default_files" / "README.md"
    shutil.copy(default_readme_path, base_path / "README.md")
    
    for dir_name in directories:
        dir_path = base_path / dir_name
        dir_path.mkdir(parents=True, exist_ok=True)

def create_gitignore(base_path: Path):
    """Create a .gitignore file using the default template."""
    default_gitignore_path = Path(__file__).parent / "default_files" / ".gitignore"
    gitignore_path = base_path / ".gitignore"
    shutil.copy(default_gitignore_path, gitignore_path)

def create_pyproject_toml(base_path: Path, project_name: str, github_url: str = ""):
    """Create a pyproject.toml file based on the default template."""
    default_pyproject_path = Path(__file__).parent / "default_files" / "pyproject.toml"
    pyproject_path = base_path / "pyproject.toml"
    with open(default_pyproject_path, "r") as f:
        pyproject_content = f.read()
    pyproject_content = pyproject_content.replace("{project_name}", project_name)
    if github_url == "":
        pyproject_content = pyproject_content.replace("\"{github_url}\"", "\"\" # TODO: Add your repository url to be able to publish to pui")
    else:
        pyproject_content = pyproject_content.replace("{github_url}", github_url)
    with open(pyproject_path, "w") as f:
        f.write(pyproject_content)

def clone_repository(repo_url: str, base_path: Path):
    """Clone a repository and copy its contents."""
    try:
        git.Repo.clone_from(repo_url, base_path / "src")
        console.print(f"✓ Successfully cloned repository", style="green")
    except git.GitCommandError as e:
        console.print(f"✗ Failed to clone repository: {e}", style="red")

def choose_python_version():
    """Ask the user to choose a Python version, recommending 3.12."""
    python_version = questionary.select(
        "Choose a Python version (Recommended: 3.12):",
        choices=["3.12", "3.11", "3.10", "3.9", "3.8"],
        default="3.12"
    ).ask()
    return python_version

# typer command
def init():
    """Create a new folder structure for a custom pack."""
    if not check_uv_installed():
        return

    # Always ask for project name first
    project_name = questionary.text(
        "What is your project name?",
        validate=lambda text: len(text) > 0
    ).ask()

    # Create base directory
    base_path = Path(project_name)
    base_path.mkdir(exist_ok=True)
    console.print(f"\nCreating project in: {base_path.absolute()}\n", style="blue")

    # Choose Python version
    python_version = choose_python_version()
    python_version_path = base_path / ".python-version"
    with open(python_version_path, "w") as f:
        f.write(python_version)
    console.print(f"✓ Set Python version to: {python_version}", style="green")

    github_url = questionary.text(
        "What is the GitHub repository URL of this project? (optional)",
        default=""
    ).ask()

    # Ask if creating a custom pack
    is_custom_pack = questionary.confirm(
        "Are you trying to create a custom pack?",
        default=False
    ).ask()

    if is_custom_pack:
        is_based_on_repo = questionary.confirm(
            "Are you basing this on an existing repository?",
            default=False
        ).ask()

        if is_based_on_repo:
            repo_url = questionary.text(
                "Please enter the repository URL:"
            ).ask()
            with console.status("Cloning repository...", spinner="dots"):
                clone_repository(repo_url, base_path)



    # Create directory structure and files
    create_directory_structure(base_path, is_custom_pack)
    create_pyproject_toml(base_path, project_name, github_url)
    create_gitignore(base_path)

    console.print("\n✨ Project successfully created!", style="green bold")