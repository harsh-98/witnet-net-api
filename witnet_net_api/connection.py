from witnet_lib.witnet_client import WitnetClient
from .utils.logger import log


def get_connection(consensus_constants, node_addr=""):
    # Setting config
    # log.debug(f"Node address: {node_addr}, {consensus_constants.__dict__}")
    client = WitnetClient(consensus_constants)
    client.handshake(node_addr)
    return client
    # client.close()
