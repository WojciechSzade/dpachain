from fastapi import Request


def check_if_service_started(request: Request):
    def wrapper():
        if not request.app.state.service_started:
            raise Exception("Service is not started")


@check_if_service_started
def get_blockchain_service(request: Request):
    return request.app.state.blockchain


@check_if_service_started
def get_block_service(request: Request):
    return request.app.state.blockchain.block_service


@check_if_service_started
def get_peer_service(request: Request):
    return request.app.state.blockchain.peer_service


@check_if_service_started
def get_node_service(request: Request):
    return request.app.state.blockchain.node_service
