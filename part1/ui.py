#!/usr/bin/env python3
"""
    @author: Kemal Turksonmez
"""
from blockchain import Blockchain
from log import Log
from transactions import Transactions
class UI:
    def __init__(self, minerNum, lock):
        # the node's copy of blockchain
        self.log = Log(lock)
        self.transObj = Transactions(minerNum)
        self.blockchain = Blockchain(self.log, self.transObj)
        self.startUI()

    def startUI(self):
        canContinue = True
        while True:
            canContinue = self.blockchain.mine()
            if not canContinue:
                inp = input("Would you like to quit?\n")
                if inp.lower() == "quit":
                    break
                else:
                    canContinue = True



    # def broadcastBlock(self, block):
    #     print(0)

    # #check to see if new block matches last block in chain
    # def verifyNewBlock(self):
    #     # if block's prev hash matches last block's hash, add to chain
    #     # if it doesn't, ask for full chain
    #         # pass full chain to consensus algorithm
    
    # def consensus(self):
    #     # verify the chain is valid
    #     # if it is, overwrite your chain
    #     # if it isn't, leave it 

    # # if the node has crashed and comes back online, it will ask the network for chain lengths
    # def askNetworkForChainLength(self):

    # # asks network for chain
    # def askNetForChain(self):
    

