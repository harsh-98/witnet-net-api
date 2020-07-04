import logging
import socketio
from witnet_lib.utils import AttrDict
from .connection import get_connection
from .history import Blockchain


class APINamespace(socketio.ClientNamespace):
    def __init__(self, namespace, args):
        self.namespace = namespace
        self.args = args
        super().__init__(namespace)

    def on_connect(self):
        print("I'm connected!")
        self.emit("hello", {
            "secret": self.args.secret,
            "id": self.args.node_id,
            "info": self.args.info,
        }, namespace=self.namespace)

    def on_disconnect(self):
        print("I'm disconnected!")

    def on_data(self, data):
        pass


class Client():
    NAMESPACE = "/api"
    LOCAL_ADDR = "127.0.0.1:21341"
    blockchain = {}

    def __init__(self, node_id="", ws="", node_addr=""):
        self.node_id = node_id
        self.ws = ws
        self.node_addr = node_addr
        self.blockchain = Blockchain()

    def run_client(self):

        connection = get_connection(
            local_addr=self.LOCAL_ADDR, node_addr=self.node_addr)
        self.sio = socketio.Client()
        attr = AttrDict()

        attr.update({
            "secret": "secret123",
            "node_id": self.node_id,
            "info": "",
        })
        self.sio.register_namespace(APINamespace(self.NAMESPACE, attr))
        self.sio.connect(self.ws)
        # get data from witnet node
        while True:
            # this returns serialized message from node
            msg = connection.tcp_handler.receive_witnet_msg()
            parsed_msg = connection.msg_handler.parse_msg(msg)
            if parsed_msg.kind.HasField("Block"):
                logging.info(parsed_msg)
                self.blockchain.add_block(parsed_msg.kind.Block)

            if parsed_msg.kind.HasField("LastBeacon"):
                checkpoint = parsed_msg.kind.LastBeacon.highest_block_checkpoint
                logging.info(parsed_msg)
                _hash = checkpoint.hash_prev_block.SHA256.hex()
                epoch = checkpoint.checkpoint
                block = self.blockchain.get_block(epoch, _hash)
                if block:
                    self.send_block(block)

    def send_block(self, block):
        msg = {
            "id": self.node_id,
            "block": block,
        }
        print(msg)
        self.sio.emit("block", msg, namespace=self.NAMESPACE)
