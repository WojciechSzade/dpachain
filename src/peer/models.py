from enum import Enum


class PeerStatus(Enum):
    UNKNOWN = 0
    ACTIVE = 1
    INACTIVE = 2
    OWN = 3
    BANNED = 9

    def __str__(self):
        return self.name


class Peer:
    def __init__(self, nickname: str, status: PeerStatus = PeerStatus.UNKNOWN, is_authorized: bool = False, public_key: str = None, is_banned: bool = False,):
        self.nickname = nickname
        self.status = status
        self.is_authorized = is_authorized
        self.public_key = public_key

    @property
    def dict(self):
        return {
            "nickname": self.nickname,
            "status": self.status.value,
            "is_authorized": self.is_authorized,
            "public_key": self.public_key
        }

    @classmethod
    def from_dict(cls, data: dict):
        return cls(
            data["nickname"],
            PeerStatus(data["status"]),
            data["is_authorized"],
            data["public_key"]
        )

    def is_valid(self):
        return self.status != PeerStatus.BANNED

    def is_active(self):
        return self.status == PeerStatus.ACTIVE or self.status == PeerStatus.OWN
