import logging
from p2pd import *
from tenacity import after_log, before_log, before_sleep_log, retry, stop_after_attempt

from src.node.protocols import ProtocolManager
from src.peer.models import PeerStatus
from src.peer.peers import PeersManager


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 20  # 2 minutes


class NodeManager:
    def __init__(self, peers_manager: PeersManager, nickname):
        self.node = None
        self.peers_manager = peers_manager
        self.protocol_manager = ProtocolManager(self.peers_manager)
        self.nickname = nickname
        self.pipes = []

    async def start(self, port):
        self.node = await self.__create_node(port)
        await self._set_node_nickname(self.nickname)
        # await self.connect_to_nodes()

    async def stop(self):
        await self.node.close()

    async def _set_node_nickname(self, nickname):
        try:
            node_name = await self.node.nickname(nickname)
            logger.info(f"Node name set to: {node_name}")

        except:
            logger.error(f"Failed to set node name to {nickname}")

    async def sync_chain(self):
        nodes_list = self.peers_manager.get_valid_peers_to_connect()
        responses = []
        for node in nodes_list:
            pipe = await self.node.connect(node.nickname)
            if pipe is None:
                logger.info(
                    f"Failed to connect to {node.nickname} with previous state {self.peers_manager.get_peer_state(node.nickname)}")
                self.peers_manager.set_peer_status(
                    node.nickname, PeerStatus.INACTIVE)
                continue
            logger.info(f"Connected to {node.nickname}")
            logger.info(f"Pipe is {pipe.sock}")
            chain_size = await self.protocol_manager.request_chain_size(pipe)
            responses.append({"node": node, "chain_size": chain_size})
            pipe.close()

        # select best node
        # connect to it
        # sync node list
        # compare blokchain(size and last hash)
        # foreaach missing block ask_for_block
        # if sent an invalid one - ban the node, repeat process
        # synced
        pass

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
            node.add_msg_cb(self.protocol_manager.add_peer_protocole_support)
            await node.start(out=True)
            logger.info(f"Node started = {node.addr_bytes}")
            logger.info(f"Node port = {node.listen_port}",)
            return node
        except Exception as e:
            logger.error(f"Failed to create node: {e}")
            raise e
