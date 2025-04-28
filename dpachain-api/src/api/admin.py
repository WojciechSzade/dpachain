import logging

from fastapi import APIRouter, Depends
from typing import Annotated, Optional
import datetime
from fastapi import File


from src.block.errors import BlockError
from src.block.interfaces import IBlockService
from src.node.errors import NodeError
from src.node.interfaces import INodeService
from src.peer.interfaces import IPeerService
from src.utils.dependencies import get_block_service, get_node_service, get_peer_service
from src.api.utils import handle_error

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/admin/add_new_authorized_peer")
def add_new_authorized_peer(nickname: str, public_key: str, adress: Optional[str] = None, peer_service: IPeerService = Depends(get_peer_service)):
    try:
        res = peer_service.add_new_peer(nickname, public_key, adress, True)
        return {"message": res[0], "peer": res[1]}
    except Exception as e:
        return handle_error(e)


@router.post("/admin/add_new_peer")
def add_new_peer(nickname: str, public_key: str, adress: Optional[str] = None, peer_service: IPeerService = Depends(get_peer_service)):
    try:
        res = peer_service.add_new_peer(nickname, public_key, adress, False)
        return {"message": res[0], "peer": res[1]}
    except Exception as e:
        return handle_error(e)


@router.get("/admin/get_peers_list")
def get_peers_list(peer_service: IPeerService = Depends(get_peer_service)):
    try:
        return {
            "peers": peer_service.get_peers_list()
        }
    except Exception as e:
        return handle_error(e)


@router.post("/admin/remove_peer")
def remove_peer(nickname: str, peer_service: IPeerService = Depends(get_peer_service)):
    try:
        return {"message": peer_service.remove_peer(nickname)}
    except Exception as e:
        return handle_error(e)


@router.post("/admin/ban_peer")
def ban_peer(nickname: str, peer_service: IPeerService = Depends(get_peer_service)):
    try:
        return {"message": peer_service.ban_peer(nickname)}
    except Exception as e:
        return handle_error(e)


@router.post("/admin/unban_peer")
def unban_peer(nickname: str, peer_service: IPeerService = Depends(get_peer_service)):
    try:
        return {"message": peer_service.unban_peer(nickname)}
    except Exception as e:
        return handle_error(e)


@router.post("/admin/sync_chain")
async def sync_chain(node_service: INodeService = Depends(get_node_service)):
    logger.info("Syncing chain...")
    try:
        return await node_service.sync_chain()
    except (Exception, NodeError, BlockError) as e:
        return handle_error(e)


@router.post("/admin/present_to_peer")
async def present_to_peer(nickname: str, node_service: INodeService = Depends(get_node_service)):
    try:
        await node_service.present_to_peer(nickname)
        return {"message": "Node has been presented to peer!"}
    except Exception as e:
        return handle_error(e)


@router.post("/admin/ask_peer_to_sync")
async def ask_peer_to_sync(nickname: str, node_service: INodeService = Depends(get_node_service)):
    try:
        await node_service.ask_peer_to_sync(nickname)
        return {"message": "Node has been asked to sync!"}
    except Exception as e:
        return handle_error(e)


@router.post("/admin/drop_all_blocks")
def drop_all_blocks(block_service: IBlockService = Depends(get_block_service)):
    try:
        block_service.drop_all_blocks()
        return {"message": "All blocks have been dropped!"}
    except Exception as e:
        return handle_error(e)


@router.get("/admin/generate_genesis_block")
def generate_genesis_block(block_service: IBlockService = Depends(get_block_service)):
    try:
        return {"message": block_service.generate_genesis_block()}
    except BlockError as e:
        return handle_error(e)


@router.post("/admin/change_node_nickname")
async def change_node_nickname(nickname: str, node_service: INodeService = Depends(get_node_service)):
    try:
        await node_service.change_node_nickname(nickname)
        return {"message": "Node nickname has been changed!"}
    except Exception as e:
        return handle_error(e)
