import logging
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PeerListProtocol:
    def __init__(self, peers_manager):
        self.peers_manager = peers_manager

    async def add_peer_protocole_support(self, msg, client_tup, pipe):
        if b"PEERLIST" == msg[:8]:
            peerlist = self._read_peerlist(msg)
            logger.info(f"Received PEERLIST message from {client_tup}")
            logger.info(f"Peerlist: {peerlist}")
            await pipe.send(b"PEERRECEIVED")
        elif b"PEERHASH" == msg[:8]:
            peerhash = self._read_peerhash(msg)
            logger.info(f"Received PEERHASH message from {client_tup}")
            logger.info(f"Peerhash: {peerhash}")
            await pipe.send(b"HASHRECEIVED")

    
    async def send_peerlist(self, pipe):
        peerlist = self.peers_manager.get_active_peers()
        msg = json.dumps(peerlist).encode()
        logger.info(f"Sending PEERLIST message to {pipe}")
        await pipe.send(b"PEERLIST" + msg + b"ENDLIST")
        buf = await pipe.recv()
        if buf != b"PEERRECEIVED":
            logger.warning(f"Failed to send peerlist to {pipe}")
        
    async def send_peerhash(self, pipe):
        peerhash = self.peers_manager.get_peerlist_hash()
        msg = peerhash.encode()
        logger.info(f"Sending PEERHASH message to {pipe}")
        await pipe.send(b"PEERHASH" + msg + b"ENDHASH")
        buf = await pipe.recv()
        if buf != b"HASHRECEIVED":
            logger.warning(f"Failed to send peerhash to {pipe}")
        
    def _read_peerlist(self, msg):
        if msg[-1:-7] != b"ENDLIST":
            logger.warning("Invalid PEERLIST message")
        json_message = msg[8:-7].decode()
        return json_message
    
    def _read_peerhash(self, msg):
        if msg[-1:-7] != b"ENDHASH":
            logger.warning("Invalid PEERHASH message")
        json_message = msg[8:-7].decode()
        return json_message
