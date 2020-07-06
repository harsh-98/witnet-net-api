import json
from witnet_lib.tcp_handler import TCPSocket
from .utils.logger import log
from witpy.util.jsonrpc import Request


class RPC():
    def __init__(self, node_addr):
        self.tcp = TCPSocket("connect")
        self.node_addr = node_addr

    def connect(self):
        self.tcp.connect(self.node_addr)

    def close(self):
        self.tcp.close()

    def receive(self):
        decoded = ""
        while True:
            try:
                resp = self.tcp.receive()
                decoded += resp.decode("utf-8")
                decoded = json.loads(decoded)
                if decoded.get('error', False):
                    log.fatal("Error", decoded)
                    return {}
                else:
                    return decoded['result']
            except json.decoder.JSONDecodeError as err:
                log.fatal(err)
            except Exception as err:
                log.fatal(err)
                return

    def send(self, method, **params):
        req = Request(method, **params)
        msg = f'{req}\n'
        msg_in_bytes = msg.encode("utf-8")
        try:
            self.tcp.send(msg_in_bytes)
        except Exception as err:
            log.fatal(err)

    def get_mempool(self):
        self.send("getMempool")
        return self.receive()

    def known_peers(self):
        self.send("knownPeers")
        return self.receive()
