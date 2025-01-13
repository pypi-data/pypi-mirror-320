import os
from importlib.resources import files

from ayods.directory_handler import DirectoryHandler
from ayods.util import create_archive, create_figures


class NotebookDirectoryHandler(DirectoryHandler):
    """Class for handling the creation of notebook directories

    ...

    Attributes
    ----------
    dirname : str
        Directory name to handle

    datetime : str
        Current date and time in YYYY-MM-DD-HHMM format

    notebook_dir : str
        Notebook directory path

    Methods
    -------
    create_minimal()
        Create the minimal notebook directory structure

    create_standard()
        Create the standard notebook directory structure

    create_professional()
        Create the professional notebook directory structure
    """

    def __init__(self, dirname: str, datetime: str) -> None:
        """Initialize the NotebookDirectoryHandler class

        Args:
            dirname (str): Directory name to handle
            datetime (str): Current date and time in YYYY-MM-DD-HHMM format
        """

        DirectoryHandler.__init__(self, dirname)
        self.datetime = datetime
        self.notebook_dir = os.path.join(self.dirname, "notebooks")

    def create_minimal(self) -> None:
        """Create the minimal notebook directory structure"""

        os.makedirs(self.notebook_dir, exist_ok=True)
        notebook = os.path.join(self.notebook_dir, f"01-[2-4 word description].ipynb")

        content = files("ayods.templates").joinpath("Minimal.ipynb").read_bytes()

        with open(notebook, "wb") as nb:
            nb.write(content)

    def create_standard(self) -> None:
        """Create the standard notebook directory structure"""

        os.makedirs(self.notebook_dir, exist_ok=True)
        notebook = os.path.join(
            self.dirname, "notebooks", f"01-[2-4 word description].ipynb"
        )

        content = files("ayods.templates").joinpath("Standard.ipynb").read_bytes()

        with open(notebook, "wb") as nb:
            nb.write(content)

        create_archive(self.notebook_dir)

        create_figures(self.dirname)

    def create_professional(self) -> None:
        """Create the professional notebook directory structure"""

        os.makedirs(self.notebook_dir, exist_ok=True)
        develop_dir = os.path.join(self.notebook_dir, "develop")

        os.makedirs(develop_dir, exist_ok=True)

        notebook_develop = os.path.join(
            develop_dir,
            f"{self.datetime}-[author-initial]-[2-4 word description].ipynb",
        )

        content = files("ayods.templates").joinpath("Professional.ipynb").read_bytes()

        with open(notebook_develop, "wb") as nb:
            nb.write(content)

        create_archive(develop_dir)

        deliver_dir = os.path.join(self.notebook_dir, "deliver")

        os.makedirs(deliver_dir, exist_ok=True)

        notebook_deliver = os.path.join(deliver_dir, f"[final-analysis].ipynb")

        with open(notebook_deliver, "wb") as nb:
            nb.write(content)

        create_figures(self.dirname)
