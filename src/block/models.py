import logging
import hashlib
from datetime import datetime

from src.block.errors import *


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Block:
    def __init__(self, previous_block, _id, timestamp, diploma_type, pdf_hash, author, date_of_defense, title, language, discipline, is_defended, university, faculty, supervisor, reviewer, additional_info, chain_version, hash, signed_hash):
        self.previous_block = previous_block
        self._id = _id
        self.timestamp = timestamp
        self.diploma_type = diploma_type
        self.pdf_hash = pdf_hash
        self.author = author
        self.date_of_defense = date_of_defense
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
        self.hash = hash
        self.signed_hash = signed_hash
        

    @classmethod
    def create_block(cls, previous_block: str, _id: int, diploma_type: str, pdf_hash: str, authors: (list[str] | str), title: str, language: str, discipline: str, is_defended: int, date_of_defense: datetime.date, university: str, faculty: str, supervisor: (list[str] | str), reviewer: (list[str] | str), chain_version: str, signing_function: callable, additional_info: (str | None) = None):
        logger.info(f"Creating block {title}")
        block = {}
        block['previous_block'] = previous_block
        block['_id'] = _id
        block['timestamp'] = datetime.now().timestamp()
        block['diploma_type'] = diploma_type
        block['pdf_hash'] = pdf_hash
        block['author'] = authors
        block['date_of_defense'] = datetime.combine(
            date_of_defense, datetime.min.time())
        block['title'] = title
        block['language'] = language
        block['discipline'] = discipline
        block['is_defended'] = is_defended
        block['university'] = university
        block['faculty'] = faculty
        block['supervisor'] = supervisor
        block['reviewer'] = reviewer
        block['additional_info'] = additional_info
        block['chain_version'] = chain_version
        block['hash'] = cls.calculate_merkle_root([
            block['previous_block'],
            block['_id'],
            block['timestamp'],
            block['diploma_type'],
            block['pdf_hash'],
            block['author'],
            block['date_of_defense'],
            block['title'],
            block['language'],
            block['discipline'],
            block['is_defended'],
            block['university'],
            block['faculty'],
            block['supervisor'],
            block['reviewer'],
            block['additional_info'],
            block['chain_version']
        ])
        block['signed_hash'] = signing_function(block['hash'])
        return cls.from_dict(block)
        

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
        logger.info(f"Creating class from dict for {data['title']}")
        return cls(
            data['previous_block'],
            data['_id'],
            data['timestamp'],
            data['diploma_type'],
            data['pdf_hash'],
            data['author'],
            data['date_of_defense'],
            data['title'],
            data['language'],
            data['discipline'],
            data['is_defended'],
            data['university'],
            data['faculty'],
            data['supervisor'],
            data['reviewer'],
            data['additional_info'],
            data['chain_version'],
            data['hash'],
            data['signed_hash'],
        )
