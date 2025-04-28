from src.peer.models import Peer


class NodeError(Exception):
    """Base class for Node errors."""
    pass


class NoPeersAvailableError(NodeError):
    """Raised when could not connect to any valid peers from the database"""

    def __init__(self):
        super().__init__(f"Could not connect to any valid peers saved.")


class PeerUnavailableError(NodeError):
    """Raise when couldn't connect to a peer"""

    def __init__(self, peer: Peer):
        super().__init__(f"Could not connect to peer {peer.nickname}.")


class NoResponseReceivedError(NodeError):
    """Raise when didn't receive a response from a peer"""

    def __init__(self, pipe, protocol_name):
        super().__init__(
            f"Did not receive response from pipe {pipe} running protocol {protocol_name}")


class InvalidResponseReceivedError(NodeError):
    """Raise when received an invalid reponse from a peer"""

    def __init__(self, pipe, protocol_name, payload):
        super().__init__(
            f"Received invalid response from pipe {pipe} running protocol {protocol_name}. Payload: {payload}")


class InvalidMessageReceivedError(NodeError):
    """Raise when received an invalid message"""

    def __init__(self, msg):
        super().__init__(f"Received an invalid message: {msg}")


class InvalidMessageAuthorError(NodeError):
    """Raise when received a message with an invalid author"""

    def __init__(self, author, reason, protocol):
        super().__init__(
            f"Message's author '{author}' invalid, reason: {reason}. Protocol was: {protocol}.")


class InvalidSignatureError(NodeError):
    """Raised when the signature is invalid."""

    def __init__(self, peer_nickname):
        self.peer_nickname = peer_nickname
        super().__init__(f"Invalid signature from peer {self.peer_nickname}.")
