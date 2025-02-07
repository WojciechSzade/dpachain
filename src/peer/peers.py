import logging
from p2pd import *

from src.core.config import settings
from src.peer.models import Peer, PeerStatus
from src.core.db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PeersManager:
    def __init__(self, client_db, authorized, public_key):
        self.db = client_db.blockchain
        self.peers = self.db.peers
        self.own_peer_name = settings.HOST_NODE_NAME
        if self.peers.find_one({"nickname": self.own_peer_name}) is None:
            own_peer = Peer(settings.HOST_NODE_NAME, PeerStatus.OWN,
                            is_authorized=authorized, is_banned=False, public_key=public_key)
            self.peers.insert_one(own_peer.dict)

    def get_peers_list(self):
        peers = self.peers.find()
        return [Peer.from_dict(peer) for peer in peers]

    def get_peer_by_name(self, name):
        peer = self.peers.find_one({"nickname": name})
        if peer is None:
            logger.error(f"Peer {name} not found")
        return Peer.from_dict(peer)

    def get_valid_peers_names(self):
        peers = self.get_peers_list()
        return [peer.nickname for peer in peers if peer.is_valid()]

    def get_valid_peers_to_connect(self):
        peers = self.get_peers_list()
        return [peer for peer in peers if peer.is_valid() and peer.status != PeerStatus.OWN]

    def set_peer_state(self, name, state):
        self.peers.update_one({"nickname": name}, {
                              "$set": {"status": state.value}})

    def get_peer_state(self, name):
        return PeerStatus(self.get_peer_by_name(name).status)

    def get_active_peers(self):
        peers = self.get_peers_list()
        return [peer.nickname for peer in peers if peer.status == PeerStatus.ACTIVE or peer.status == PeerStatus.OWN]

    def get_peerlist_hash(self):
        hash = self.__calculate_hash_sum(self.get_active_peers())
        return hash

    @staticmethod
    def __calculate_hash_sum(elements):
        hashsum = 0
        for e in elements:
            hashsum += int(hashlib.sha256(str(e).encode()).hexdigest(), 16)
            hashsum %= 2**256
        final_hashsum = hashlib.sha256(str(hashsum).encode()).hexdigest()
        return final_hashsum

    def parse_peer_list_message(self, peerlist):
        for name in peerlist:
            if name not in self.get_valid_peers_names() and name != self.get_own_name():
                self.peers.insert_one(Peer(name, PeerStatus.UNKNOWN).dict)

    def get_own_peer(self):
        return self.get_peer_by_name(self.own_peer_name)

    def get_own_name(self):
        return self.own_peer_name
