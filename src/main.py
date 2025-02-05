from fastapi import FastAPI
from contextlib import asynccontextmanager
import uvicorn
import asyncio

from src.core.db import init_db
from src.core.models import BlockchainService
from src.core.config import settings
from src.api.routers import router
from src.peer.nodes import NodeService, PeersManager

@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.database_client = init_db()
    app.state.blockchain = BlockchainService(app.state.database_client, settings.NETWORK_ID, settings.CHAIN_VERSION, settings.SIGNING_PRIVATE_KEY)
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
    config = uvicorn.Config(app)
    server = uvicorn.Server(config)
    
    fastapi_serv_task = asyncio.ensure_future(server.serve())
    
    app.state.node = NodeService(PeersManager(settings.NODES_LIST_FILE), settings.HOST_NODE_NAME)
    await app.state.node.start(settings.P2P_PORT)
    
    close_signal = asyncio.Event()
    await close_signal.wait()
    await app.state.node.stop()
        
asyncio.run(entry())
