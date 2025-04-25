from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional


from src.peer.models import Peer, PeerStatus


class IPeerManager(ABC):
    """Peer manager is used to manage all operations related to creating new peers, changing their status and storing them in the database"""
    @abstractmethod
    def get_peers_list(self) -> list[Peer]:
        """Returns all the peers"""
        ...

    @abstractmethod
    def get_peer_by_nickname(self, nickname: str) -> Peer:
        ...

    @abstractmethod
    def find_peer_by_nickname(self, nickname: str) -> Peer | None:
        ...

    @abstractmethod
    def get_valid_peers_to_connect(self) -> list[Peer]:
        """Returns peers that are valid only"""
        ...

    @abstractmethod
    def set_peer_status(self, peer: Peer, status: PeerStatus, unban=False) -> None:
        """Changes peer's status"""
        ...

    @abstractmethod
    def add_new_peer(self, nickname: str, public_key: str, adress: Optional[str] = None, is_authorized=False, status=PeerStatus.UNKNOWN):
        ...

    @abstractmethod
    def remove_peer(self, peer: Peer):
        ...

    @abstractmethod
    def ban_peer(self, peer: Peer):
        ...

    @abstractmethod
    def unban_peer(self, peer: Peer):
        ...

    @abstractmethod
    def change_own_peer_nickname(self, nickname: str, adress=None):
        ...

    @abstractmethod
    def get_own_peer_name(self) -> str:
        ...

    @abstractmethod
    def get_own_peer_adress(self) -> str:
        ...

    @abstractmethod
    def get_own_peer_public_key(self) -> str:
        ...

    @abstractmethod
    def get_authorized_peers(self) -> list[Peer]:
        ...


class IPeerService(ABC):
    """Service class to be used as a proxy between the API and PeerManager, with some neccessary improvments, for the API"""
    @abstractmethod
    def add_new_peer(self, nickname: str, public_key: str, adress: Optional[str] = None, is_authorized: bool = False) -> tuple[str, Peer]:
        ...

    @abstractmethod
    def get_peers_list(self) -> list[Peer]:
        ...

    @abstractmethod
    def remove_peer(self, nickname: str):
        ...

    @abstractmethod
    def ban_peer(self, nickname: str):
        ...

    @abstractmethod
    def unban_peer(self, nickname: str):
        ...
