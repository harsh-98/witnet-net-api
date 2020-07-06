from .utils.logger import log
import socketio
from witnet_lib.utils import AttrDict
from .connection import get_connection
from .history.blockchain import Blockchain
from datetime import datetime
from .rpc_client import RPC
import asyncio
import logging

logging.getLogger('socketio').setLevel(logging.ERROR)
logging.getLogger('engineio').setLevel(logging.ERROR)
logging.getLogger('witnet_lib').setLevel(logging.ERROR)


class APINamespace(socketio.ClientNamespace):
    def __init__(self, namespace, args):
        self.namespace = namespace
        self.args = args
        super().__init__(namespace)

    def on_connect(self):
        log.info(f'{self.args.id}: Connecting to [{self.args.addr}]')
        self.emit("hello", {
            "secret": self.args.secret,
            "id": self.args.id,
            "info": self.args.info,
        }, namespace=self.namespace)

    def on_disconnect(self):
        log.info(f'{self.args.id}: Disconnecting from [{self.args.addr}]')

    def on_data(self, data):
        pass


class Client():
    NAMESPACE = "/api"
    LOCAL_ADDR = "127.0.0.1:21341"
    blockchain = {}

    def __init__(self, web_addr="", node={}):
        self.node = node
        log.debug(node)
        self.ws = web_addr

        self.blockchain = Blockchain()
        self.connection = get_connection(
            local_addr=self.LOCAL_ADDR, node_addr=self.node.p2p_addr)
        self.sio = socketio.Client()
        self.rpc_client = RPC(self.node.rpc_addr)
        self.terminate = False

    def run_client(self):
        attr = AttrDict(**{
            "secret": "secret123",
            "id": self.node.id,
            "addr": self.ws,
            "info": "",
        })
        self.sio.register_namespace(APINamespace(self.NAMESPACE, attr))
        self.sio.connect(self.ws)
        # get data from witnet node
        self.rpc_client.connect()
        self.start_listener_loop()

    def start_listener_loop(self):
        past = datetime.now()
        while not self.terminate:
            # this returns serialized message from node
            msg = self.connection.tcp_handler.receive_witnet_msg()
            parsed_msg = self.connection.msg_handler.parse_msg(msg)
            if parsed_msg.kind.HasField("Block"):
                log.debug(parsed_msg)
                self.blockchain.add_block(parsed_msg.kind.Block)

            if parsed_msg.kind.HasField("LastBeacon"):
                checkpoint = parsed_msg.kind.LastBeacon.highest_block_checkpoint
                log.debug(parsed_msg)
                _hash = checkpoint.hash_prev_block.SHA256.hex()
                epoch = checkpoint.checkpoint
                block = self.blockchain.get_block(epoch, _hash)
                if block:
                    self.send_block(block)

            if parsed_msg.kind.HasField("Peers"):
                self.send_stats(parsed_msg)

            if (datetime.now() - past).seconds > 10:
                get_peers_cmd = self.connection.msg_handler.get_peers_cmd()
                msg = self.connection.msg_handler.serialize(get_peers_cmd)
                self.connection.tcp_handler.send(msg)
                # msg = self.rpc_client.known_peers()
                msg = self.rpc_client.get_mempool()
                self.send_pending(msg)
                past = datetime.now()

    def send_block(self, block):
        msg = {
            "id": self.node.id,
            "block": block,
        }
        log.debug(msg)
        self.sio.emit("block", msg, namespace=self.NAMESPACE)

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
            "pending": len(msg.get('value_transfer', [])),
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
