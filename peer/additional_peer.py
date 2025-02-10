import logging 
import uvicorn
import asyncio
from src.peer.nodes import NodeService
from src.peer.peers import PeersManager
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



async def entry():
    peer_manager = PeersManager("peer/nodes.txt")
    node_service = NodeService(peer_manager, "node111")
    await node_service.start(5000)
    await node_service.connect_to_nodes()
    for pipe in node_service.pipes:
        pipe_peerhash = await node_service.protocol_manager.get_peerhash_from_pipe(pipe)
        logger.info(f"Peerhash from pipe: {pipe_peerhash}")
        own_peerhash = node_service.peers_manager.get_peerlist_hash()
        logger.info(f"Own peerhash: {own_peerhash}")            
        if pipe_peerhash != own_peerhash:
            time.sleep(5)
            logger.info("Peerhashes are different")
            pipe_peerlist = await node_service.protocol_manager.get_peerlist_from_pipe(pipe)
            if pipe_peerlist is None:
                continue
            logger.info(f"Peerlist from pipe: {pipe_peerlist}")
            node_service.peers_manager.parse_peer_list_message(pipe_peerlist)
            
    
    
    close_signal = asyncio.Event()
    await close_signal.wait()
    await node_service.stop()

loop = asyncio.get_event_loop()
loop.run_until_complete(entry())
