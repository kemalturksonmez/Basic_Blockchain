#!/usr/bin/env python3
"""
    @author: Kemal Turksonmez
"""
from blockchain import Blockchain
from block import Block
from log import Log
from transactions import Transactions
from time import sleep
import random
import json
class UI:
    def __init__(self, minerNum, lock, comm):
        # the node's copy of blockchain
        self.minerNum = minerNum
        self.log = Log(lock, minerNum)
        self.transObj = Transactions(minerNum)
        self.blockchain = Blockchain(self.log, self.transObj)
        self.comm = comm
        self.allNodes = [i + 1 for i in range(1 + self.comm.get_num_of_processes())]
        self.comm.set_ui_receive(self)

    def startUI(self):
        canContinue = True
        while True:
            rc = self.blockchain.mine()
            if rc == -2:
                print("########################")
                print()
                print("Would you like to quit?")
                print()
                print("########################")
                inp = input()
                if inp.lower() == "quit":
                    break
                else:
                    canContinue = True
                    self.blockchain.commitTransactions()
            else:
                print("Broadcasting block")
                self.broadcastLastBlock()


    def broadcastLastBlock(self):
        # block = [self.blockchain.getLastBlock().__dict__]
        block = [json.dumps(self.blockchain.getLastBlock().__dict__, sort_keys=True)]
        self.sendMessage(100, 'all', msg=block)
            
    
    def sendMessage(self, msg_type, node, msg=None):
        if msg_type == 100:         #send single block
            sent_msg = {'code': 100, 'node': self.minerNum, 'msg': msg}
            
        # ask for full chain to node if not verified
        if msg_type == 101:
                sent_msg = {'code': 101, 'node': self.minerNum}
                    
        # send full block chain if requested
        if msg_type == 102:
                sent_msg = {'code': 102, 'node': self.minerNum, 'msg': msg} #msg should contain full blockchain list
                    
        # for broadcast, node == 'all' and for specific node, node= node_id        
        if node == 'all':
            for node_id in self.allNodes:
                if node_id != self.minerNum:
                    self.comm.send_msg(node_id, sent_msg)
        else:
            self.comm.send_msg(node, sent_msg)

    # converts dict chain to block chain          
    def convertToBlockChain(self, dictchain):
        blockchain = []
        for block in dictchain:
                block = json.loads(block)
                blockchain.append(Block(block["index"], block["transaction"], block["timestamp"], block["previous_hash"], block["nonce"]))
        return blockchain

    # converts dict chain to block chain          
    def convertToDictChain(self, blockchain):
        dictchain = []
        for block in blockchain:
                dictchain.append(json.dumps(block.__dict__, sort_keys=True))
        return dictchain

    def handleReceivedMessage(self, msg):
        msg_type = msg.get('code')
        sent_node = msg.get('node')
        if msg_type == 100:         #handle single block 
            received_block = msg.get('msg')
            print('Received Last block from node {0} :::: {1}'.format(sent_node, received_block))
            #verify block
            block = self.convertToBlockChain(received_block)[0]
            #if true add to blockchain
            valid = self.blockchain.verifyBlock(block)
            if valid:
                chain = self.blockchain.getChain()
                chain.append(block)
                overwritten = self.log.overwriteChain(chain)
                if overwritten:
                    print("Block: " + json.dumps(block.__dict__, sort_keys=True, indent=3) + "\nhas been appended to the chain")
            # request full chain to overwrite chain
            else:
                if self.blockchain.getChainLength() <= block.index:
                    print("Potential longer chain found, requesting full chain")
                    self.sendMessage(101, sent_node, msg=None)
            
        if msg_type == 101:
            # sent_node requested for full chain
            # send full chain to sent_node
            blockchain = self.blockchain.getChain()
            dictchain = self.convertToDictChain(blockchain)
            self.sendMessage(102, sent_node, dictchain)
            print("Sent full chain to miner " + str(sent_node))

                    
        if msg_type == 102:
            # received full chain from sent_node
            full_chain = msg.get('msg')
            # process full chain
            chain = self.convertToBlockChain(full_chain)
            print("Verifying new chain")
            valid = self.blockchain.verifyChain(chain)
            if valid:
                print("Attempting to overwrite new chain")
                overwritten = self.log.overwriteChain(chain)
                if overwritten:
                    print("Current chain has been overwritten")
                else:
                    print("Current chain hasn't been overwritten")
            else:
                print("Chain not valid")