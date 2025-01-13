from abc import ABC


class DirectoryHandler(ABC):
    """Abstract class for handling directories management

    ...

    Attributes
    ----------
    dirname : str
        Directory name to handle

    Methods
    -------
    create_minimal()
        Create the minimal directory structure

    create_standard()
        Create the standard directory structure

    create_professional()
        Create the professional directory structure
    """

    def __init__(self, dirname: str) -> None:
        """Initialize the DirectoryHandler class

        Args:
            dirname (str): Directory name to handle
        """
        self.dirname = dirname

    def create_minimal(self) -> None:
        pass

    def create_standard(self) -> None:
        pass

    def create_professional(self) -> None:
        pass
