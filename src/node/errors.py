class NodeError(Exception):
    """Base class for Node errors."""
    pass


class NoPeersAviableError(NodeError):
    """Raised when could not connect to any valid peers from the database"""

    def __init__(self):
        super().__init__(f"Could not connect to any valid peers saved.")
