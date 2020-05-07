# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 22:54:57 2020

@author: asadc
"""

import socket
from time import sleep
import queue
import threading

class CLIENT():
        
        def __init__(self, host_adrs):
                self.host_adrs = host_adrs
                self.client = None
                self.delivery_queue = queue.Queue(maxsize= 200)
                self.get_message_queue = queue.Queue(maxsize= 200)
                threading.Thread(target=self.send_msg).start()
                
        def delivery_msg(self, value=None, type= 'PUT') :
                if type == 'PUT':
                        self.delivery_queue.put(value)
                if type == 'GET':
                        return self.delivery_queue.get()
        def get_msg(self, value=None, type= 'PUT') :
                if type == 'PUT':
                        self.get_message_queue.put(value)
                if type == 'GET':
                        if not self.get_message_queue.empty():
                                return self.get_message_queue.get()
                        else:
                                return {'code' : -1}
        def send_msg(self):
                while(True):
                        if self.client != None:
                                #send msg
                                if not self.delivery_queue.empty():
                                        msg = self.delivery_msg(type='GET')
                                        try:
                                                self.client.send(msg.encode())
                                        except:
                                                #print('sending failed ::: ', self.host_adrs[1])
                                                pass
                                
                
        def run(self):
                self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                #while self.client.connect(self.host_adrs):
                sleep(1)
                while True:
                        try:
                                self.client.connect(self.host_adrs)
                                #self.client.send('{\"code\" : -2, \"msg\": \"connected to server\"}'.encode())
                                break
                        except:
                                #print('connecting ::: ', self.host_adrs[1])
                                sleep(1)
                                continue
                                        
