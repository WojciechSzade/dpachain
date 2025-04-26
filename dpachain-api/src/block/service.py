import datetime
from typing import Annotated

from fastapi import File
from src.block.interfaces import IBlockManager
from src.block.models import Block

from src.block.interfaces import IBlockService


class BlockService(IBlockService):
    def __init__(self, block_manager: IBlockManager):
        self.block_manager = block_manager

    def drop_all_blocks(self):
        return self.block_manager.drop_all_blocks()

    def get_all_blocks(self):
        return self.block_manager.get_all_blocks()

    def get_block_by_hash(self, hash):
        return self.block_manager.get_block_by_hash(hash)

    def generate_genesis_block(self):
        self.block_manager.generate_genesis_block()
        return "Genesis block has been created"

    def calculate_pdf_hash(self, pdf_file):
        return Block.calculate_pdf_hash(pdf_file)
