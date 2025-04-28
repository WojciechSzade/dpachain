import base64
import json
import logging
import hashlib
import datetime
import os
from typing import Any, Callable, Optional

from src.block.errors import *
from src.block.interfaces import IBlock


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Block(IBlock):
    def __init__(
            self, previous_block: str, _id: int, timestamp: float,
            diploma_type: str, pdf_hash: str, authors: (list[str] | str),
            authors_id: (list[str] | str), date_of_defense: datetime.date,
            title: str, language: str, discipline: str, is_defended: int,
            university: str, faculty: str, supervisor: (list[str] | str),
            reviewer: (list[str] | str), additional_info: Optional[str],
            peer_author: str, chain_version: str, hash: str, signed_hash: str, jwt_token: str):
        self.previous_block = previous_block
        self._id = _id
        self.timestamp = timestamp
        self.diploma_type = diploma_type
        self.pdf_hash = pdf_hash
        self.authors = authors
        self.authors_id = authors_id
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
        self.jwt_token = jwt_token

    @classmethod
    def create_block(
            cls, previous_block: str, _id: int, diploma_type: str, pdf_hash: str, authors: (list[str] | str),
            authors_id: (list[str] | str), title: str, language: str, discipline: str, is_defended: int,
            date_of_defense: datetime.date, university: str, faculty: str, supervisor: (list[str] | str),
            reviewer: (list[str] | str), peer_author: str, chain_version: str, signing_function: Callable[[str], str],
            jwt_encoding_function: Callable[[dict], str], additional_info: Optional[str] = None):
        timestamp = datetime.datetime.now().timestamp()
        date_of_defense = datetime.datetime.combine(
            date_of_defense, datetime.datetime.min.time())

        hash = cls.calculate_merkle_root([previous_block, _id, timestamp, diploma_type, pdf_hash, authors, authors_id,
                                          date_of_defense, title, language, discipline, is_defended, university, faculty,
                                          supervisor, reviewer, additional_info, peer_author, chain_version])
        signed_hash = signing_function(hash)
        jwt_token = jwt_encoding_function({
            "previous_block": previous_block,
            "_id": _id,
            "timestamp": timestamp,
            "diploma_type": diploma_type,
            "pdf_hash": pdf_hash,
            "authors": authors,
            "authors_id": authors_id,
            "date_of_defense": date_of_defense.isoformat(),
            "title": title,
            "language": language,
            "discipline": discipline,
            "is_defended": is_defended,
            "university": university,
            "faculty": faculty,
            "supervisor": supervisor,
            "reviewer": reviewer,
            "additional_info": additional_info,
            "peer_author": peer_author,
            "chain_version": chain_version,
            "hash": hash,
            "signed_hash": signed_hash
        })
        return cls(
            previous_block=previous_block, _id=_id, timestamp=timestamp, diploma_type=diploma_type, pdf_hash=pdf_hash,
            authors=authors, authors_id=authors_id, date_of_defense=date_of_defense, title=title, language=language,
            discipline=discipline, is_defended=is_defended, university=university, faculty=faculty, supervisor=supervisor,
            reviewer=reviewer, additional_info=additional_info, peer_author=peer_author, chain_version=chain_version, hash=hash,
            signed_hash=signed_hash, jwt_token=jwt_token)

    @staticmethod
    def calculate_merkle_root(data):
        def _hash_pair(a, b):
            sum = (str(a) + str(b)).encode()

            hash_string = hashlib.sha256(sum).hexdigest()
            return hash_string

        data = sorted(data, key=lambda x: str(x))

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

    def as_dict(self):
        return {
            "previous_block": self.previous_block,
            "_id": self._id,
            "timestamp": self.timestamp,
            "diploma_type": self.diploma_type,
            "pdf_hash": self.pdf_hash,
            "authors": self.authors,
            "authors_id": self.authors_id,
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
            "signed_hash": self.signed_hash,
            "jws_token": self.jwt_token
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(
            data['previous_block'],
            data['_id'],
            data['timestamp'],
            data['diploma_type'],
            data['pdf_hash'],
            data['authors'],
            data['authors_id'],
            datetime.datetime.fromisoformat(data['date_of_defense']),
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
            data['jws_token'],
        )


class GenesisBlock(IBlock):
    def __init__(self, _id, keys, hash, signed_hash, jwt_token):
        self._id = _id
        self.keys = keys
        self.hash = hash
        self.signed_hash = hash
        self.jwt_token = jwt_token

    @classmethod
    def create_block(cls, keys_file: str, signing_function: Callable[[str], str], jwt_encoding_function: Callable[[dict], str]):
        keys = {}
        with open("signing_keys/" + keys_file + ".json", "r") as file:
            keys = json.load(file)
        keys_as_list = [x for pair in keys.items() for x in pair]
        hash = Block.calculate_merkle_root(keys)
        signed_hash = signing_function(hash)
        jwt_token = jwt_encoding_function(
            {**keys, **{"signed_hash": signed_hash}})
        return cls(
            _id=0,
            keys=keys,
            hash=hash,
            signed_hash=signed_hash,
            jwt_token=jwt_token
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "_id": self._id,
            "keys": self.keys,
            "hash": self.hash,
            "signed_hash": self.signed_hash,
            "jwt_token": self.jwt_token
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(
            _id=data["_id"],
            keys=data["keys"],
            hash=data["hash"],
            signed_hash=data["signed_hash"],
            jwt_token=data["jwt_token"]
        )
