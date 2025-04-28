from src.core.db import init_db
from src.node.service import NodeService
from src.node.manager import NodeManager
from src.node.interfaces import INodeManager, INodeService
from src.block.service import BlockService
from src.block.manager import BlockManager
from src.block.interfaces import IBlockManager, IBlockService
from src.peer.service import PeerService
from src.peer.manager import PeerManager
from src.peer.interfaces import IPeerManager, IPeerService
from src.api.routers import router
from src.core.config import settings
from fastapi import FastAPI
from typing import Any
from contextlib import asynccontextmanager
import uvicorn
import asyncio
import uvloop


def configure_dependencies() -> dict[str, Any]:
    client_db = init_db(mongodb_url=settings.MONGODB_URL)
    db = client_db.blockchain
    block_manager: IBlockManager = BlockManager(
        database=db, network_id=settings.NETWORK_ID, chain_version=settings.CHAIN_VERSION, authorized=settings.AUTHORIZED, generating_private_key=settings.GENERATING_PRIVATE_KEY, university_name=settings.UNIVERSITY_NAME)
    peer_manager: IPeerManager = PeerManager(
        client_db=db, authorized=settings.AUTHORIZED, signing_public_key=settings.SIGNING_PUBLIC_KEY)
    node_manager: INodeManager = NodeManager(
        nickname=settings.HOST_NODE_NAME, port=settings.P2P_PORT, private_signing_key=settings.SIGNING_PRIVATE_KEY)

    block_manager.set_peer_manager(peer_manager=peer_manager)
    node_manager.set_block_manager(block_manager=block_manager)
    node_manager.set_peer_manager(peer_manager=peer_manager)

    block_service: IBlockService = BlockService(block_manager=block_manager)
    peer_service: IPeerService = PeerService(peer_manager=peer_manager)
    node_service: INodeService = NodeService(node_manager=node_manager)

    return {
        "block_manager": block_manager,
        "peer_manager": peer_manager,
        "node_manager": node_manager,
        "block_service": block_service,
        "peer_service": peer_service,
        "node_service": node_service
    }


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.block_service = None
    app.state.peer_service = None
    app.state.node_service = None
    app.state.service_started = False
    yield

app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
)
fastapi_serv_task = None

app.include_router(router)


async def entry():
    config = uvicorn.Config(app, host=settings.HOST,
                            port=settings.PORT, loop=uvloop.EventLoopPolicy())
    server = uvicorn.Server(config)

    fastapi_serv_task = asyncio.ensure_future(server.serve())

    container = configure_dependencies()
    await container["node_manager"].start()
    app.state.block_service = container["block_service"]
    app.state.peer_service = container["peer_service"]
    app.state.node_service = container["node_service"]
    app.state.service_started = True

    close_signal = asyncio.Event()
    await close_signal.wait()
    await app.state.node.stop()

asyncio.run(entry())
