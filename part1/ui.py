#!/usr/bin/env python3
"""
    @author: Kemal Turksonmez
"""
from blockchain import Blockchain
from log import Log
from transactions import Transactions
from time import sleep
import random
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
        #self.startUI()

    def startUI(self):
        canContinue = True
        while True:
            sleep(random.randint(10,20))
            canContinue = self.blockchain.mine()
            if not canContinue:
                inp = input("Would you like to quit?\n")
                if inp.lower() == "quit":
                    break
                else:
                    canContinue = True
            else:
                    self.broadcastLastBlock()


    def broadcastLastBlock(self):
        block = self.blockchain.getLastBlock().__dict__
        self.sendMessage(100, 'all', msg=block)
            

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
    
    def sendMessage(self, msg_type, node, msg=None):
        if msg_type == 100:         #send single block
            sent_msg = {'code': 100, 'node': self.minerNum, 'msg': msg}
            
        # ask for full chain to node if not verified
        #if msg_type == 101:
                #sent_msg = {'code': 101, 'node': self.minerNum}
                    
        # send full block chain if requested
        #if msg_type == 102:
                #sent_msg = {'code': 102, 'node': self.minerNum, 'msg': msg} #msg should contain full blockchain list
                    
        # for broadcast, node == 'all' and for specific node, node= node_id        
        if node == 'all':
            for node_id in self.allNodes:
                if node_id != self.minerNum:
                    self.comm.send_msg(node_id, sent_msg)
        else:
            self.comm.send_msg(node, sent_msg)
                    
                    
    def handleReceivedMessage(self, msg):
        msg_type = msg.get('code')
        sent_node = msg.get('node')
        if msg_type == 100:         #handle single block 
            received_block = msg.get('msg')
            print('Received Last block from node {0} :::: {1}'.format(sent_node, received_block))
            #handle received block
            
        #if msg_type == 101:
            #sent_node requested for full chain
            # send full chain to sent_node
                    
        #if msg_type == 102:
            #received full chain from sent_node
            # full_chain = msg.get('msg')
            #process full chain