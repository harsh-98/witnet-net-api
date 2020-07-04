from witnet_lib.witnet_client import WitnetClient
from witnet_lib.utils import AttrDict


def get_connection(local_addr, node_addr=""):

    # Setting config
    config = AttrDict()
    config.update({
        "genesis_sec": 1592996400,
        "magic": 20787,
        "sender_addr": local_addr,
        "time_per_epoch": 45,
    })

    client = WitnetClient(config)
    client.handshake(node_addr)
    return client

    # client.close()
