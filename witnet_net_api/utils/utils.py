import hashlib
import toml
from witnet_lib.utils import AttrDict
from .formats import validate_config


def number(rust_style_number):
    parts = rust_style_number.split("_")
    str_num = "".join(parts)
    return int(str_num)


def sha256_proto(msg):
    m = hashlib.sha256()
    bytes_stream = msg.SerializeToString()
    m.update(bytes_stream)
    return m.digest().hex()


def load_config(cfg):
    config = toml.load(cfg)
    attr = validate_config(config)
    return AttrDict(attr)
