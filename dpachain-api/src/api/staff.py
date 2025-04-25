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
async def generate_next_block(
        diploma_type: str, pdf_file: Annotated[bytes, File()], authors: (list[str] | str),
        authors_id: (list[str] | str),  title: str, language: str, discipline: str,
        is_defended: int, date_of_defense: datetime.date, university: str, faculty: str,
        supervisor: (list[str] | str), reviewer: (list[str] | str),
        additional_info: (str | None) = None, node_service: NodeService = Depends(get_node_service)):
    try:
        res = await node_service.generate_new_block(
            diploma_type=diploma_type, pdf_file=pdf_file, authors=authors, authors_id=authors_id,
            title=title, language=language, discipline=discipline, is_defended=is_defended,
            date_of_defense=date_of_defense, university=university, faculty=faculty, supervisor=supervisor,
            reviewer=reviewer, additional_info=None)
        return {"message": res[0], "block": res[1]}
    except (PeerError, NodeError, BlockError) as e:
        return handle_error(e)


@router.get("/staff/get_all_blocks")
async def get_all_blocks(block_service: BlockService = Depends(get_block_service)):
    try:
        return {"blocks": block_service.get_all_blocks()}
    except BlockError as e:
        return handle_error(e)
