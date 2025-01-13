import argparse
import os

import questionary

from ayods.project import ProjectHandler
from ayods.util import validate_dirname


def create_project_prompt(dirname: str) -> None:
    """Create a new data science project in the specified directory

    Args:
        dirname (str): Directory name to initialize the data science project
    """

    print(f"Creating a new data science project in {dirname}\n")

    project_type: str = questionary.select(
        "Choose the project template:",
        choices=["Minimal", "Standard", "Professional"],
    ).ask()

    if not project_type:
        exit(1)

    project_handler = ProjectHandler(dirname, project_type)
    project_handler.create_project()


def main() -> None:
    """Main function for the CLI tool"""

    parser = argparse.ArgumentParser(
        prog="ayods",
        description="Python CLI tool for initializing data science projects",
    )

    parser.add_argument(
        "dirname",
        nargs="?",
        help="Directory name to initialize the data science project",
    )

    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s 0.1",
    )

    args = parser.parse_args()

    if not args.dirname:
        parser.print_help()
        return

    if args.dirname == ".":
        args.dirname = os.getcwd()

    if not validate_dirname(args.dirname):
        return

    create_project_prompt(args.dirname)
