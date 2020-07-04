import hashlib


def number(rust_style_number):
    parts = rust_style_number.split("_")
    str_num = "".join(parts)
    return int(str_num)


def sha256_proto(msg):
    m = hashlib.sha256()
    bytes_stream = msg.SerializeToString()
    m.update(bytes_stream)
    return m.digest().hex()
