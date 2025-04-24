from datetime import datetime
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

    async def present_to_peer(self, nickname):
        return await self.node_manager.present_to_peer(nickname)

    async def ask_peer_to_sync(self, nickname):
        return await self.node_manager.ask_peer_to_sync(nickname)

    async def generate_new_block(self, diploma_type: str, pdf_file: str, authors: (list[str] | str), authors_id: (list[str] | str), title: str, language: str, discipline: str, is_defended: int, date_of_defense: datetime.date, university: str, faculty: str, supervisor: (list[str] | str), reviewer: (list[str] | str), additional_info: (str | None) = None):
        return "Block has been added", await self.node_manager.generate_new_block(diploma_type, pdf_file, authors, authors_id,
                                                                                  title, language, discipline, is_defended, date_of_defense,
                                                                                  university, faculty, supervisor, reviewer,
                                                                                  additional_info=None)
