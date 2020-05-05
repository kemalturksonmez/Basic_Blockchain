# -*- coding: utf-8 -*-
"""
Created on Sat Feb 29 14:42:51 2020

@author: asadc
"""

import pandas as pd
import socket
import Server
import client
import threading
import json
from time import sleep
import numpy as np
import os.path

class Communication():
        def __init__(self, port=None):
                self.node_id = 0
                self.link_in = {}
                self.link_out = {}
                self.player_link_out = {}
                self.thread_list = []
                self.ui_receive = None
                self.restart = False
                self.port = port
                
        def init_network(self):
                df = pd.read_csv('network_adrs.csv', names=['node_id', 'adrs', 'port'])
                sys_ip = socket.gethostbyname(socket.gethostname())
                for index, row in df.iterrows():
                       adrs = eval(row['adrs'])
                       # if  adrs== sys_ip: #ourself
                       if self.port == row['port']:
                                self.node_id = int(row['node_id'])
                                node_srvr = Server.SERVER((adrs, row['port']))
                                self.link_in[row['node_id']] = node_srvr
                                self.thread_list.append(threading.Thread(target= node_srvr.run).start())
                                
                for index, row in df.iterrows():
                        adrs = eval(row['adrs'])
                        #if  adrs != sys_ip:
                        if self.port != row['port']:
                                node_client = client.CLIENT((adrs, row['port']))                               
                                self.link_out[row['node_id']] = node_client
                                self.thread_list.append(threading.Thread(target=node_client.run).start())
                                self.check_restart()
                                if self.restart:
                                        print('in restart send msg')
                                        sleep(3)
                                        self.send_msg(row['node_id'], {'code': 2, 'node' : self.node_id, 'msg': 'server restarted'})
                                        
                                
        def receive_msg(self):
                conn = self.link_in.get(self.node_id)
                #return self.handleMultipleReceive(conn.get_msg(type='GET'))
                return json.loads(conn.get_msg(type='GET'))
        
        def handleMultipleReceive(self, msg):
                msg = msg.replace('}{', '};{')
                msg_list = msg.split(';')
                msg_list = [json.loads(item) for item in msg_list]
                return msg_list
        
        #### Message Types ####
        # code 2: server restarted
        
        
        def display_received_msg(self):
                while True:
                        if self.ui_receive != None:
                                msg = self.receive_msg()                                
                                if msg.get('code') == 1:
                                        print("Received in Node {0} from Node {1} ::: {2}".format(self.node_id, msg.get('node'), msg.get('log')))
                                        
                                        
                                elif msg.get('code') == 2:
                                        print("Received in Node {0} ::: {1}".format(self.node_id, msg.get('msg')))
                                        node = msg.get('node')
                                        df = pd.read_csv('network_adrs.csv', names=['node_id', 'adrs', 'port'])
                                        row = df[df['node_id'] == node].iloc[0]
                                        node_client = client.CLIENT((eval(row['adrs']), row['port']))
                                        self.link_out[row['node_id']] = node_client
                                        self.thread_list.append(threading.Thread(target=node_client.run).start())
                                        
                                elif msg.get('code') > 2:
                                        self.ui_receive.handleReceivedMessage(msg)
                                
        
        def send_msg(self, node_id, msg):
                msg = json.dumps(msg)
                conn = self.link_out.get(node_id)
                conn.delivery_msg(value=msg, type='PUT')
                
        def send_msg_player(self, node_id, msg):
                msg = json.dumps(msg)
                conn = self.player_link_out.get(node_id)
                conn.delivery_msg(value=msg, type='PUT')
        
        def set_ui_receive(self, ui):
                self.ui_receive = ui
                
        def get_self_process_id(self):
                return self.node_id
                
        def get_num_of_processes(self):
                return len(self.link_out)
        
        def check_restart(self):
                self.restart = os.path.isfile(str(self.node_id) + '/log.json')
                                
                
                
                
                
        