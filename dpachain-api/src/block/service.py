from src.block.errors import BlockAlreadyExistsError
from src.block.manager import BlockManager
from src.block.models import Block


class BlockService:
    def __init__(self, block_manager: BlockManager):
        self.block_manager = block_manager

    def drop_all_blocks(self):
        try:
            return self.block_manager.drop_all_blocks()
        except Exception as e:
            return str(e)

    def get_latest_block(self):
        return self.block_manager.get_latest_block().dict

    def get_all_blocks(self):
        return self.block_manager.get_all_blocks()
    
    def get_block_by_hash(self, hash):
        return self.block_manager.get_block_by_hash(hash)

    def generate_genesis_block(self):
        self.block_manager.generate_genesis_block()
        return "Genesis block has been created"

    def create_new_block(self, diploma_type, pdf_hash, authors, authors_id, title, language, discipline, is_defended, date_of_defense, university, faculty, supervisor, reviewer, additional_info=None):
        return self.block_manager.create_new_block(diploma_type, pdf_hash, authors, authors_id, title, language, discipline, is_defended, date_of_defense, university, faculty, supervisor, reviewer, additional_info)

    def calculate_pdf_hash(self, pdf_file):
        try:
            return Block.calculate_pdf_hash(pdf_file)
        except Exception as e:
            return str(e)
