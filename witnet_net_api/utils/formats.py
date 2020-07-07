import platform
from witnet_net_api import __version__

NODE_FORMAT = {
    "p2p_addr": "",
    "id": "",
    "rpc_addr": "",
    "contact": "",
    "secret": ""
}

INFO_FORMAT = {
    "name": "",
    "contact": "",
    "coinbase": None,
    "node": None,
    "ip": "",
    "net": None,
    "port": 0,
    "os": platform.system(),
    "os_v": platform.release(),
    "client": __version__,
    "canUpdateHistory": True,
}

TOML_FORMAT = {
    "nodes": [],
    "secret": "",
    "web_addr": "",
}
