import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PeerListProtocol:
    def __init__(self, peers_manager):
        self.peers_manager = peers_manager

    async def add_peer_protocole_support(self, msg, client_tup, pipe):
        if msg == (b"SENDPEERHASH"):
            logger.info(f"Received request for peerhash from {pipe}")
            logger.info("--------------------------------------------------")
            logger.info(msg)
            logger.info(client_tup)
            logger.info(pipe.get_client_tup())
            await self.send_peerhash_to_pipe(pipe)
        if msg == (b"SENDPEERLIST"):
            logger.info(f"Received request for peerlist from {pipe}")
            await self.send_peerlist_to_pipe(pipe)
        if msg.startswith(b"PEERHASH"):
            logger.info(f"Received peerhash from {pipe}")
            await self.receive_peerhash(msg)
        if msg.startswith(b"PEERLIST"):
            logger.info(f"Received peerlist from {pipe}")
            await self.receive_peerlist(msg)

    async def get_peerhash_from_pipe(self, pipe):
        await pipe.send(b"SENDPEERHASH")
        logger.info(f"Sent request for peerhash to {pipe}")
        buf = await pipe.recv(timeout=100)
        if buf is None:
            logger.info(f"Failed to receive peerhash from {pipe}")
            return None
        return self.__read_peerhash(buf)

    async def get_peerlist_from_pipe(self, pipe):
        await pipe.send(b"SENDPEERLIST")
        logger.info(f"Sent request for peerlist to {pipe}")
        buf = await pipe.recv(timeout=100)
        if buf is None:
            logger.info(f"Failed to receive peerlist from {pipe}")
            return None
        return self.__read_peerlist(buf)

    async def send_peerhash_to_pipe(self, pipe):
        logger.info(f"Sending peerhash to {pipe}")
        peerhash = self.peers_manager.get_peerlist_hash().encode()
        await pipe.send(b"PEERHASH" + peerhash)
        logger.info(f"Sent peerhash to {pipe}")

    async def send_peerlist_to_pipe(self, pipe):
        peerlist = self.peers_manager.get_peers_names()
        peerlist = json.dumps(peerlist).encode()
        await pipe.send(b"PEERLIST" + peerlist)
        logger.info(f"Sent peerlist to {pipe}")

    async def receive_peerhash(self, msg):
        peerhash = self.__read_peerhash(msg)
        if peerhash is None:
            return None
        logger.info(f"Received peerhash: {peerhash}")
        return peerhash

    async def receive_peerlist(self, msg):
        peerlist = self.__read_peerlist(msg)
        if peerlist is None:
            return None
        logger.info(f"Received peerlist: {peerlist}")
        return peerlist

    async def sync_peerlist_with_pipe(self, pipe):
        logger.info(f"Syncing peerlist with {pipe}")
        own_peerhash = self.peers_manager.get_peerlist_hash()
        pipe_peerhash = await self.get_peerhash_from_pipe(pipe)
        if pipe_peerhash is None:
            logger.warning(f"Failed to receive peerhash from {pipe}")
            return
        logger.info(f"Peerhash from pipe: {pipe_peerhash}")
        logger.info(f"Received peerhash is same as own: {pipe_peerhash == own_peerhash}")
        if pipe_peerhash != own_peerhash:
            pipe_peerlist = await self.get_peerlist_from_pipe(pipe)
            logger.info(f"Peerlist from pipe: {pipe_peerlist}")
            self.peers_manager.parse_peer_list_message(pipe_peerlist)

    def __read_peerhash(self, buf):
        if buf.startswith(b"PEERHASH"):
            try:
                return buf[8::].decode()
            except:
                logger.warning("Received invalid peerhash - could not parse")
                logger.warning(f"Received: {buf}")
                return None
        logger.warning(
            "Received invalid peerhash - unexpected start of message")
        logger.warning(f"Received: {buf}")

    def __read_peerlist(self, buf):
        if buf.startswith(b"PEERLIST"):
            try:
                return json.loads(buf[8::].decode())
            except:
                logger.warning("Received invalid peerlist - could not parse")
                logger.warning(f"Received: {buf}")
                return None
        logger.warning(
            "Received invalid peerlist - unexpected start of message")
        logger.warning(f"Received: {buf}")
        return None


class BlockchainProtocol:
    def __init__(self, blockchain_service):
        self.blockchain_service = blockchain_service
        
    async def add_blockchain_protocol_support(self, msg, client_tup, pipe):
        if msg.startswith(b"BLOCK"):
            pass