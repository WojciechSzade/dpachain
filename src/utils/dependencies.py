from fastapi import Request

def get_blockchain(request: Request):
    return request.app.state.blockchain

def get_node_service(request: Request):
    return request.app.state.node

def get_database_client():
    from src.main import database_client
    return database_client