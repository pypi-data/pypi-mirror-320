import os

import questionary


def validate_dirname(dirname: str) -> bool:
    """Validate the directory name for the project

    Args:
        dirname (str): Directory name to validate

    Returns:
        bool: True if the directory is valid, False otherwise
    """

    # Normalize the path to prevent traversal issues
    normalized_path = os.path.abspath(dirname)

    # Check if the path is within an allowed base directory
    allowed_base = os.getcwd()
    if not normalized_path.startswith(allowed_base):
        print(f"Invalid directory: {dirname} is outside the allowed base path.")
        return False

    if normalized_path == allowed_base:
        # Check if the directory is empty or not
        if os.listdir(normalized_path):
            print(f"Directory {dirname} is not empty!")
            confirmation: str = questionary.confirm(
                "Do you want to continue and create a project in this directory?",
                default=False,
            ).ask()

            if not confirmation:
                return False

        # Remove the content of the directory recursively
        for root, dirs, files in os.walk(normalized_path, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))

        return True

    # Ensure the directory doesn't already exist
    if os.path.exists(normalized_path):
        if os.path.isdir(normalized_path):
            print(f"Directory {dirname} already exists!")
            confirmation: str = questionary.confirm(
                "Do you want to overwrite the existing directory?", default=False
            ).ask()

            if not confirmation:
                return False

            # Overwrite the existing directory
            os.rmdir(normalized_path)
        else:
            print(f"{dirname} exists but is not a directory!")
            return False

    return True


def create_gitkeep(dirname: str) -> None:
    """Create a .gitkeep file in the specified directory

    Args:
        dirname (str): Directory name to create the .gitkeep file
    """

    gitkeep = os.path.join(dirname, ".gitkeep")
    with open(gitkeep, "w") as f:
        f.write("")


def create_archive(dirname: str) -> None:
    """Create an archive directory in the specified directory

    Args:
        dirname (str): Directory name to create the archive directory
    """

    archive_dir = os.path.join(dirname, "archive")
    os.makedirs(archive_dir, exist_ok=True)
    create_gitkeep(archive_dir)


def create_figures(dirname: str) -> None:
    """Create a figures directory in the specified directory

    Args:
        dirname (str): Directory name to create the figures directory
    """

    figures_dir = os.path.join(dirname, "figures")
    os.makedirs(figures_dir, exist_ok=True)
    create_gitkeep(figures_dir)
