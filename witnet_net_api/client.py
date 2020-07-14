from datetime import datetime
import logging
import socketio
from witnet_lib.utils import resolve_url, AttrDict
from witnet_net_api import __version__
from .connection import get_connection
from .utils.logger import log
from .history.blockchain import Blockchain
from .rpc_client import RPC
from .utils.formats import INFO_FORMAT

logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)
logging.getLogger('witnet_lib').setLevel(logging.ERROR)


class APINamespace(socketio.ClientNamespace):
    def __init__(self, namespace, args):
        self.namespace = namespace
        self.args = args
        super().__init__(namespace)

    def on_connect(self):
        log.info(f'{self.args.id}: Connecting to [{self.args.web_addr}]')
        # host, port = resolve_url(self.args.node_addr)
        info = {
            **INFO_FORMAT,
            "contact": self.args.contact,
            "name": self.args.id,
        }
        log.debug(f"Info msg: {info}")
        self.emit("hello", {
            "id": self.args.id,
            "secret": self.args.secret,
            "info": info,
        }, namespace=self.namespace)

    def on_disconnect(self):
        log.info(f'{self.args.id}: Disconnecting from [{self.args.web_addr}]')

    def on_data(self, data):
        pass


class Client():
    NAMESPACE = "/api"

    def __init__(self, web_addr="", secret="", consensus_constants=None, node=None):
        log.debug(node.__dict__)
        self.node = node

        self.web_addr = web_addr
        self.secret = secret
        self.last_rpc_call = None
        self.terminate = True

        # set blockchain for maintaining  history
        self.blockchain = Blockchain()
        # connect to node at p2p port
        try:
            self.connection = get_connection(
                consensus_constants=consensus_constants, node_addr=self.node.p2p_addr)
            self.terminate = False
        except ValueError as err:
            log.fatal("Genesis timestamp is in the future %s", err)
        except ConnectionRefusedError as err:
            log.fatal(err)
        except Exception as err:
            log.fatal(err)

        # connect to web dashboard server
        self.sio = socketio.Client()

        # connect to rpc at rpc_addr
        self.rpc_client = RPC(self.node.rpc_addr)

    def run_client(self):
        attr = AttrDict({
            "contact": self.node.contact,
            "id": self.node.id,
            "web_addr": self.web_addr,
            # "node_addr": self.node.p2p_addr,
            "secret": self.node.secret if self.node.secret != "" else self.secret
        })
        self.sio.register_namespace(APINamespace(self.NAMESPACE, attr))

        try:
            self.sio.connect(self.web_addr)
        except socketio.exceptions.ConnectionError as err:
            log.error(err)
            return

        self.last_rpc_call = datetime.now()
        # get data from witnet node
        self.rpc_client.connect()
        self.start_listener_loop()

    def rpc_enabled(self):
        return len(self.node.rpc_addr) > 0

    def start_listener_loop(self):
        while not self.terminate:
            # this returns serialized message from node
            msg = self.connection.tcp_handler.receive_witnet_msg()
            parsed_msg = self.connection.msg_handler.parse_msg(msg)
            if parsed_msg.kind.HasField("Block"):
                log.debug(parsed_msg)
                self.blockchain.add_block(parsed_msg.kind.Block)

            if parsed_msg.kind.HasField("SuperBlockVote"):
                log.debug(parsed_msg)
                self.send_super_block(parsed_msg)

            if parsed_msg.kind.HasField("LastBeacon"):
                checkpoint = parsed_msg.kind.LastBeacon.highest_block_checkpoint
                # log.debug(parsed_msg)
                _hash = checkpoint.hash_prev_block.SHA256.hex()
                epoch = checkpoint.checkpoint
                block = self.blockchain.get_block(epoch, _hash)
                if block:
                    self.send_block(block)

            if parsed_msg.kind.HasField("Peers"):
                self.send_stats(parsed_msg)

            self.rpc_calls()

    def rpc_calls(self):
        if (datetime.now() - self.last_rpc_call).seconds > self.node.rpc_interval_sec and self.rpc_enabled():
            get_peers_cmd = self.connection.msg_handler.get_peers_cmd()
            msg = self.connection.msg_handler.serialize(get_peers_cmd)
            self.connection.tcp_handler.send(msg)
            # msg = self.rpc_client.known_peers()

            # fetch active pkhs
            msg = self.rpc_client.active_reputation()
            self.send_activePkh(msg)

            # get pending tx
            msg = self.rpc_client.get_mempool()
            self.send_pending(msg)

            # set past for scheduling next rpc calls
            self.last_rpc_call = datetime.now()

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
        self.sio.emit("superBlock", msg, namespace=self.NAMESPACE)

    def send_block(self, block):
        msg = {
            "id": self.node.id,
            "block": block,
        }
        log.debug(msg)
        self.sio.emit("block", msg, namespace=self.NAMESPACE)

    def send_activePkh(self, active_reputation_set):
        active_count = 0
        for _, rep in active_reputation_set.items():
            if rep[0] > 0 and rep[1]:
                active_count += 1
        msg = {
            "id": self.node.id,
            "count": active_count,
        }
        log.debug(msg)
        self.sio.emit("activePkh", msg, namespace=self.NAMESPACE)

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
        log.debug(msg)
        self.sio.emit("stats", msg, namespace=self.NAMESPACE)

    def send_pending(self, msg):
        stats = {
            "pendingVTT": len(msg.get('value_transfer', [])),
            "pendingRAD": len(msg.get('data_request', [])),
        }
        msg = {
            "id": self.node.id,
            "stats": stats,
        }
        log.info(msg)
        self.sio.emit("pending", msg, namespace=self.NAMESPACE)

    def close(self):
        log.info("closing")
        self.terminate = True
        self.rpc_client.close()
        self.sio.disconnect()
