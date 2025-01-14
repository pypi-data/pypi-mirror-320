import hashlib
import random


def hex_format(_hex):
    """Hex格式化"""
    Hex = ' '.join(_hex[i:i + 2] for i in range(0, len(_hex), 2))
    return Hex


def get_random_bin(_len):
    byte = b""
    for _ in range(_len):
        byte += bytes([random.randint(0, 255)])
    return byte


def get_md5(byte_content):
    if isinstance(byte_content, str):
        byte_content = byte_content.encode('utf-8')
    md5_object = hashlib.md5()
    md5_object.update(byte_content)
    return md5_object.digest()
