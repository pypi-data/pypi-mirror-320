import os
from datetime import datetime

from ayods.notebook import NotebookDirectoryHandler
from ayods.data import DataDirectoryHandler


class ProjectHandler:
    """Class for handling the creation of a data science project

    ...

    Attributes
    ----------
    dirname : str
        Directory name to initialize the data science project

    project_type : str
        Type of project to create

    CURRENT_DATE : str
        Current date in YYYY-MM-DD format

    notebook_handler : NotebookDirectoryHandler
        Instance of the NotebookDirectoryHandler class

    Methods
    -------
    create_project()
        Create the data science project based on the project type

    __create_minimal()
        Create the minimal project structure

    __create_standard()
        Create the standard project structure

    __create_professional()
        Create the professional project structure
    """

    def __init__(self, dirname: str, project_type: str) -> None:
        """Initialize the ProjectHandler class

        Args:
            dirname (str): Directory name to initialize the data science project
            project_type (str): Type of project to create
        """

        self.dirname = dirname
        self.project_type = project_type
        self.CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
        self.notebook_handler = NotebookDirectoryHandler(dirname, self.CURRENT_DATE)
        self.data_handler = DataDirectoryHandler(dirname)

    def create_project(self) -> None:
        """Create the data science project based"""

        print(f"Creating {self.project_type.lower()} project...")

        # Create the project directory
        os.makedirs(self.dirname, exist_ok=True)

        # Create the project structure based on the project type
        if self.project_type == "Minimal":
            self.__create_minimal()
        elif self.project_type == "Standard":
            self.__create_standard()
        elif self.project_type == "Professional":
            self.__create_professional()

        print(f"Project created in {self.dirname}")

    def __create_minimal(self) -> None:
        """Create the minimal project structure"""

        print("Creating minimal project structure...")
        self.notebook_handler.create_minimal()
        self.data_handler.create_minimal()

    def __create_standard(self) -> None:
        """Create the standard project structure"""

        print("Creating standard project structure...")
        self.notebook_handler.create_standard()
        self.data_handler.create_standard()

    def __create_professional(self) -> None:
        """Create the professional project structure"""

        print("Creating professional project structure...")
        self.notebook_handler.create_professional()
        self.data_handler.create_professional()
