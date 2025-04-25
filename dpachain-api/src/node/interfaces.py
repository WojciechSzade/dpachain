from __future__ import annotations
from abc import ABC, abstractmethod
import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.block.interfaces import IBlockManager
    from src.peer.interfaces import IPeerManager


class INodeManager(ABC):
    """NodeManager is used to manage all the operations that uses the Node to exchange communication."""
    @abstractmethod
    def __init__(self, nickname: str, port: int):
        ...

    @abstractmethod
    def set_block_manager(self, block_manager: IBlockManager):
        """Lazy dependency injection."""
        ...

    @abstractmethod
    def set_peer_manager(self, peer_manager: IPeerManager):
        """Lazy dependency injection."""
        ...

    @abstractmethod
    async def start(self):
        """Starts the node."""
        ...

    @abstractmethod
    async def stop(self):
        """Stops the node from running."""
        ...

    @abstractmethod
    async def sync_chain(self):
        """Starts the syncing with other nodes."""
        ...

    @abstractmethod
    def select_best_peers(self, responses):
        """Returns peers sorted by given criteria"""
        ...

    @abstractmethod
    async def change_node_nickname(self, nickname: str):
        ...

    @abstractmethod
    async def present_to_peer(self, nickname: str):
        """Sends a message asking to be added to the peers list of another node."""
        ...

    @abstractmethod
    async def ask_peer_to_sync(self, nickname: str):
        """Ask a peer to sync it's chain."""
        ...

    @abstractmethod
    async def generate_new_block(self, diploma_type: str, pdf_file: bytes, authors: (list[str] | str), authors_id: (list[str] | str),  title: str, language: str, discipline: str, is_defended: int, date_of_defense: datetime.date, university: str, faculty: str, supervisor: (list[str] | str), reviewer: (list[str] | str), additional_info: (str | None) = None):
        """Creates and spreads a new block."""
        ...

    @abstractmethod
    async def connect_to_peer(self, peer):
        """Establishes a conenction with a peer, returns the pipe."""
        ...

    @abstractmethod
    async def check_if_block_was_added_sucessfully(self, block, best_peers_list):
        """Asks given peers if a given block exists in their chain."""
        ...


class INodeService(ABC):
    """Service class to be used as a proxy between the API and NodeManager, with some neccessary improvments, for the API"""
    @abstractmethod
    def __init__(self, node_manager: INodeManager):
        ...

    @abstractmethod
    async def sync_chain(self):
        ...

    @abstractmethod
    def stop_node_service(self):
        ...

    @abstractmethod
    async def change_node_nickname(self, nickname: str):
        ...

    @abstractmethod
    async def present_to_peer(self, nickname: str):
        ...

    @abstractmethod
    async def ask_peer_to_sync(self, nickname):
        ...

    @abstractmethod
    async def generate_new_block(self, *args):
        ...
