#!/usr/bin/env python3
"""
    @author: Kemal Turksonmez
"""
from hashlib import sha256
import json
from time import time
import os
from block import Block
class Blockchain:

    # Initializes blockchain if a user hasn't created one.
    def __init__(self, log, transObj):
        # difficulty of PoW algorithm
        self.difficulty = 4
        self.log = log
        self.transObj = transObj
        self.unspentTransactions = transObj.getUnspentTransactions()
        self.spentTransactions = transObj.getSpentTransactions()
        self.chain = log.getChain()
        if len(self.chain) == 0:
            self.chain = []
            self.startGenesis()

    # creates genesis block
    def startGenesis(self):
        genesis = Block(0, "", time(), "0")
        self.chain.append(genesis)
        print("Genesis block created")
        print(json.dumps(genesis.__dict__, sort_keys=True))
        self.log.overwriteChain(self.chain)

    # returns last block
    def getLastBlock(self):
        return self.chain[-1]

    # proof of work, increases nonce till a hash of a certain difficulty is found
    def PoW(self, block):
        while not (block.computeHash().startswith('0' * self.difficulty)):
            block.nonce += 1
        print("Proof of work found!")

    # gets coin from a transaction
    def getCoins(self, transaction):
        vals = transaction.split(" ")
        coins = vals[3].replace("#", "")
        return int(coins)

    # gets unspent transaction output for a given user
    # name - name of user
    def utxo(self, name):
        wallet = 0
        for block in self.chain:
            transaction = block.transaction
            if name + " gives" in transaction:
                wallet = wallet - self.getCoins(transaction)
            elif "gives " + name in transaction:
                wallet = wallet + self.getCoins(transaction)
        return wallet
    
    # checks to see if a transaction was a double spending 
    # transaction - transaction in question
    # returns true if was 
    def doubleSpend(self, transaction):
        for block in self.chain:
            if transaction in block.transaction:
                return True
        return False

    #overwrites transactions
    def overWriteTransactions(self):
        self.transObj.overwriteUnspentTransactions(self.unspentTransactions)
        self.transObj.overwriteSpentTransactions(self.spentTransactions)

    # begins mining process
    def mine(self):
        transaction = None
        prevHash = self.getLastBlock().computeHash()
        block = Block(len(self.chain), "", time(), prevHash)

        # verify through utxo that spender has enough money to send transaction and that it is not a double spending
        # once a verified transaction has been selected
        # pick transactions from list
        for val in self.unspentTransactions:
            print("Attempting to mine transaction: " + val)
            name = val.split(" ")[0]
            coins = self.getCoins(val)
            if name == "ExtExchange":
                if not self.doubleSpend(val):
                    transaction = val
                    break
                else:
                    print('Transaction "' + val + '" was a double spend')
                    self.unspentTransactions.remove(val)
            elif self.utxo(name) >= coins:
                if not self.doubleSpend(val):
                    transaction = val
                    break
                else:
                    print('Transaction "' + val + '" was a double spend')
                    self.unspentTransactions.remove(val)
            else:
                print('In transaction "' + val + '", ' + name + ' did not have enough money')
        # if a transaction has been set continue
        if transaction:
            # set block transaction
            block.transaction = transaction
            # remove transaction from unspent transactions to spent transactions
            self.unspentTransactions.remove(transaction)
            self.spentTransactions.append(transaction)
            # perform proof of work
            self.PoW(block)
            # return updated block
            self.chain.append(block)
            print("Block: \n" +  json.dumps(block.__dict__, sort_keys=True, indent=3) + "\nmined!")
            # overwrite chain
            self.log.overwriteChain(self.chain)
            # overwrite transactions
            self.overWriteTransactions()
            return block
        # else return error code
        print("Currently no valid transactions sitting in pool")
        #overwrite transactions
        self.overWriteTransactions()
        return -1

        # don't remove transaction from list until its a couple blocks behind
        # maybe we can move to another temporary list so we know that it fully hasn't been accepted
        # once transaction is a couple blocks behind, we can fully remove it

    
    # verifies block sent from another miner
    def verifyBlock(self):
        print(0)
    
    # verifies chain sent from another miner
    # chain sent by miner
    def verifyChain(self, chain):
        print(0)