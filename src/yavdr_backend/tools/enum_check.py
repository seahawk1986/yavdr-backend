from enum import StrEnum


def check_if_enum(v: str, e: type[StrEnum]) -> bool:
    try:
        e(v)
    except Exception:
        return False
    else:
        return True
