import logging
from p2pd import *
from tenacity import after_log, before_log, before_sleep_log, retry, stop_after_attempt

from src.peer.protocols import PeerListProtocol
from src.peer.models import PeerStatus
from src.peer.peers import PeersManager


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 20  # 2 minutes


class NodeService:
    def __init__(self, peers_manager: PeersManager, nickname):
        self.node = None
        self.peers_manager = peers_manager
        self.peer_list_protocol = PeerListProtocol(self.peers_manager)
        self.nickname = nickname
        self.pipes = []

    async def start(self, port):
        self.node = await self.__create_node(port)
        await self._set_node_nickname(self.nickname)
        await self.connect_to_nodes()

    async def stop(self):
        await self.node.close()

    async def _set_node_nickname(self, nickname):
        try:
            node_name = await self.node.nickname(nickname)
            logger.info(f"Node name set to: {node_name}")

        except:
            logger.error("Failed to set node name")

    @retry(
        stop=stop_after_attempt(max_tries),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.WARN),
        before_sleep=before_sleep_log(logger, logging.INFO)
    )
    async def connect_to_nodes(self):
        for peer_name in self.peers_manager.get_peers_names():
            if self.peers_manager.get_peer_state(peer_name) == PeerStatus.OWN:
                continue
            try:
                pipe = await self.node.connect(peer_name)
                if pipe is None:
                    logger.info(f"Failed to connect to {peer_name} with previous state {
                                self.peers_manager.get_peer_state(peer_name)}")
                    self.peers_manager.set_peer_state(
                        peer_name, PeerStatus.INACTIVE)
                    continue
                logger.info(f"Connected to {peer_name}")
                logger.info(f"Pipe is {pipe.sock}")
                self.pipes.append(pipe)
                await self.peer_list_protocol.sync_peerlist_with_pipe(pipe)
                self.peers_manager.set_peer_state(peer_name, PeerStatus.ACTIVE)
            except Exception as e:
                if str(e).startswith("Could not fetch"):
                    logger.info(f"Failed to connect to {peer_name} with previous state {
                                self.peers_manager.get_peer_state(peer_name)}")
                    self.peers_manager.set_peer_state(
                        peer_name, PeerStatus.INACTIVE)
                    continue
                logger.error(f"Failed to connect to {peer_name}: {e}")
                self.peers_manager.set_peer_state(
                    peer_name, PeerStatus.INACTIVE)
                continue

    @retry(
        stop=stop_after_attempt(max_tries),
        before=before_log(logger, logging.INFO),
        after=after_log(logger, logging.WARN),
        before_sleep=before_sleep_log(logger, logging.INFO)
    )
    async def __create_node(self, port):
        try:
            logger.info("Creating node...")
            node = P2PNode(port=port)
            node.add_msg_cb(self.__add_echo_support)
            node.add_msg_cb(self.peer_list_protocol.add_peer_protocole_support)
            await node.start(out=True)
            logger.info(f"Node started = {node.addr_bytes}")
            logger.info(f"Node port = {node.listen_port}",)
            return node
        except Exception as e:
            logger.error(f"Failed to create node: {e}")
            raise e

    async def __add_echo_support(self, msg, client_tup, pipe):
        if b"ECHO" == msg[:4]:
            print()
            print("\tGot echo proto msg: " + to_s(msg) +
                  fstr(" from {0}", (client_tup,)))
            print()
            await pipe.send(msg[4:], client_tup)
