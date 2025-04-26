from fastapi import HTTPException, Request, status

from src.block.interfaces import IBlockService
from src.peer.interfaces import IPeerService
from src.node.interfaces import INodeService


def get_block_service(request: Request) -> IBlockService:
    if request.app.state.service_started:
        return request.app.state.block_service
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Block service was not started yet",
        )


def get_peer_service(request: Request) -> IPeerService:
    if request.app.state.service_started:
        return request.app.state.peer_service
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Peer service was not started yet",
        )


def get_node_service(request: Request) -> INodeService:
    if request.app.state.service_started:
        return request.app.state.node_service
    else:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Node service was not started yet",
        )
