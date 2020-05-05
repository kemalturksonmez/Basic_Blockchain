# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 19:15:26 2020

@author: asadc
"""

import socket
import threading
import queue
from time import sleep
import json

class SERVER():
        
        def __init__(self, address):
                self.server = None
                self.MAX_CLIENT_NO = 5
                self.client_list = []
                self.address = address
                self.delivery_queue = queue.Queue(maxsize= 200)
                self.get_message_queue = queue.Queue(maxsize= 200)
                
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
                                return json.dumps({'code' : -1})
                
        def client_thread(self, conn, address):
                #conn.send(str('server request accepted').encode())
                while True:
                        try:    #receive msg
                                msg = conn.recv(4096).decode()
                                if msg:  
                                        self.get_msg(value=msg)                                      
                                
                        except:
                                #print('something went wrong in port::', self.address[1])
                                #self.server.close()
                                pass
                        
        def send_msg(self):
                #send msg
                while True:
                        if not self.delivery_queue.empty():
                                if len(self.client_list) > 0:
                                        msg = self.delivery_msg(type='GET')
                                        for client in self.client_list:
                                                client[0].send(msg.encode())
                                
                                
        def run(self):
                
                self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
                self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) 
                self.server.bind(self.address)
                print('server started with address: ', self.address[0])
                self.server.listen(self.MAX_CLIENT_NO)
                #send msg based on queue
                #threading.Thread(target=self.send_msg).start()
                while True:
                        #accepts connection
                        conn, add = self.server.accept()
                        self.client_list.append((conn, add))
                        print(add[0] + ' is connected!!!')
                        #start a thread for each user
                        threading.Thread(target=self.client_thread,args=(conn,add)).start()
                        
                self.server.close()            