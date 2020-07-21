from witnet_lib.witnet_client import WitnetClient
from .utils.logger import log


def get_connection(consensus_constants, node_addr=""):
    # Setting config
    # log.debug(f"Node address: {node_addr}, {consensus_constants.__dict__}")

    # not required to set persistent
    # as client implements a checker to reconnect after `retry_after` seconds
    # but if the connection is resetted we can retry immidiately will
    # persistent connections
    consensus_constants.persistent = True

    client = WitnetClient(consensus_constants)
    client.handshake(node_addr)
    return client
    # client.close()
