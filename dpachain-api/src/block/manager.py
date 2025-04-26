import logging
import datetime

from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import pss
from Cryptodome.Hash import SHA256
import base64

from src.peer.interfaces import IPeerManager
from src.node.interfaces import INodeManager

from src.utils.utils import require_authorized
from src.block.errors import *
from src.block.models import Block
from src.block.interfaces import IBlockManager


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BlockManager(IBlockManager):
    def __init__(self, database, network_id: str, chain_version: str, authorized: bool, signing_private_key):
        self.db = database.blockchain
        self.blocks = self.db.blocks
        self.network_id = network_id
        self.chain_version = chain_version
        self.authorized = authorized
        self.peer_manager: IPeerManager
        self.signing_private_key = RSA.import_key(signing_private_key)

    def set_peer_manager(self, peer_manager: IPeerManager):
        self.peer_manager = peer_manager

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
            "0",
            "Genesis block - not a real diploma!",
            "0",
            "0",
            0,
            datetime.datetime.min.date(),
            "0",
            "0",
            "0",
            "0",
            self.peer_manager.get_own_peer_name(),
            self.chain_version,
            self._sign_hash_with_private_key
        )
        logger.info(f"Genesis block - {block}")
        self.blocks.insert_one(block.as_dict())

    @require_authorized
    def create_new_block(
            self, diploma_type: str, pdf_file: bytes, authors: (list[str] | str), authors_id: (list[str] | str),
            title: str, language: str, discipline: str, is_defended: int, date_of_defense: datetime.date,
            university: str, faculty: str, supervisor: (list[str] | str), reviewer: (list[str] | str),
            additional_info: (str | None) = None):
        last_block = self.get_last_block()
        if last_block is None:
            raise BlockNotFoundError(
                "genesis block", "Could not create new block, because there are no blocks in the chain"
            )
        previous_block = last_block.hash
        _id = last_block._id + 1
        pdf_hash = Block.calculate_pdf_hash(pdf_file)
        block = Block.create_block(previous_block=previous_block, _id=_id, diploma_type=diploma_type,
                                   pdf_hash=pdf_hash, authors=authors, authors_id=authors_id, title=title,
                                   language=language, discipline=discipline, is_defended=is_defended,
                                   date_of_defense=date_of_defense, university=university, faculty=faculty,
                                   supervisor=supervisor, reviewer=reviewer, peer_author=self.peer_manager.get_own_peer_name(),
                                   chain_version=self.chain_version, signing_function=self._sign_hash_with_private_key,
                                   additional_info=additional_info)
        try:
            self.blocks.insert_one(block.as_dict())
        except Exception as e:
            logger.error(f"Failed to insert block: {e}")
            raise e
        return block

    def get_last_block(self):
        if self.blocks.count_documents({}) < 1:
            raise BlockNotFoundError("latest", "No blocks in the database.")
        return Block.from_dict(self.blocks.find_one(sort=[('_id', -1)]))

    def get_all_blocks(self):
        return [Block.from_dict(block) for block in self.blocks.find(sort=[('_id', 1)])] if self.blocks.count_documents({}) > 0 else []

    @require_authorized
    def _sign_hash_with_private_key(self, hash):
        encrypted_hash = SHA256.new(hash.encode('utf-8'))
        signature = pss.new(self.signing_private_key).sign(encrypted_hash)
        result = base64.b64encode(signature).decode()
        return result

    def drop_all_blocks(self):
        self.blocks.delete_many({})

    def get_chain_size(self):
        return self.blocks.count_documents({})

    def get_block_by_index(self, index: int):
        return Block.from_dict(self.blocks.find_one({"_id": index}))

    def get_block_by_hash(self, hash: str):
        block = self.blocks.find_one({"hash": hash})
        if not block:
            raise BlockNotFoundError(hash)
        return Block.from_dict(block)

    def add_block(self, block: Block):
        try:
            self.validate_block(block)
        except UnauthorizedBlockError as e:
            logger.error(f"Failed to validate block: {e}")
            raise e
        self.blocks.insert_one(block.as_dict())
        return block

    def validate_block(self, block):
        previous_block = self.get_block_by_index(
            block._id - 1) if block._id > 0 else None
        if previous_block is None and block._id != 0:
            raise UnauthorizedBlockError(
                block, "Could not validate block, because previous block does not exist"
            )

        if previous_block and previous_block.hash != block.previous_block:
            raise UnauthorizedBlockError(
                block, "Could not validate block, because previous block hash does not match"
            )
        author_peer = self.peer_manager.get_peer_by_nickname(
            block.peer_author)
        if author_peer is None:
            raise UnauthorizedBlockError(
                block, "Could not validate block, because author peer does not exist"
            )
        if block.hash != Block.calculate_merkle_root([previous_block.hash if previous_block else None, block._id, block.timestamp, block.diploma_type, block.pdf_hash, block.authors, block.authors_id, block.date_of_defense, block.title, block.language, block.discipline, block.is_defended, block.university, block.faculty, block.supervisor, block.reviewer, block.additional_info, block.peer_author, block.chain_version]):
            raise UnauthorizedBlockError(
                block, "Could not validate block, because hash does not match - calculated hash does not match"
            )
        public_key = RSA.import_key(author_peer.public_key)
        verifier = pss.new(public_key)
        if not verifier.verify(SHA256.new(block.hash.encode('utf-8')), base64.b64decode(block.signed_hash)):
            raise UnauthorizedBlockError(
                block, "Could not validate block, because hash signed (with author's key) does not match"
            )

    def remove_block(self, index):
        block = self.get_block_by_index(index)
        if block is None:
            raise BlockNotFoundError(
                index, "Could not remove block, because it does not exist"
            )
        if block._id != self.get_chain_size() - 1:
            raise CouldNotRemoveBlockError(
                block, "Could not remove block, because it is not the last block in the chain")
        self.blocks.delete_one({"_id": index})
        return block

    def compare_blocks(self, block1, block2):
        return block1.as_dict() == block2.as_dict()
