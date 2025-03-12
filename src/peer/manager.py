import logging
from p2pd import *

from src.peer.models import Peer, PeerStatus
from src.core.db import init_db
from src.peer.errors import *

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PeersManager:
    def __init__(self, client_db, authorized, public_key):
        self.db = client_db.blockchain
        self.peers = self.db.peers
        self.own_peer_name = None
        self.AUTHORIZED = authorized
        self.PUBLIC_KEY = public_key

    def get_peers_list(self):
        peers = self.peers.find()
        return [Peer.from_dict(peer) for peer in peers]

    def get_peer_by_nickname(self, nickname):
        peer = self.peers.find_one({"nickname": nickname})
        if peer is None:
            raise PeerNotFoundError(nickname)
        return Peer.from_dict(peer)

    def get_valid_peers_names(self):
        peers = self.get_peers_list()
        return [peer.nickname for peer in peers if peer.is_valid()]

    def get_valid_peers_to_connect(self):
        peers = self.get_peers_list()
        return [peer for peer in peers if peer.is_valid() and peer.status != PeerStatus.OWN]

    def set_peer_status(self, nickname: str, status: PeerStatus):
        peer = self.get_peer_by_nickname(nickname)
        if peer.status is PeerStatus.BANNED:
            raise PeerBannedError(nickname)
        self.peers.update_one({"nickname": nickname}, {
                              "$set": {"status": status.value}})

    def get_peer_state(self, name):
        return PeerStatus(self.get_peer_by_nickname(name).status)

    def get_active_peers(self):
        peers = self.get_peers_list()
        return [peer.nickname for peer in peers if peer.status == PeerStatus.ACTIVE or peer.status == PeerStatus.OWN]

    def add_new_peer(self, nickname, is_authorized=False, public_key=None, status=PeerStatus.UNKNOWN):
        new_peer = Peer(nickname, status, is_authorized, public_key)
        result = self.peers.update_one(
            {"nickname": nickname},
            {"$set": new_peer.dict},
            upsert=True)
        if result.matched_count > 0:
            raise PeerAlreadyExistsError(nickname)

    def remove_peer(self, nickname):
        peer = self.get_peer_by_nickname(nickname)
        if peer.status == PeerStatus.OWN:
            raise PeerRemovalError(nickname, "Cannot remove own peer")
        elif peer.status == PeerStatus.BANNED:
            raise PeerBannedError(nickname)
        self.peers.delete_one({"nickname": nickname})

    def ban_peer(self, nickname):
        peer = self.get_peer_by_nickname(nickname)
        if peer.status == PeerStatus.OWN:
            raise PeerBannedError(nickname)

        self.set_peer_status(nickname, PeerStatus.BANNED)

    def unban_peer(self, nickname):
        if self.get_peer_by_nickname(nickname) is None:
            logger.warning(f"Peer {nickname} does not exist")
            return
        if self.get_peer_state(nickname) != PeerStatus.BANNED:
            logger.warning(f"Peer {nickname} is not banned")
            return
        self.set_peer_status(nickname, PeerStatus.UNKNOWN)

    def _set_own_peer(self, nickname):
        if self.own_peer_name is not None:
            raise OwnPeerAlreadyExistsError(self.own_peer_name)
        self.own_peer_name = nickname
        self.add_new_peer(nickname, self.AUTHORIZED,
                          self.PUBLIC_KEY, PeerStatus.OWN)

    def change_own_peer_name(self, nickname):
        if self.own_peer_name is None:
            return self._set_own_peer(nickname)
        self.set_peer_status(self.own_peer_name, PeerStatus.UNKNOWN)
        self.add_new_peer(nickname, self.AUTHORIZED,
                          self.PUBLIC_KEY, PeerStatus.OWN)
        self.own_peer_name = nickname

    def get_own_peer_name(self):
        return self.own_peer_name

    def get_authorized_peers(self):
        return [peer for peer in self.get_peers_list() if peer.is_authorized]
