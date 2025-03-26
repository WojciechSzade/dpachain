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
        self.own_peer = None
        self.authorized = authorized
        self.public_key = public_key

    def get_peers_list(self):
        peers = self.peers.find()
        return [Peer.from_dict(peer) for peer in peers]

    def get_peer_by_nickname(self, nickname):
        peer = self.peers.find_one({"nickname": nickname})
        if peer is None:
            raise PeerNotFoundError(nickname)
        return Peer.from_dict(peer)

    def _get_peer_by_nickname(self, nickname):
        peer = self.peers.find_one({"nickname": nickname})
        if peer is None:
            return None
        return Peer.from_dict(peer)

    def get_valid_peers_names(self):
        peers = self.get_peers_list()
        return [peer.nickname for peer in peers if not peer.is_not_valid()]

    def get_valid_peers_to_connect(self):
        peers = self.get_peers_list()
        return [peer for peer in peers if not peer.is_not_valid() and peer.status != PeerStatus.OWN]

    def set_peer_status(self, nickname: str, status: PeerStatus, unban=False):
        peer = self.get_peer_by_nickname(nickname)
        if peer.status is PeerStatus.BANNED and not unban:
            raise PeerBannedError(nickname)
        self.peers.update_one({"nickname": nickname}, {
                              "$set": {"status": status.value}})

    def get_peer_state(self, nickname):
        return PeerStatus(self.get_peer_by_nickname(nickname).status)

    def get_peers_by_state(self, state):
        return [peer for peer in self.get_peers_list() if peer.status == state]

    def get_active_peers(self):
        peers = self.get_peers_list()
        return [peer.nickname for peer in peers if peer.status == PeerStatus.ACTIVE or peer.status == PeerStatus.OWN]

    def add_new_peer(self, nickname, adress=None, is_authorized=False, public_key=None, status=PeerStatus.UNKNOWN):
        new_peer = Peer(nickname, adress, status, is_authorized, public_key)
        if self._get_peer_by_nickname(nickname) is not None:
            raise PeerAlreadyExistsError(nickname)
        self.peers.update_one(
            {"nickname": nickname},
            {"$set": new_peer.dict},
            upsert=True)
        return new_peer

    def remove_peer(self, nickname):
        peer = self._get_peer_by_nickname(nickname)
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

    def _set_own_peer(self, nickname, adress=None):
        if self.own_peer is not None:
            raise OwnPeerAlreadyExistsError(self.own_peer)
        if len(self.get_peers_by_state(PeerStatus.OWN)) > 0:
            raise OwnPeerAlreadyExistsError(
                self.get_peers_by_state(PeerStatus.OWN)[0].nickname)
        self.own_peer = self.add_new_peer(
            nickname, adress, self.authorized, self.public_key, PeerStatus.OWN)

    def change_own_peer_nickname(self, nickname, adress=None):
        if self.own_peer is None:
            return self._set_own_peer(nickname, adress)
        self.set_peer_status(self.own_peer, PeerStatus.UNKNOWN)
        self.own_peer = self.add_new_peer(nickname, adress, self.authorized,
                                          self.public_key, PeerStatus.OWN)

    def get_own_peer_name(self):
        return self.own_peer.nickname

    def get_own_peer_adress(self):
        return self.own_peer.adress

    def get_authorized_peers(self):
        return [peer for peer in self.get_peers_list() if peer.is_authorized]
