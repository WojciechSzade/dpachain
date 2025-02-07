import logging
from p2pd import *

from src.core.config import settings
from src.peer.models import Peer, PeerStatus
from src.core.db import init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PeersManager:
    def __init__(self, database_url, authorized, public_key):
        self.client_db = init_db(database_url)
        self.db = self.client_db.blockchain
        self.peers = self.db.peers
        self.own_peer_name = settings.HOST_NODE_NAME
        if self.peers.find_one({"nickname": self.own_peer_name}) is None:
            own_peer = Peer(settings.HOST_NODE_NAME, PeerStatus.OWN,
                            is_authorized=authorized, is_banned=False, public_key=public_key)
            self.peers.insert_one(own_peer.dict)

    def get_peers_list(self):
        return self.peers.find()

    def get_peer_by_name(self, name):
        peer = self.peers.find_one({"nickname": name})
        if peer is None:
            logger.error(f"Peer {name} not found")
            raise ValueError(f"Peer {name} not found")
        return peer

    def get_peers_names(self):
        peers = self.get_peers_list()
        return [peer["nickname"] for peer in peers]

    def set_peer_state(self, name, state):
        self.peers.update_one({"nickname": name}, {
                              "$set": {"status": state.value}})

    def get_peer_state(self, name):
        return PeerStatus(self.get_peer_by_name(name)["status"])

    def get_active_peers(self):
        peers = self.get_peers_list()
        return [peer["nickname"] for peer in peers if peer["status"] == PeerStatus.ACTIVE.value or peer["status"] == PeerStatus.OWN.value]

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
            if name not in self.get_peers_names() and name != self.get_own_name():
                self.peers.insert_one(Peer(name, PeerStatus.UNKNOWN).dict)

    def get_own_peer(self):
        return self.get_peer_by_name(self.own_peer_name)

    def get_own_name(self):
        return self.own_peer_name
