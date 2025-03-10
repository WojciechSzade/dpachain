from src.node.manager import NodeManager


class NodeService:
    def __init__(self, node_manager: NodeManager):
        self.node_manager = node_manager

    async def start_node_service(self, port):
        return await self.node_manager.start(port)

    async def sync_chain(self):
        return await self.node_manager.sync_chain()

    def stop_node_service(self):
        return self.node_manager.stop()
        
    async def change_node_nickname(self, nickname):
        return await self.node_manager.change_node_nickname(nickname)
