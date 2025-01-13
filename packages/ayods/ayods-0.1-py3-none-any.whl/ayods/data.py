import os

from ayods.directory_handler import DirectoryHandler
from ayods.util import create_gitkeep


class DataDirectoryHandler(DirectoryHandler):
    """Class for handling the creation of data directories

    ...

    Attributes
    ----------
    dirname : str
        Directory name to handle

    data_dir : str
        Data directory path

    Methods
    -------
    create_minimal()
        Create the minimal data directory structure

    create_standard()
        Create the standard data directory structure

    create_professional()
        Create the professional data directory structure
    """

    def __init__(self, dirname: str) -> None:
        """Initialize the DataDirectoryHandler class

        Args:
            dirname (str): Directory name to handle
        """

        DirectoryHandler.__init__(self, dirname)
        self.data_dir = os.path.join(self.dirname, "data")

    def create_minimal(self) -> None:
        """Create the minimal data directory structure"""

        os.makedirs(self.data_dir, exist_ok=True)
        create_gitkeep(self.data_dir)

    def create_standard(self) -> None:
        """Create the standard data directory structure"""

        os.makedirs(self.data_dir, exist_ok=True)
        test_dir = os.path.join(self.data_dir, "test")
        os.makedirs(test_dir, exist_ok=True)
        create_gitkeep(test_dir)

        train_dir = os.path.join(self.data_dir, "train")
        os.makedirs(train_dir, exist_ok=True)
        create_gitkeep(train_dir)

    def create_professional(self) -> None:
        """Create the professional data directory structure"""

        os.makedirs(self.data_dir, exist_ok=True)
        raw_dir = os.path.join(self.data_dir, "raw")
        os.makedirs(raw_dir, exist_ok=True)
        create_gitkeep(raw_dir)

        processed_dir = os.path.join(self.data_dir, "processed")
        os.makedirs(processed_dir, exist_ok=True)
        create_gitkeep(processed_dir)

        external_dir = os.path.join(self.data_dir, "cleaned")
        os.makedirs(external_dir, exist_ok=True)
        create_gitkeep(external_dir)
