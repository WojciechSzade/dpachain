class NodeService:
    def __init__(self, node_manager):
        self.node_manager = node_manager

    def start_node_service(self, port):
        return self.node_manager.start(port)

    def sync_chain(self):
        return self.node_manager.sync_chain()

    def stop_node_service(self):
        return self.node_manager.stop()
