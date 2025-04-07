from contextlib import asynccontextmanager
from fastapi import FastAPI
import uvicorn
import asyncio

from src.core.config import settings
from src.api.routers import router
from src.core.main import BlockchainManager, BlockchainService


@asynccontextmanager
async def lifespan(app: FastAPI):
    # app.state.database_client = init_db(settings.MONGODB_URL)
    # app.state.blockchain = BlockchainManager(app.state.database_client, settings.NETWORK_ID, settings.CHAIN_VERSION, settings.AUTHORIZED, settings.SIGNING_PRIVATE_KEY if settings.AUTHORIZED else None)
    app.state.blockchain = None
    app.state.service_started = False
    yield

app = FastAPI(
    lifespan=lifespan,
    title=settings.PROJECT_NAME,
)
fastapi_serv_task = None

app.include_router(router)


async def entry():
    config = uvicorn.Config(app, host=settings.HOST, port=settings.PORT)
    server = uvicorn.Server(config)

    fastapi_serv_task = asyncio.ensure_future(server.serve())

    blockchain = BlockchainManager(settings.MONGODB_URL, settings.AUTHORIZED, settings.SIGNING_PUBLIC_KEY,
                                   settings.SIGNING_PRIVATE_KEY, settings.NETWORK_ID, settings.HOST_NODE_NAME, settings.CHAIN_VERSION)
    await blockchain.start_node_service(settings.P2P_PORT)
    app.state.blockchain = BlockchainService(blockchain)
    app.state.service_started = True

    close_signal = asyncio.Event()
    await close_signal.wait()
    await app.state.node.stop()

asyncio.run(entry())
