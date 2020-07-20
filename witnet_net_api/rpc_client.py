import json
from witnet_lib.tcp_handler import TCPSocket
# from .utils.logger import log
from witpy.util.jsonrpc import Request


class RPC():
    def __init__(self, node_addr, log):
        self.tcp = TCPSocket(node_addr)
        self.node_addr = node_addr
        self.log = log

    def connect(self):
        self.tcp.connect()

    def close(self):
        self.tcp.close()

    def receive(self):
        decoded = ""
        while True:
            try:
                # fix for infinite in the tcp connection is dropped
                # as resp is not decoded as json and results in error
                # and due to exception loop repeats
                if self.tcp.isClosed():
                    return {}
                resp, _ = self.tcp.receive()
                decoded += resp.decode("utf-8")
                decoded = json.loads(decoded)
                if decoded.get('error', False):
                    self.log.error(decoded)
                    return {}
                else:
                    return decoded['result']
            except json.decoder.JSONDecodeError as err:
                self.log.warn(err)
            except Exception as err:
                self.log.fatal(err)
                return

    def send(self, method, **params):
        req = Request(method, **params)
        msg = f'{req}\n'
        msg_in_bytes = msg.encode("utf-8")
        try:
            self.tcp.send(msg_in_bytes)
        except Exception as err:
            self.log.fatal(err)

    def get_mempool(self):
        self.send("getMempool")
        return self.receive()

    def active_reputation(self):
        self.send("getReputationAll")
        return self.receive()

    def known_peers(self):
        self.send("knownPeers")
        return self.receive()
