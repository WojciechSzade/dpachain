from fastapi import HTTPException, Request, status

from src.block.service import BlockService


def get_blockchain_service(request: Request):
    return request.app.state.blockchain


def get_block_service(request: Request) -> BlockService:
    try:
        return request.app.state.blockchain.block_service
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Block service was not started yet",
        )


def get_peer_service(request: Request):
    try:
        return request.app.state.blockchain.peer_service
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Peer service was not started yet",
        )


def get_node_service(request: Request):
    try:
        return request.app.state.blockchain.node_service
    except:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Node service was not started yet",
        )
