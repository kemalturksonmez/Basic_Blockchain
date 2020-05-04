# -*- coding: utf-8 -*-
"""
Created on Sun Mar 29 15:26:48 2020

@author: asadc
"""

import comm
#import raft
import sys
import threading
from time import sleep

threadObj = []
port = sys.argv[1]
#port = 5001
print(port)
commn = comm.Communication(int(port))
commn.init_network()
#raftProtocol = raft.Raft(commn, log)

sleep(10)

threadObj.append(threading.Thread(target= commn.display_received_msg ))
#threadObj.append(threading.Thread(target= raftProtocol.handleTimeout ))

for obj in threadObj: 
        obj.start()

