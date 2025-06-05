from enum import Enum


class Flag(Enum):
    INADEQUATE = "inadequate"
    UNRELEVANT = "unrelevant"
    UNDETERMINED = "undetermined"
    ERROR = "error"
    OK = "ok"
    TIMEOUT = "timeout"


class Channel(Enum):
    EMAIL = "email"
    REVIEW = "review"
