import hashlib
import time


class Block:

    def __init__(self, index, data, previous_hash):
        self.index = index
        self.timestamp = time.time()
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.mine_block(3)

    def calculate_hash(self):
        block_data = (
            str(self.index)
            + str(self.timestamp)
            + str(self.data)
            + str(self.previous_hash)
            + str(self.nonce)
        )

        return hashlib.sha256(block_data.encode()).hexdigest()

    def mine_block(self, difficulty):
        target = "0" * difficulty

        self.hash = self.calculate_hash()

        while not self.hash.startswith(target):
            self.nonce += 1
            self.hash = self.calculate_hash()

        return self.hash


class Blockchain:

    def __init__(self):
        self.chain = []

        genesis_block = Block(
            0,
            "Genesis Block",
            "0"
        )

        self.chain.append(genesis_block)

    def add_block(self, data):

        previous_block = self.chain[-1]

        new_block = Block(
            len(self.chain),
            data,
            previous_block.hash
        )

        self.chain.append(new_block)

    def is_chain_valid(self):

        for i in range(1, len(self.chain)):

            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            if current_block.hash != current_block.calculate_hash():
                return False

            if current_block.previous_hash != previous_block.hash:
                return False

        return True