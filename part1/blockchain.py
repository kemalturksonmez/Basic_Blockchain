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

    #get length of chain
    def getChainLength(self):
        return len(self.chain)

    #get length of chain
    def getChain(self):
        return self.chain

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
    def utxo(self, name, chain):
        wallet = 0
        for block in chain:
            transaction = block.transaction
            if name + " gave" in transaction:
                wallet = wallet - self.getCoins(transaction)
            elif "gave " + name in transaction:
                wallet = wallet + self.getCoins(transaction)
        return int(wallet)
    
    # checks to see if a transaction was a double spending 
    # transaction - transaction in question
    # returns true if was 
    def doubleSpend(self, transaction, chain):
        for block in chain:
            if transaction in block.transaction:
                return True
        return False

    #overwrites transactions
    def overWriteTransactions(self):
        self.transObj.overwriteUnspentTransactions(self.unspentTransactions)
        self.transObj.overwriteSpentTransactions(self.spentTransactions)

    #Checks blockchain to ensure that it can commit transaction
    def commitTransactions(self):
        chainlength = len(self.chain)
        for transaction in self.spentTransactions:
            committed = False
            onChain = False
            for block in self.chain:
                if transaction == block.transaction:
                    onChain = True
                    if block.index < (chainlength - 5):
                        print("Transaction: " + transaction + " has been committed")
                        # commit transaction
                        self.spentTransactions.remove(transaction)
                        committed = True
            if not onChain and not committed:
                # add back to transaction pool
                self.unspentTransactions.append(transaction)
                self.spentTransactions.remove(transaction)

    # begins mining process
    def mine(self):
        #Ensure chain is most recent version
        self.chain = self.log.getChain()
        transaction = None
        prevHash = self.getLastBlock().computeHash()
        block = Block(len(self.chain), "", time(), prevHash)

        # verify through utxo that spender has enough money to send transaction and that it is not a double spending
        # once a verified transaction has been selected
        # pick transactions from list
        for val in self.unspentTransactions:
            rc = -2
            chainWritten = False
            print("Attempting to mine transaction: " + val)
            name = val.split(" ")[0]
            amount = self.getCoins(val)
            if name == "ExtExchange":
                if not self.doubleSpend(val, self.chain):
                    transaction = val
                    break
                else:
                    print('Transaction "' + val + '" was a double spend')
                    self.unspentTransactions.remove(val)
            elif self.utxo(name, self.chain) >= amount:
                if not self.doubleSpend(val, self.chain):
                    transaction = val
                    break
                else:
                    print('Transaction "' + val + '" was a double spend')
                    self.unspentTransactions.remove(val)
            else:
                print('In transaction "' + val + '", ' + name + ' did not have enough money')
                print(name + "'s wallet had: " + str(self.utxo(name, self.chain)) + " and " + name + " wanted to spend " + str(amount))
        # if a transaction has been set continue
        if transaction:
            # set block transaction
            block.transaction = transaction
            # perform proof of work
            self.PoW(block)
            # return updated block
            self.chain.append(block)
            print("Block: \n" +  json.dumps(block.__dict__, sort_keys=True, indent=3) + "\nmined!")
            # overwrite chain
            chainWritten = self.log.overwriteChain(self.chain)
            if chainWritten:
                # remove transaction from unspent transactions to spent transactions
                self.unspentTransactions.remove(transaction)
                self.spentTransactions.append(transaction)
                rc = 0
        # if transaction not found
        else:
            print("Currently no valid transactions sitting in pool")
            rc = -2
        if transaction and not chainWritten:
            print("Transaction " + transaction + " was not mined because longer block chain was found")
            rc = -1
        # attempt to commit transactions
        self.commitTransactions()
        # overwrite transactions
        self.overWriteTransactions()
        return rc
    
    #verifies block sent from another miner
    def verifyBlock(self, block, chain=None):
        if not chain:
            chain = self.chain
        transaction = block.transaction
        sender,f,receipient,amount = transaction.split(" ")
        amount = amount.replace("#","").replace("\n", "")
        # check to see if transaction is double spend
        canContinue = self.doubleSpend(transaction, chain)
        if canContinue:
            canContinue = False
            if sender != "ExtExchange":
                wallet = self.utxo(sender, chain)
                if wallet >= int(amount):
                    canContinue = True
                if not canContinue:
                    print("Block invalid: sender did not have enough money")
                    return False
            else:
                canContinue = True
        else:
            print("Block invalid: double spend transaction exists on chain")
            return False
        if canContinue:
            if len(chain) < block.index:
                print("Block invalid: block is ahead of chain")
                return False
            # verify hash of previous block
            canContinue = chain[block.index-1].computeHash() == block.previous_hash
        if canContinue:
            # verify proof of work of current block
            canContinue = block.computeHash().startswith('0' * self.difficulty)
            if not canContinue:
                print("Block invalid: incorrect proof of work")
                return False
        else:
                print("Block invalid: previous hash did not match previous block's hash")
                return False
        return canContinue


    # verifies chain sent from another miner
    # chain sent by miner
    def verifyChain(self, chain):
        canContinue = True
        for block in chain:
            if block.index > 0:
                if not self.verifyBlock(block, chain):
                    return False
        return True