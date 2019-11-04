import hashlib
import random

import Constants

BITS_COUNT = 256


def format2(a, b) -> str:
    return str(a) + str(b)


def format3(a, b, c) -> str:
    return str(a) + str(b) + str(c)


def format6(a, b, c, d, e, f) -> str:
    return str(a) + str(b) + str(c) + str(d) + str(e) + str(f)


def make_hash(to_hash: str) -> int:
    return int(hashlib.sha256(to_hash.encode("ascii")).hexdigest(), 16)


def make_rand() -> int:
    return random.getrandbits(BITS_COUNT) % Constants.N
