import logging 
import uvicorn
import asyncio
from src.peer.nodes import NodeService, PeersManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)



async def entry():
    node_service = NodeService(PeersManager("peer/nodes.txt"), "node1")
    await node_service.start(5000)
    await node_service.peer_list_protocol.send_peerlist(node_service.pipes[0])
    await node_service.peer_list_protocol.send_peerhash(node_service.pipes[0])
    
    close_signal = asyncio.Event()
    await close_signal.wait()
    await node_service.stop()

loop = asyncio.get_event_loop()
loop.run_until_complete(entry())
