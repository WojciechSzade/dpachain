class BlockError(Exception):
    """Base class for Block errors."""
    pass


class BlockAlreadyExistsError(BlockError):
    """Raised when a block that already exists is attempted to be created."""

    def __init__(self, block: str, additional_info: str = ""):
        self.block = block
        super().__init__(
            f"Block {str(block)} already exists. {additional_info}")


class BlockNotFoundError(BlockError):
    """Raised when a block that does not exist is attempted to be accessed."""

    def __init__(self, block: str, additional_info: str = ""):
        self.block = block
        super().__init__(
            f"Block {str(block)} not found. {additional_info}")


class InvalidBlockError(BlockError):
    """Raised when a block is invalid - has not been created by a authorized peer."""

    def __init__(self, block: str, additional_info: str = ""):
        self.block = block
        super().__init__(
            f"Block {str(block)} is invalid. {additional_info}")
        
class UnauthorizedBlockError(BlockError):
    """Raised when a block is invalid - has not been created by a authorized peer or is malicious in any other way"""

    def __init__(self, block: str, additional_info: str = ""):
        self.block = block
        super().__init__(
            f"Block {str(block)} is unauthorized. {additional_info}")
        
class CouldNotRemoveBlockError(BlockError):
    """Raised when a block could not be removed from the chain"""

    def __init__(self, block: str, additional_info: str = ""):
        self.block = block
        super().__init__(
            f"Could not remove block {str(block)}. {additional_info}")