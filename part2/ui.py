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
        self.blockchain = Blockchain(self.log, self.transObj, minerNum)
        self.comm = comm
        self.allNodes = [i + 1 for i in range(1 + self.comm.get_num_of_processes())]
        self.comm.set_ui_receive(self)
        self.stakeMoney = random.randint(150, 200)
        
        self.clientProb = 0
        self.NumForgedBlock = 0
        self.blockForged = None
        self.signingPool = []
        self.setSigningPool()
        
        self.blockLen = 0
        self.votedFor = []
        self.winner = 0

    def startUI(self):
        while True:
            sleep(20)
            if random.random() <= self.calcProbability() and self.winner ==0:
                
                self.blockForged = self.blockchain.mine()
                if self.blockForged == -2:
                    break
                self.blockForged.signer = {self.minerNum : self.stakeMoney}
                #request votes from miners
                self.sendMessage(101, 'all')
            else:
                print('$$$ Whats Happening $$$')
    
    def setSigningPool(self):
        self.signingPool = [i for i in self.allNodes]
        self.signingPool.remove(self.minerNum)
        random.shuffle(self.signingPool)
        
    def calcProbability(self):
        if self.blockLen == 0:
            return 0.5
        self.clientProb = 1 - (self.NumForgedBlock  / self.blockLen  )
        return self.clientProb
        


    def broadcastLastBlock(self):
        # block = [self.blockchain.getLastBlock().__dict__]
        block = [json.dumps(self.blockchain.getLastBlock().__dict__, sort_keys=True)]
        self.sendMessage(100, 'all', msg=block)
            
    
    def sendMessage(self, msg_type, node, msg=None):
        #sleep(random.randint(1,4))
        if msg_type == 101:         #request vote
            self.votedFor.append(self.minerNum)
            sent_msg = {'code': 101, 'node': self.minerNum}
            
        # reply vote if not voted for anyone
        if msg_type == 102:
            if not self.votedFor:
                self.votedFor.append(node)
                sent_msg = {'code': 102, 'node': self.minerNum}
            else:
                sent_msg = {'code': -1, 'node': self.minerNum}
                    
        # notify all nodes about winner
        if msg_type == 103:
                sent_msg = {'code': 103, 'node': self.minerNum} 
                
        # send signing request to all miners
        if msg_type == 104:
                sent_msg = {'code': 104, 'node': self.minerNum, 'msg': msg} 
                
        # send signed block to winner
        if msg_type == 105:
                sent_msg = {'code': 105, 'node': self.minerNum, 'msg': msg} 
        
        # send verified block to all miners
        if msg_type == 106:
                sent_msg = {'code': 106, 'node': self.minerNum, 'msg': msg} 
                    
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
                block_ = Block(block["index"], block["transaction"], block["timestamp"], block["previous_hash"], block["validator"], block["signer"])
                block_.reward =block["reward"]
                blockchain.append(block_)
        return blockchain

    # converts dict chain to block chain          
    def convertToDictChain(self, blockchain):
        dictchain = []
        for block in blockchain:
                dictchain.append(json.dumps(block.__dict__, sort_keys=True))
        return dictchain
    
    def sendVerifiedBlock(self):
        self.winner = 0
        self.votedFor = []
        self.NumForgedBlock += 1
        
        self.setSigningPool()
        
        #add reward money to block
        self.blockForged = self.blockchain.addRewardMoney(self.blockForged)
        self.blockchain.appendBlockChain(self.blockForged)
        self.blockLen = self.blockchain.getChainLength()                
        print('## Winner ## Block ::: {2} ##Current Length ::: {0} ## NumBlocks ::: {1}'.format(self.blockLen, self.NumForgedBlock, self.blockForged.index))
        self.sendMessage(106, 'all', msg = self.blockForged.__dict__)
        

    def handleReceivedMessage(self, msg):
        msg_type = msg.get('code')
        sent_node = msg.get('node')
        if msg_type == 101:         #vote request from sent_node
            self.sendMessage(102, sent_node)
            
        if msg_type == 102:
            # received vote reply from sent_node
            self.votedFor.append(sent_node)
            if len(self.votedFor) > (len(self.allNodes)/2) and self.winner == 0:
                self.winner = self.minerNum
                self.sendMessage(103, 'all')
                sleep(2.5)
                if self.blockchain.checkSigner(self.blockForged):
                    signer_node = self.signingPool[0]
                    self.signingPool.remove(signer_node)
                    self.sendMessage(104, signer_node, msg=self.blockForged.__dict__)
                else:
                    self.sendVerifiedBlock()
                    
                
                

                    
        if msg_type == 103:
            # notification received from winner node
            self.winner = sent_node
            #wait until block received from winner
            
        if msg_type == 104:
            #received signing request from sent_node
            dict_block = msg.get('msg')
            block = self.convertToBlockChain([dict_block])[0]
            print('Signing Block Index ::: ', block.index)
            condition, block = self.blockchain.singBlock(block, self.stakeMoney)
            if condition:
                self.sendMessage(105, sent_node, msg=self.stakeMoney)
            else:
                print('Signing Failed for Block ::: ', block.index)
                
        if msg_type == 105:
            #received signed block from sent_node
            self.blockForged.signer[sent_node] = int(msg.get('msg'))  
            if self.blockchain.checkSigner(self.blockForged):
                print('#$#$# Alert ::: {0} from ::: {1}'.format(msg.get('msg'), sent_node))
                signer_node = self.signingPool[0]
                self.signingPool.remove(signer_node)
                self.sendMessage(104, signer_node, msg=self.blockForged.__dict__)
            else:
                self.sendVerifiedBlock()
            
            
        if msg_type == 106:
            # received block from winner to attach in chain
            dict_block = msg.get('msg')
            block = self.convertToBlockChain([dict_block])[0]            
            print('Veryfining Block Index ::: {0} from node ::: {1}'.format( block.index, sent_node))
            if self.blockchain.verifyBlock(block):
                self.blockchain.appendBlockChain(block)
                self.winner = 0
                self.votedFor = []
                self.blockLen = self.blockchain.getChainLength()
                print('Block Verified ## Current Chain Length ::: ', self.blockLen)
            
            
            