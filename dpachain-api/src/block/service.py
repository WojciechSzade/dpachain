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

    def get_latest_block(self):
        return self.block_manager.get_last_block().as_dict()

    def get_all_blocks(self):
        return self.block_manager.get_all_blocks()

    def get_block_by_hash(self, hash):
        return self.block_manager.get_block_by_hash(hash)

    def generate_genesis_block(self):
        self.block_manager.generate_genesis_block()
        return "Genesis block has been created"

    def create_new_block(
        self, diploma_type: str, pdf_file: Annotated[bytes, File()],
            authors: (list[str] | str), authors_id: (list[str] | str),
            title: str, language: str, discipline: str, is_defended: int,
            date_of_defense: datetime.date, university: str, faculty: str,
            supervisor: (list[str] | str), reviewer: (list[str] | str),
            additional_info: (str | None) = None):
        return self.block_manager.create_new_block(diploma_type, pdf_file, authors, authors_id, title, language, discipline, is_defended, date_of_defense, university, faculty, supervisor, reviewer, additional_info)

    def calculate_pdf_hash(self, pdf_file):
        return Block.calculate_pdf_hash(pdf_file)
