from datetime import datetime
import logging
import time
import socketio
from witnet_lib.utils import resolve_url, AttrDict

from witnet_net_api import __version__
from .connection import get_connection
from .utils.logger import log, get_logger
from .history.blockchain import Blockchain
from .rpc_client import RPC
from .utils.formats import INFO_FORMAT

logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)
logging.getLogger('witnet_lib').setLevel(logging.ERROR)


class APINamespace(socketio.ClientNamespace):
    def __init__(self, namespace, _log, args):
        self.namespace = namespace
        self.args = args
        self.log = _log
        super().__init__(namespace)

    def on_connect(self):
        self.log.info('Connecting to [%s]', self.args.web_addr)
        ip, port = resolve_url(self.args.p2p_addr)
        info = {
            **INFO_FORMAT,
            "contact": self.args.contact,
            "name": self.args.id,
            "ip": ip,
            "port": port
        }
        self.log.debug(f"Info msg: {info}")
        self.emit("hello", {
            "id": self.args.id,
            "secret": self.args.secret,
            "info": info,
        }, namespace=self.namespace)

    def on_disconnect(self):
        self.log.info(
            f'{self.args.id}: Disconnecting from [{self.args.web_addr}]')

    def on_data(self, data):
        pass


class Client():
    NAMESPACE = "/api"

    def __init__(self, common=None, consensus_constants=None, node=None):
        log.debug(node.__dict__)
        self.node = node

        self.web_addr = common.web_addr
        self.secret = common.secret
        self.retry_after = common.retry_after
        self.last_rpc_call = None
        self.terminate = False
        self.log = get_logger(self.node.id)
        self.consensus_constants = consensus_constants

        # set blockchain for maintaining  history
        self.blockchain = Blockchain()

        # connect to web dashboard server
        self.sio = socketio.Client()

        # get the p2p and dashboard connection for the first time
        self.get_connections()

        # connect to rpc at rpc_addr
        if self.rpc_enabled():
            self.rpc_client = RPC(self.node.rpc_addr, self.log)

    # Tried to use schedule lib for checking if the connection is present or not
    # after retry_after seconds but it is not required.
    # since that requires running a loop too.
    def get_connections(self):
        self.p2p_connection()
        self.dashboard_connection()

    def p2p_connection(self):
        # connect to node at p2p port
        if not self.is_p2p_valid():
            try:
                self.connection = get_connection(
                    consensus_constants=self.consensus_constants, node_addr=self.node.p2p_addr)
            except ValueError as err:
                self.log.fatal("Genesis timestamp is in the future %s", err)
            except ConnectionRefusedError as err:
                self.log.fatal(err)
            except Exception as err:
                self.log.fatal(err)

    def is_p2p_valid(self):
        return (hasattr(self, 'connection') and not self.connection.is_closed())

    def dashboard_connection(self):
        self.log.info("Dashboard connection status %s", self.sio.connected)
        if not self.sio.connected:
            attr = AttrDict({
                "contact": self.node.contact,
                "id": self.node.id,
                "web_addr": self.web_addr,
                "p2p_addr": self.node.p2p_addr,
                "secret": self.secret
            })
            try:
                self.sio.register_namespace(
                    APINamespace(self.NAMESPACE, self.log, attr))
            except Exception as err:
                self.log.fatal("Namespace registration error: %s", err)

            try:
                self.sio.connect(self.web_addr)
            except socketio.exceptions.ConnectionError as err:
                self.log.error(err)

    def run_client(self):
        self.last_rpc_call = datetime.now()
        # connect to rpc port of node
        self.rpc_connection()
        # get data from witnet node
        self.start_listener_loop()

    def rpc_connection(self):
        if self.rpc_enabled() and self.rpc_client.is_closed():
            self.rpc_client.connect()

    def rpc_enabled(self):
        return len(self.node.rpc_addr) > 0

    def start_listener_loop(self):
        while not self.terminate:
            # this returns serialized message from node and parses to python obj
            if self.is_p2p_valid() and self.sio.connected:
                msg = self.connection.receive_msg()
                try:
                    parsed_msg = self.connection.msg_handler.parse_msg(msg)
                except Exception as err:
                    self.log.fatal(err)
                    continue

                if parsed_msg.kind.WhichOneof("kind") in ['SuperBlockVote', 'Block', 'LastBeacon', 'Peers']:
                    self.log.info(
                        parsed_msg.kind.WhichOneof("kind"))

                # match the kind of the object
                if parsed_msg.kind.HasField("Block"):
                    self.log.debug(parsed_msg)
                    self.blockchain.add_block(parsed_msg.kind.Block)

                if parsed_msg.kind.HasField("SuperBlockVote"):
                    self.log.debug(parsed_msg)
                    self.send_super_block(parsed_msg)
                # last beacon takes which block is consolidated to prevent unneccessary forks
                if parsed_msg.kind.HasField("LastBeacon"):
                    checkpoint = parsed_msg.kind.LastBeacon.highest_block_checkpoint
                    # self.log.debug(parsed_msg)
                    _hash = checkpoint.hash_prev_block.SHA256.hex()
                    epoch = checkpoint.checkpoint
                    block = self.blockchain.get_block(epoch, _hash)
                    if block:
                        self.send_block(block)
                # this targets node to send its peers list
                if parsed_msg.kind.HasField("Peers"):
                    self.send_stats(parsed_msg)
                self.schedule_calls()
            else:
                if self.retry_after == 0:
                    return
                self.log.info("Retrying in %d seconds", self.retry_after)
                time.sleep(self.retry_after)
                self.get_connections()
                # for scheduling calls to pull data, above handles push messages from node

        # close rpc, dashboard sio and p2p connections
        self.close_connections()

    def close_connections(self):
        # if rpc is specified in api.toml for
        if self.rpc_enabled():
            self.rpc_client.close()

        # close connection with dashboard
        try:
            self.sio.disconnect()
        except Exception as err:
            self.log.fatal(err)
        # it might happen that connection is not created if the connection is refused via p2p port
        # so check if self has connection attribute
        if self.is_p2p_valid():
            self.connection.close()
        self.log.info("Closing p2p connection")

    def schedule_calls(self):
        if (datetime.now() - self.last_rpc_call).seconds > self.node.calls_interval_sec:
            if self.rpc_enabled():
                self.rpc_calls()
            # currently rpc getPeer is disabled so p2p GETPEERS message is used
            get_peers_cmd = self.connection.msg_handler.get_peers_cmd()
            msg = self.connection.msg_handler.serialize(get_peers_cmd)
            self.connection.send_msg(msg)

            # set past for scheduling next rpc calls
            self.last_rpc_call = datetime.now()

    def rpc_calls(self):
        # msg = self.rpc_client.known_peers()

        # if the connection is terminated get a new connections
        self.rpc_connection()

        # fetch active pkhs
        msg = self.rpc_client.active_reputation()
        self.send_activePkh(msg)

        # get pending tx
        msg = self.rpc_client.get_mempool()
        self.send_pending(msg)

    def send_super_block(self, msg):
        super_block = msg.kind.SuperBlockVote
        reduced_super_block = {
            "index": super_block.superblock_index,
            "hash": super_block.superblock_hash.SHA256.hex()
        }
        msg = {
            "id": self.node.id,
            "super": reduced_super_block
        }
        self.emit_event("superBlock", msg)

    def send_block(self, block):
        msg = {
            "id": self.node.id,
            "block": block,
        }
        self.log.debug(msg)
        self.emit_event("block", msg)

    def emit_event(self, event_name, msg):
        try:
            self.sio.emit(event_name, msg, namespace=self.NAMESPACE)
        except Exception as err:
            self.log.fatal(err)

    def send_activePkh(self, active_reputation_set):
        if active_reputation_set == None:
            return
        active_count = 0
        for _, rep in active_reputation_set.items():
            if rep[0] > 0 and rep[1]:
                active_count += 1
        msg = {
            "id": self.node.id,
            "count": active_count,
        }
        self.log.debug(msg)
        self.emit_event("activePkh", msg)

    def send_stats(self, msg):
        stats = {
            "peers": len(msg.kind.Peers.peers),
            "active": True,
            "mining": True,
            "syncing": False,
            "uptime": 100,
        }
        msg = {
            "id": self.node.id,
            "stats": stats,
        }
        self.log.debug(msg)
        self.emit_event("stats", msg)

    def send_pending(self, msg):
        stats = {
            "pendingVTT": len(msg.get('value_transfer', [])),
            "pendingRAD": len(msg.get('data_request', [])),
        }
        msg = {
            "id": self.node.id,
            "stats": stats,
        }
        self.log.info(msg)
        self.emit_event("pending", msg)

    # async def close(self):

    def close(self):
        self.log.info("closing")
        self.terminate = True
