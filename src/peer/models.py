from enum import Enum


class PeerStatus(Enum):
    UNKNOWN = 0
    ACTIVE = 1
    INACTIVE = 2
    OWN = 3


class Peer:
    def __init__(self, nickname: str, status: PeerStatus = PeerStatus.UNKNOWN, is_authorized: bool = False, is_banned: bool = False, public_key: str = None):
        self.nickname = nickname
        self.status = status
        self.is_authorized = is_authorized
        self.is_banned = is_banned
        self.public_key = public_key
    
    @property
    def dict(self):
        return {
            "nickname": self.nickname,
            "status": self.status.value,
            "is_authorized": self.is_authorized,
            "is_banned": self.is_banned,
            "public_key": self.public_key
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data["nickname"],
            PeerStatus(data["status"]),
            data["is_authorized"],
            data["is_banned"],
            data["public_key"]
        )
    