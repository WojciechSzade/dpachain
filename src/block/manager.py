import logging
from datetime import datetime

from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import PKCS1_v1_5
from Cryptodome.Hash import SHA256
import base64

from src.utils.utils import require_authorized
from src.block.errors import *
from src.block.models import Block


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BlockManager:
    def __init__(self, database, network_id, chain_version, authorized, signing_private_key=None):
        self.db = database.blockchain
        self.network_id = network_id
        self.chain_version = chain_version
        self.blocks = self.db.blocks
        self.transactions = []
        self.authorized = authorized
        if self.authorized:
            if signing_private_key is None:
                raise ValueError(
                    "signing_private_key is required for authorized blockchain service")
            self.signing_private_key = RSA.import_key(signing_private_key)

    @require_authorized
    def generate_genesis_block(self):
        if self.blocks.count_documents({}) > 0:
            raise BlockAlreadyExistsError(
                "genesis block", "Could not generate genesis block, because it already exists"
            )
        block = Block.create_block(
            None,
            0,
            "0",
            "0",
            "0",
            "Genesis block - not a real diploma!",
            "0",
            "0",
            0,
            datetime.min.date(),
            "0",
            "0",
            "0",
            "0",
            self.chain_version,
            self.sign_hash_with_private_key
        )
        logger.info(f"Genesis block - {block}")
        self.blocks.insert_one(block.dict)

    @require_authorized
    def create_new_block(self, diploma_type: str, pdf_hash: str, authors: (list[str] | str), title: str, language: str, discipline: str, is_defended: int, date_of_defense: datetime.date, university: str, faculty: str, supervisor: (list[str] | str), reviewer: (list[str] | str), additional_info: (str | None) = None):
        previous_block = self.get_latest_block()['hash']
        _id = self.get_latest_block()['_id'] + 1
        block = Block.create_block(
            previous_block,
            _id,
            diploma_type,
            pdf_hash,
            authors,
            title,
            language,
            discipline,
            is_defended,
            date_of_defense,
            university,
            faculty,
            supervisor,
            reviewer,
            self.chain_version,
            self.sign_hash_with_private_key,
            additional_info
        )
        try:
            self.blocks.insert_one(block.dict)
        except Exception as e:
            logger.error(f"Failed to insert block: {e}")
            raise e

    def get_latest_block(self):
        # return Block.from_dict(self.blocks.find_one(sort=[('_id', -1)]))
        b = self.blocks.find_one(sort=[('_id', -1)])
        logger.info(f"Latest block: {b}")
        block = Block.from_dict(b)
        logger.info(f"Latest block from block {block}")
        return block

    def get_all_blocks(self):
        return list(self.blocks.find())

    @require_authorized
    def sign_hash_with_private_key(self, hash):
        encrypted_hash = SHA256.new(hash.encode('utf-8'))
        signature = PKCS1_v1_5.new(
            self.signing_private_key).sign(encrypted_hash)
        result = base64.b64encode(signature).decode()
        return result

    def drop_all_blocks(self):
        self.blocks.delete_many({})

    def get_chain_size(self):
        return self.blocks.count_documents({})

    def get_block_by_index(self, index):
        return Block.from_dict(self.blocks.find_one({"_id": index}))

    def add_block(self, block):
        self.blocks.insert_one(block.dict)
