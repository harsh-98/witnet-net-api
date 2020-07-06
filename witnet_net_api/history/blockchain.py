from .block import Block


class Blockchain():
    blockchain = {}
    LIMIT = 60

    def get_item(self, epoch):
        return self.blockchain[epoch]

    def reduce(self):
        keys = list(self.blockchain.keys())
        if len(keys) > self.LIMIT:
            del self.blockchain[min(keys)]

    def add_block(self, block):
        _block = Block(block)
        epoch = _block.epoch()

        item = self.blockchain.get(epoch, {})
        block_hash = _block.hash()
        item[block_hash] = _block.convert()
        self.blockchain[epoch] = item
        self.reduce()

    def get_block(self, epoch, _hash):
        return self.blockchain.get(epoch, {}).get(_hash, None)
