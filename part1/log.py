#!/usr/bin/env python3
"""
    @author: Kemal Turksonmez
"""
import os
import json
from block import Block
class Log:
    def __init__(self, lock):
        self.lock = lock
        if not os.path.isfile('log.json'):
            logfile = open('log.json', 'w+')
            logfile.close()
    
    # returns chain from file
    def getChain(self):
        # acquire lock
        self.lock.acquire()
        logfile = open('log.json', 'r')
        data = logfile.read()
        blockchain = []
        if not data == "":
            chain = json.loads(data)
            for block in chain:
                blockchain.append(Block(block["index"], block["transaction"], block["timestamp"], block["previous_hash"], block["nonce"]))
            # release lock
            self.lock.release()
            return blockchain
        # release lock
        self.lock.release()
        return blockchain

    #gets chain length
    def getLogChainLength(self):
        logfile = open('log.json', 'r')
        data = logfile.read()
        chain = []
        if not data == "":
            chain = json.loads(data)
        return len(chain)

    # overwrites chain with new chain
    def overwriteChain(self, chain):
        chainWritten = False
        # acquire lock
        self.lock.acquire()
        if self.getLogChainLength() < len(chain):
            logfile = open('log.json', 'w')
            logfile.write("[\n")
            for block in chain:
                logfile.write(json.dumps(block.__dict__, sort_keys=True, indent=3))
                if block != chain[-1]:
                    logfile.write(",\n")
            logfile.write("\n]")
            logfile.close()
            chainWritten = True
         # release lock
        self.lock.release()
        return chainWritten


    