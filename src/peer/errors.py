class PeerError(Exception):
    """Base class for Peer errors."""
    pass


class PeerNotFoundError(PeerError):
    """Raised when peer is not found."""

    def __init__(self, nickname: str):
        self.nickname = nickname
        super().__init__(f"Peer {nickname} not found")


class PeerBannedError(PeerError):
    """Raised when peer is banned."""

    def __init__(self, nickname: str):
        self.nickname = nickname
        super().__init__(f"Peer {nickname} is banned")


class PeerAlreadyExistsError(PeerError):
    """Raised when peer already exists."""

    def __init__(self, nickname: str):
        self.nickname = nickname
        super().__init__(f"Peer {nickname} already exists")


class PeerRemovalError(PeerError):
    """Raised when peer removal fails."""

    def __init__(self, nickname: str, message: str):
        super().__init__(f"Removing peer {nickname} failed.\n" + message)
