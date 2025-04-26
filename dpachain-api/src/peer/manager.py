from __future__ import annotations
import logging
from p2pd import *
from typing import Optional

from src.peer.models import Peer, PeerStatus
from src.core.db import init_db
from src.peer.errors import *
from src.peer.interfaces import IPeerManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PeerManager(IPeerManager):
    def __init__(self, client_db, authorized: bool, public_key: str):
        self.db = client_db.blockchain
        self.peers = self.db.peers
        self.own_peer = None
        self.authorized = authorized
        self.public_key = public_key

    def get_peers_list(self) -> list[Peer]:
        peers = self.peers.find()
        return [Peer.from_dict(peer) for peer in peers]

    def get_peer_by_nickname(self, nickname: str) -> Peer:
        peer = self.peers.find_one({"nickname": nickname})
        if peer is None:
            raise PeerNotFoundError(nickname)
        return Peer.from_dict(peer)

    def find_peer_by_nickname(self, nickname: str) -> Peer | None:
        peer = self.peers.find_one({"nickname": nickname})
        if peer is None:
            return None
        return Peer.from_dict(peer)

    def get_valid_peers_to_connect(self) -> list[Peer]:
        peers = self.get_peers_list()
        return [peer for peer in peers if not peer.is_not_valid() and peer.status != PeerStatus.OWN]

    def set_peer_status(self, peer: Peer, status: PeerStatus, unban: bool = False) -> None:
        if peer.get_state() == PeerStatus.BANNED and not unban:
            raise PeerBannedError(peer.nickname)
        self.peers.update_one({"nickname": peer.nickname}, {
                              "$set": {"status": status.value}})

    def _get_peers_by_status(self, status: PeerStatus) -> list[Peer]:
        return [peer for peer in self.get_peers_list() if peer.status == status]

    def add_new_peer(self, nickname: str, public_key: str, adress: Optional[str] = None, is_authorized=False, status=PeerStatus.UNKNOWN):
        if public_key is None:
            raise NoPublicKeyForPeerError(nickname)
        if self.find_peer_by_nickname(nickname) is not None:
            raise PeerAlreadyExistsError(nickname)
        new_peer = Peer(nickname, public_key, adress, status, is_authorized)
        self.peers.update_one(
            {"nickname": nickname},
            {"$set": new_peer.as_dict()},
            upsert=True)
        return new_peer

    def remove_peer(self, peer: Peer, remove_own=False):
        if peer.get_state() == PeerStatus.OWN and not remove_own:
            raise PeerRemovalError(peer.nickname, "Cannot remove own peer")
        elif peer.status == PeerStatus.BANNED:
            raise PeerBannedError(peer.nickname)
        self.peers.delete_one({"nickname": peer.nickname})

    def ban_peer(self, peer: Peer):
        if peer.status == PeerStatus.OWN:
            raise ForbiddenOperationForOwnPeerError("ban")

        self.set_peer_status(peer, PeerStatus.BANNED)

    def unban_peer(self, peer: Peer):
        if peer.get_state() != PeerStatus.BANNED:
            msg = f"Peer {peer.nickname} had status {peer.get_state()} instead of banned - no operations were performed."
            return msg
        self.set_peer_status(peer, PeerStatus.UNKNOWN, unban=True)
        return f"Peer {peer.nickname} unbanned."

    def _set_own_peer(self, nickname: str, adress=None):
        if self.own_peer is not None:
            raise OwnPeerAlreadyExistsError(self.own_peer)
        own_peers_in_db = self._get_peers_by_status(PeerStatus.OWN)
        if len(own_peers_in_db) > 0:
            if own_peers_in_db == 1:
                if own_peers_in_db[0].nickname == nickname:
                    return
                else:
                    self.remove_peer(own_peers_in_db[0], remove_own=True)
            else:
                for invalid_own_peer in own_peers_in_db:
                    self.remove_peer(invalid_own_peer, remove_own=True)
        self.own_peer = self.add_new_peer(
            nickname, self.public_key, adress, self.authorized, PeerStatus.OWN)

    def change_own_peer_nickname(self, nickname, adress=None):
        if self.own_peer is None:
            return self._set_own_peer(nickname, adress)
        self.set_peer_status(self.own_peer, PeerStatus.UNKNOWN)
        self.own_peer = self.add_new_peer(
            nickname, self.public_key, adress, self.authorized, PeerStatus.OWN)

    def get_own_peer_name(self) -> str:
        if self.own_peer is None:
            raise OwnPeerWasNotSetError()
        return self.own_peer.nickname

    def get_own_peer_adress(self) -> str:
        if self.own_peer is None:
            raise OwnPeerWasNotSetError()
        return self.own_peer.adress

    def get_own_peer_public_key(self) -> str:
        if self.own_peer is None:
            raise OwnPeerWasNotSetError()
        return self.public_key

    def get_authorized_peers(self) -> list[Peer]:
        return [peer for peer in self.get_peers_list() if peer.is_authorized]
