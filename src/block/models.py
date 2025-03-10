import logging
import hashlib
from datetime import datetime

from src.block.errors import *


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
