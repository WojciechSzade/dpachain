import logging

from fastapi import APIRouter, Depends
from typing import Annotated
import datetime
from fastapi import File


from src.block.errors import BlockError
from src.block.service import BlockService
from src.node.errors import NodeError
from src.node.manager import NodeManager
from src.node.service import NodeService
from src.peer.errors import PeerError
from src.peer.service import PeerService
from src.utils.dependencies import get_block_service, get_node_service, get_peer_service
from src.api.utils import handle_error

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/staff/generate_new_block")
async def generate_next_block(diploma_type: str, pdf_file: Annotated[bytes, File()], authors: (list[str] | str), title: str, language: str, discipline: str, is_defended: int, date_of_defense: datetime.date, university: str, faculty: str, supervisor: (list[str] | str), reviewer: (list[str] | str), additional_info: (str | None) = None, node_service: NodeService = Depends(get_node_service)):
    try:
        return {"message": await node_service.generate_new_block(diploma_type, pdf_file, authors,
                                                                 title, language, discipline, is_defended, date_of_defense,
                                                                 university, faculty, supervisor, reviewer,
                                                                 additional_info=None)}
    except (PeerError, NodeError, BlockError) as e:
        return handle_error(e)


@router.get("/staff/get_all_blocks")
async def get_all_blocks(block_service: BlockService = Depends(get_block_service)):
    try:
        return {"blocks": block_service.get_all_blocks()}
    except BlockError as e:
        return handle_error(e)
