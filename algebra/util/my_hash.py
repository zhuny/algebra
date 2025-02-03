from hashlib import blake2b


def int_sequence_hash(name: str, sequence: list[int]) -> str:
    h = blake2b(digest_size=24)
    h.update(name.encode())
    for num in sequence:
        h.update(f'/{num}'.encode())
    h.update(f'/{name}'.encode())

    return f'{name}({h.hexdigest()})'
