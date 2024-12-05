import hashlib


def calculate_checksum(file_content: bytes) -> str:
    return hashlib.md5(file_content).hexdigest()
