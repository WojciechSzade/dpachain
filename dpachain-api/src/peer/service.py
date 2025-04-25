from __future__ import annotations
from typing import Optional
from src.peer.models import Peer, PeerStatus
from src.peer.interfaces import IPeerManager, IPeerService


class PeerService(IPeerService):
    def __init__(self, peer_manager: IPeerManager):
        self.peer_manager = peer_manager

    def add_new_peer(self, nickname: str, public_key: str, adress: Optional[str] = None, is_authorized: bool = False) -> tuple[str, Peer]:
        return "Peer has been added", self.peer_manager.add_new_peer(
            nickname,  public_key, adress, is_authorized)

    def get_peers_list(self) -> list[Peer]:
        peers = self.peer_manager.get_peers_list()
        return peers

    def remove_peer(self, nickname: str):
        peer = self.peer_manager.get_peer_by_nickname(nickname)
        self.peer_manager.remove_peer(peer)
        return "Peer has been removed"

    def ban_peer(self, nickname: str):
        peer = self.peer_manager.get_peer_by_nickname(nickname)
        self.peer_manager.ban_peer(peer)
        return "Peer has been banned"

    def unban_peer(self, nickname: str):
        peer = self.peer_manager.get_peer_by_nickname(nickname)
        return self.peer_manager.unban_peer(peer)
