from witnet_net_api.utils.utils import sha256_proto
from witnet_net_api.utils.constants import INITIAL_BLOCK_REWARD, HALVING_PERIOD


class Block():
    """Wrappers the witnet block for easier access to data
    """

    def __init__(self, block):
        """

        Args:
            block (Proto Witnet Block): The is the parsed witnet block
        """
        self.block = block

    def hash(self):
        """calculates the hash of block headers

        Returns:
            string: hash of block
        """
        return sha256_proto(self.block.block_header)

    def epoch(self):
        """returns block number

        Returns:
            int: block number
        """
        return self.block.block_header.beacon.checkpoint

    def get_total_rewards(self):
        """total rewards = tx fees + wit minted in block

        Returns:
            int: total block rewards
        """
        rewards = 0
        for output in self.block.txns.mint.outputs:
            rewards += output.value
        return rewards

    def miner(self):
        """miner of the block

        Returns:
            string: miner hash
        """
        return self.block.block_header.proof.proof.public_key.public_key.hex()

    def get_block_rewards(self):
        """wit minted in block

        Returns:
            int: wit minted in block
        """
        return INITIAL_BLOCK_REWARD >> int(self.epoch()/HALVING_PERIOD)

    def parent(self):
        """parent block hash

        Returns:
            string: parent block hash
        """
        return self.block.block_header.beacon.hash_prev_block.SHA256.hex()

    def tx_fees(self):
        """tx fees in block

        Returns:
            int: total tx fee present in a block
        """
        return self.get_total_rewards() - self.get_block_rewards()

    def get_txs(self):
        """get the all txns from the block

        Returns:
            list(string): list of the hashes of transactions
        """
        tx_set = {"transactions": []}
        for descriptor in ['value_transfer_txns', 'data_request_txns', 'commit_txns', 'reveal_txns', 'tally_txns', 'mint']:
            txs = getattr(self.block.txns, descriptor)
            if descriptor != "mint":
                tx_set[descriptor] = [sha256_proto(tx) for tx in txs]
            else:
                tx_set[descriptor] = [sha256_proto(txs)]
            tx_set['transactions'].extend(tx_set[descriptor])
        return tx_set

    def get_RAD_hash(self):
        return self.block.block_header.merkle_roots.dr_hash_merkle_root.SHA256.hex()

    def short_miner(self):
        """truncated hash of miner

        Returns:
            string: truncated representation of miner hash
        """
        return self.miner()[:15] + "..." + self.miner()[-15:]

    def convert(self):
        """reduce the witnet proto object to the required data by dashboard

        Returns:
            dictionary: reduced block data
        """
        return {
            "number": self.epoch(),
            "parentHash": self.parent(),
            "miner": self.miner(),
            "difficulty": 0,
            "hash": self.hash(),
            "totalDifficulty": 0,
            "txfees": self.tx_fees(),
            # "uncles": [],
            "RADHash": self.get_RAD_hash(),
            **self.get_txs()
        }
