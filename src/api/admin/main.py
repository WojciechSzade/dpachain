import logging

from fastapi import APIRouter, Depends
from typing import Annotated
import datetime
from fastapi import File


from src.block.service import BlockService
from src.node.service import NodeService
from src.peer.service import PeerService
from src.utils.dependencies import get_block_service, get_node_service, get_peer_service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/admin/drop_all_blocks")
def drop_all_blocks(block_service: BlockService = Depends(get_block_service)):
    try:
        block_service.drop_all_blocks()
        return {"message": "All blocks have been dropped!"}
    except Exception as e:
        return {"message": f"Failed to drop blocks: {str(e)}"}


@router.get("/admin/generate_genesis_block")
def generate_genesis_block(block_service: BlockService = Depends(get_block_service)):
    block_service.generate_genesis_block()
    return {"message": "Genesis block has been generated!"}


@router.post("/create_new_block")
def generate_next_block(diploma_type: str, pdf_file: Annotated[bytes, File()], authors: (list[str] | str), title: str, language: str, discipline: str, is_defended: int, date_of_defense: datetime.date, university: str, faculty: str, supervisor: (list[str] | str), reviewer: (list[str] | str), additional_info: (str | None) = None, block_service: BlockService = Depends(get_block_service)):
    pdf_hash = block_service.calculate_pdf_hash(pdf_file)
    try:
        block_service.create_new_block(diploma_type, pdf_hash, authors, title, language, discipline,
                                       is_defended, date_of_defense, university, faculty, supervisor, reviewer, additional_info)
    except Exception as e:
        return {"message": f"Failed to create block: {e}"}
    return {"message": "Block has been generated!"}


@router.post("/admin/add_new_authorized_peer")
def add_new_authorized_peer(nickname: str, public_key: str, adress: str = None, peer_service: PeerService = Depends(get_peer_service)):
    peer_service.add_new_peer(nickname, adress, True, public_key)
    return {"message": "Peer has been added!"}


@router.post("/admin/add_new_peer")
def add_new_authorized_peer(nickname: str, adress: str = None, peer_service: PeerService = Depends(get_peer_service)):
    peer_service.add_new_peer(nickname, adress, False)
    return {"message": "Peer has been added!"}


@router.get("/admin/get_peers_list")
def get_peers_list(peer_service: PeerService = Depends(get_peer_service)):
    return peer_service.get_peers_list()


@router.post("/admin/remove_peer")
def remove_peer(nickname: str, peer_service: PeerService = Depends(get_peer_service)):
    msg = peer_service.remove_peer(nickname)
    if msg is None:
        return {"message": "Peer has been removed!"}
    return {"message": msg}


@router.post("/admin/ban_peer")
def ban_peer(nickname: str, peer_service: PeerService = Depends(get_peer_service)):
    peer_service.ban_peer(nickname)
    return {"message": "Peer has been banned!"}


@router.post("/admin/unban_peer")
def unban_peer(nickname: str, peer_service: PeerService = Depends(get_peer_service)):
    peer_service.unban_peer(nickname)
    return {"message": "Peer has been unbanned!"}


@router.post("/admin/sync_chain")
async def sync_chain(node_service: NodeService = Depends(get_node_service)):
    logger.info("Syncing chain...")
    try:
        await node_service.sync_chain()
        return {"message": "Chain has been synced!"}
    except Exception as e:
        # return {"message": f"Failed to sync chain: {e}"}
        raise e


@router.post("/admin/change_node_nickname")
async def change_node_nickname(nickname: str, node_service: NodeService = Depends(get_node_service)):
    try:
        await node_service.change_node_nickname(nickname)
        return {"message": "Node nickname has been changed!"}
    except Exception as e:
        return {"message": f"Failed to change node nickname: {e}"}


@router.post("/admin/present_to_peer")
async def present_to_peer(nickname: str, node_service: NodeService = Depends(get_node_service)):
    try:
        await node_service.present_to_peer(nickname)
        return {"message": "Node has been presented to peer!"}
    except Exception as e:
        return {"message": f"Failed to present node to peer: {e}"}


@router.post("/admin/ask_peer_to_sync")
async def ask_peer_to_sync(nickname: str, node_service: NodeService = Depends(get_node_service)):
    try:
        await node_service.ask_peer_to_sync(nickname)
        return {"message": "Node has been asked to sync!"}
    except Exception as e:
        return {"message": f"Failed to ask peer to sync: {e}"}
