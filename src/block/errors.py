class BlockError(Exception):
    """Base class for Block errors."""
    pass


class BlockAlreadyExistsError(BlockError):
    """Raised when a block that already exists is attempted to be created."""

    def __init__(self, block: int, additional_info: str = ""):
        self.block = block
        super().__init__(
            f"Block {str(block)} already exists. {additional_info}")
