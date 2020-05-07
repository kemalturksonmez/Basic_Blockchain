#!/usr/bin/env python3
"""
    @author: Kemal Turksonmez
"""
from hashlib import sha256
import json
class Block:
    # index - index of block
    # index - list of transactions
    # timestamp - timestamp when transactions were added
    # previous_hash - hash of previous block
    def __init__(self, index, transaction, timestamp, previous_hash, validator, signer=None):
        self.index = index
        self.transaction = transaction
        self.timestamp = timestamp
        self.previous_hash = previous_hash # Adding the previous hash field
        self.reward = 0 
        self.validator = validator
        self.signer = signer

    
    def computeHash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True) # The string equivalent also considers the previous_hash field now
        return sha256(block_string.encode()).hexdigest()
    
    
