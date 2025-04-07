import logging
import hashlib
from datetime import datetime

from src.block.errors import *


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Block:
    def __init__(self, previous_block, _id, timestamp, diploma_type, pdf_hash, authors, date_of_defense, title, language, discipline, is_defended, university, faculty, supervisor, reviewer, additional_info, peer_author, chain_version, hash, signed_hash):
        self.previous_block = previous_block
        self._id = _id
        self.timestamp = timestamp
        self.diploma_type = diploma_type
        self.pdf_hash = pdf_hash
        self.authors = authors
        self.date_of_defense: datetime.date = date_of_defense
        self.title = title
        self.language = language
        self.discipline = discipline
        self.is_defended = is_defended
        self.university = university
        self.faculty = faculty
        self.supervisor = supervisor
        self.reviewer = reviewer
        self.additional_info = additional_info
        self.peer_author = peer_author
        self.chain_version = chain_version
        self.hash = hash
        self.signed_hash = signed_hash

    @classmethod
    def create_block(cls, previous_block: str, _id: int, diploma_type: str, pdf_hash: str, authors: (list[str] | str), title: str, language: str, discipline: str, is_defended: int, date_of_defense: datetime.date, university: str, faculty: str, supervisor: (list[str] | str), reviewer: (list[str] | str), peer_author: str, chain_version: str, signing_function: callable, additional_info: (str | None) = None):
        timestamp = datetime.now().timestamp()
        date_of_defense = datetime.combine(
            date_of_defense, datetime.min.time())

        hash = cls.calculate_merkle_root([previous_block, _id, timestamp, diploma_type, pdf_hash, authors, date_of_defense,
                                         title, language, discipline, is_defended, university, faculty, supervisor, reviewer, additional_info, peer_author, chain_version])
        return cls(previous_block, _id, timestamp, diploma_type, pdf_hash, authors, date_of_defense, title, language, discipline, is_defended, university, faculty, supervisor, reviewer, additional_info, peer_author, chain_version, hash, signing_function(hash))

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
            "authors": self.authors,
            "date_of_defense": self.date_of_defense.isoformat(),
            "title": self.title,
            "language": self.language,
            "discipline": self.discipline,
            "is_defended": self.is_defended,
            "university": self.university,
            "faculty": self.faculty,
            "supervisor": self.supervisor,
            "reviewer": self.reviewer,
            "additional_info": self.additional_info,
            "peer_author": self.peer_author,
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
            data['authors'],
            datetime.fromisoformat(data['date_of_defense']),
            data['title'],
            data['language'],
            data['discipline'],
            data['is_defended'],
            data['university'],
            data['faculty'],
            data['supervisor'],
            data['reviewer'],
            data['additional_info'],
            data['peer_author'],
            data['chain_version'],
            data['hash'],
            data['signed_hash'],
        )
