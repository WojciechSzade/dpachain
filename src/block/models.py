import logging
import hashlib
from datetime import datetime

from pydantic import BaseModel, field_validator
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import PKCS1_v1_5
from Cryptodome.Hash import SHA256
import base64

from src.utils.utils import require_authorized
from src.block.errors import *


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
        block = Block(
            "None",  # previous_block
            0,  # _id
            "0",  # diploma_type
            "0",  # pdf_hash
            "0",  # authors
            "Genesis block - not a real diploma!",  # title
            "0",  # language
            "0",  # discipline
            0,  # is_defended
            datetime.min.date(),  # date_of_defense
            "0",  # university
            "0",  # faculty
            "0",  # supervisor
            "0",  # reviewer
            self.chain_version,  # chain_version
            self.sign_hash_with_private_key,  # signing_function
        )
        self.blocks.insert_one(block.dict)

    @require_authorized
    def create_new_block(self, diploma_type: str, pdf_hash: str, authors: (list[str] | str), title: str, language: str, discipline: str, is_defended: int, date_of_defense: datetime.date, university: str, faculty: str, supervisor: (list[str] | str), reviewer: (list[str] | str), additional_info: (str | None) = None):
        previous_block = self.get_latest_block()['hash']
        _id = self.get_latest_block()['_id'] + 1
        block = Block(
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
        return self.blocks.find_one(sort=[("_id", -1)])

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


class Block():
    def __init__(self, previous_block: str, _id: int, diploma_type: str, pdf_hash: str, authors: (list[str] | str), title: str, language: str, discipline: str, is_defended: int, date_of_defense: datetime.date, university: str, faculty: str, supervisor: (list[str] | str), reviewer: (list[str] | str), chain_version: str, signing_function: callable, additional_info: (str | None) = None):
        self.previous_block = previous_block
        self._id = _id
        self.timestamp = datetime.now().timestamp()
        self.diploma_type = diploma_type
        self.pdf_hash = pdf_hash
        self.author = authors
        self.date_of_defense = datetime.combine(
            date_of_defense, datetime.min.time())
        self.title = title
        self.language = language
        self.discipline = discipline
        self.is_defended = is_defended
        self.university = university
        self.faculty = faculty
        self.supervisor = supervisor
        self.reviewer = reviewer
        self.additional_info = additional_info
        self.chain_version = chain_version
        self.hash = self.calculate_merkle_root([
            self.previous_block,
            self._id,
            self.timestamp,
            self.diploma_type,
            self.pdf_hash,
            self.author,
            self.date_of_defense,
            self.title,
            self.language,
            self.discipline,
            self.is_defended,
            self.university,
            self.faculty,
            self.supervisor,
            self.reviewer,
            self.additional_info,
            self.chain_version
        ])
        self.signed_hash = signing_function(self.hash)

    @staticmethod
    def calculate_merkle_root(data):
        def _hash_pair(a, b):
            sum = (str(a) + str(b)).encode()

            hash_string = hashlib.sha256(sum).hexdigest()
            return hash_string

        if len(data) == 1:
            return data[0]

        hash_list = []

        for i in range(0, len(data) - 1, 2):
            hash_list.append(_hash_pair(data[i], data[i + 1]))

        if len(data) % 2 == 1:
            hash_list.append(_hash_pair(data[-1], data[-1]))

        return Block.calculate_merkle_root(hash_list)

    @staticmethod
    def calculate_pdf_hash(pdf_file):
        return hashlib.sha256(pdf_file).hexdigest()

    @property
    def dict(self):
        return {
            "previous_block": self.previous_block,
            "_id": self._id,
            "timestamp": self.timestamp,
            "diploma_type": self.diploma_type,
            "pdf_hash": self.pdf_hash,
            "author": self.author,
            "date_of_defense": self.date_of_defense,
            "title": self.title,
            "language": self.language,
            "discipline": self.discipline,
            "is_defended": self.is_defended,
            "university": self.university,
            "faculty": self.faculty,
            "supervisor": self.supervisor,
            "reviewer": self.reviewer,
            "additional_info": self.additional_info,
            "chain_version": self.chain_version,
            "hash": self.hash,
            "signed_hash": self.signed_hash
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data["previous_block"],
            data["_id"],
            data["diploma_type"],
            data["pdf_hash"],
            data["author"],
            data["title"],
            data["language"],
            data["discipline"],
            data["is_defended"],
            data["date_of_defense"],
            data["university"],
            data["faculty"],
            data["supervisor"],
            data["reviewer"],
            data["chain_version"],
            data["signing_function"],
            data["additional_info"]
        )
