from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
import asyncio

from src.core.db import init_db
from src.core.models import BlockManager
from src.core.config import settings
from src.api.routers import router
from src.peer.nodes import NodeService
from src.peer.peers import PeersManager
from src.core.main import BlockchainManager

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.database_client = init_db(settings.MONGODB_URL)
    app.state.blockchain = BlockManager(app.state.database_client, settings.NETWORK_ID, settings.CHAIN_VERSION, settings.AUTHORIZED, settings.SIGNING_PRIVATE_KEY if settings.AUTHORIZED else None)
    yield

app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
)
fastapi_serv_task = None

def get_blockchain():
    return app.state.blockchain

app.include_router(router)

async def entry():
    config = uvicorn.Config(app, host=settings.HOST, port=settings.PORT)
    server = uvicorn.Server(config)
    
    fastapi_serv_task = asyncio.ensure_future(server.serve())
    
    blockchain_manager = BlockchainManager(settings.MONGODB_URL, settings.AUTHORIZED, settings.SIGNING_PUBLIC_KEY, settings.SIGNING_PRIVATE_KEY, settings.NETWORK_ID, settings.HOST_NODE_NAME, settings.CHAIN_VERSION)
    await blockchain_manager.node_service.start(settings.P2P_PORT)
    
    close_signal = asyncio.Event()
    await close_signal.wait()
    await app.state.node.stop()
        
asyncio.run(entry())
