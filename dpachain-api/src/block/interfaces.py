from __future__ import annotations
from abc import ABC, abstractmethod
import datetime
from typing import TYPE_CHECKING
from src.block.models import Block

if TYPE_CHECKING:
    from src.peer.interfaces import IPeerManager
    from src.node.interfaces import INodeManager


class IBlockManager(ABC):
    """BlockManager is used to manage all operations related to creating blocks and storing them in the database."""
    @abstractmethod
    def __init__(self, database, network_id: str, chain_version: str, authorized: bool, signing_private_key):
        ...

    @abstractmethod
    def set_peer_manager(self, peer_manager: IPeerManager):
        """Lazy dependency injection."""
        ...

    @abstractmethod
    def generate_genesis_block(self):
        """
        Creates the genesis block - the first block.
        This is a one time only action, and should not be executed
        in an existing enviroment - it will result in an orphan genesis block
        """
        ...

    @abstractmethod
    def create_new_block(
            self, diploma_type: str, pdf_file: bytes,
            authors: (list[str] | str), authors_id: (list[str] | str),
            title: str, language: str, discipline: str, is_defended: int,
            date_of_defense: datetime.date, university: str, faculty: str,
            supervisor: (list[str] | str), reviewer: (list[str] | str),
            additional_info: (str | None) = None):
        """
        Creates an instance of a block, that is then inserted to the database. 
        This method is only used as a helper and doesn't follow the whole procedure of generating a block.
        A block created by this method can be removed, if it didn't make it into the chain.
        """
        ...

    @abstractmethod
    def get_last_block(self):
        """Retrieve the last block from the chain."""
        ...

    @abstractmethod
    def get_all_blocks(self):
        ...

    @abstractmethod
    def drop_all_blocks(self):
        """
        Remove all the blocks from the database. 
        The chain can then by synced again, if the copy is avaiable on different nodes.
        """
        ...

    @abstractmethod
    def get_chain_size(self):
        ...

    @abstractmethod
    def get_block_by_index(self, index: int):
        """Retrieves block from the database by the _id field."""
        ...

    @abstractmethod
    def get_block_by_hash(self, hash: str):
        """Retrieves block from the database by the hash field."""
        ...

    @abstractmethod
    def add_block(self, block: Block):
        """Adds the passed block to the chain - if it's is valid"""
        ...

    @abstractmethod
    def validate_block(self, block):
        """Checks the validity of the block."""
        ...

    @abstractmethod
    def remove_block(self, index: int):
        """
        Removes block from the chain. 
        Only works for a block, that has not been yet published - hasn't been accepted in other chains.
        """
        ...

    @abstractmethod
    def compare_blocks(self, block1, block2):
        """Checks if two blocks are the same."""
        ...


class IBlockService(ABC):
    """Service class to be used as a proxy between the API and BlockManager, with some neccessary improvments, for the API"""
    @abstractmethod
    def __init__(self, block_manager: IBlockManager):
        ...

    @abstractmethod
    def drop_all_blocks(self):
        ...

    @abstractmethod
    def get_latest_block(self):
        ...

    @abstractmethod
    def get_all_blocks(self):
        ...

    @abstractmethod
    def get_block_by_hash(self, hash):
        ...

    @abstractmethod
    def generate_genesis_block(self):
        ...

    @abstractmethod
    def create_new_block(self, diploma_type, pdf_hash, authors, authors_id, title, language, discipline, is_defended, date_of_defense, university, faculty, supervisor, reviewer, additional_info=None):
        ...

    @abstractmethod
    def calculate_pdf_hash(self, pdf_file):
        ...
