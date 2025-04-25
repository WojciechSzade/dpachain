from enum import Enum
from typing import Any


class PeerStatus(Enum):
    UNKNOWN = 0
    ACTIVE = 1
    INACTIVE = 2
    OWN = 3
    BANNED = 9

    def __str__(self):
        return self.name


class Peer:
    def __init__(self, nickname: str, public_key: str, adress: str | None = None, status: PeerStatus = PeerStatus.UNKNOWN, is_authorized: bool = False, is_banned: bool = False):
        self.nickname = nickname
        self.public_key = public_key
        self.adress = adress if adress else nickname if not nickname.endswith(
            ".peer") else None
        self.status = status
        self.is_authorized = is_authorized

    def as_dict(self):
        return {
            "nickname": self.nickname,
            "public_key": self.public_key,
            "adress": self.adress,
            "status": self.status.value,
            "is_authorized": self.is_authorized
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]):
        return cls(
            data["nickname"],
            data["public_key"],
            data["adress"],
            PeerStatus(data["status"]),
            data["is_authorized"]
        )

    def is_not_valid(self) -> str | None:
        if self.status == PeerStatus.BANNED:
            return "Peer is banned"
        return None

    def is_active(self):
        return self.status == PeerStatus.ACTIVE or self.status == PeerStatus.OWN

    def get_state(self):
        return PeerStatus(self.status)
