from fastapi import Request
from src.core.models import Blockchain

def get_blockchain(request: Request) -> Blockchain:
    return request.app.state.blockchain