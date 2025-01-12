import hashlib


def uuidify(input_string: str) -> str:
    sha256_hash = hashlib.sha256(input_string.encode("utf-8")).hexdigest()

    uuid_like = (
        f"{sha256_hash[:8]}-{sha256_hash[8:12]}-{sha256_hash[12:16]}-" f"{sha256_hash[16:20]}-{sha256_hash[20:32]}"
    )
    return uuid_like
