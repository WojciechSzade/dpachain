import hashlib
from datetime import datetime

from pydantic import BaseModel

class Blockchain:
    def __init__(self, client):
        self.client = client
        self.db = self.client.blockchain
        self.blocks = self.db.blocks
        self.transactions = []
        self.generate_genesis_block()

    def generate_genesis_block(self):
        if self.blocks.count_documents({}) > 0:
            return
        block = Block("0", 0, "0", "0", "0", "0", "0", "0")
        self.blocks.insert_one(block.dict)

    def generate_next_block(self, pdf_hash, author, date_of_defense, university, faculty, supervisor):
        previous_block = self.get_latest_block()['merkle_root']
        _id = self.get_latest_block()['_id'] + 1
        block = Block(previous_block, _id, pdf_hash, author,
                      date_of_defense, university, faculty, supervisor)
        self.blocks.insert_one(block.dict)

    def get_latest_block(self):
        return self.blocks.find_one(sort=[("_id", -1)])

    def get_all_blocks(self):
        return list(self.blocks.find())


class Block():
    def __init__(self, previous_block, _id, pdf_hash, author, date_of_defense, university, faculty, supervisor):
        self.previous_block = previous_block
        self._id = _id
        self.timestamp = datetime.now().timestamp(),
        self.pdf_hash = pdf_hash
        self.author = author
        self.date_of_defense = date_of_defense
        self.university = university
        self.faculty = faculty
        self.supervisor = supervisor
        self.merkle_root = self.calculate_merkle_root([self.previous_block, self._id, self.timestamp,
                                                      self.pdf_hash, self.author, self.date_of_defense, self.university, self.faculty, self.supervisor])

    @property
    def dict(self):
        return {
            "previous_block": self.previous_block,
            "_id": self._id,
            "timestamp": self.timestamp,
            "pdf_hash": self.pdf_hash,
            "author": self.author,
            "date_of_defense": self.date_of_defense,
            "university": self.university,
            "faculty": self.faculty,
            "supervisor": self.supervisor,
            "merkle_root": self.merkle_root
        }

    def calculate_merkle_root(self, data):
        if len(data) == 1:
            return data[0]

        hash_list = []

        for i in range(0, len(data) - 1, 2):
            hash_list.append(self.hash_pair(data[i], data[i + 1]))

        if len(data) % 2 == 1:
            hash_list.append(self.hash_pair(data[-1], data[-1]))

        return self.calculate_merkle_root(hash_list)

    def hash_pair(self, a, b):
        sum = (str(a) + str(b)).encode()

        hash_string = hashlib.sha256(sum).hexdigest()
        return hash_string