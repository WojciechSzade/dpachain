from fastapi import Request
from src.core.models import BlockchainService

def get_blockchain(request: Request) -> BlockchainService:
    return request.app.state.blockchain