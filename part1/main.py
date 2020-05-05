#!/usr/bin/env python3
"""
    @author: Kemal Turksonmez
"""
from ui import UI
import threading
import comm
import sys
from time import sleep

threadObj = []
port = sys.argv[1]
#port = 5001
print(port)
commn = comm.Communication(int(port))
commn.init_network()

lock = threading.Lock()
minerNum = commn.get_self_process_id()
ui = UI(minerNum, lock, commn)

sleep(10)

threadObj.append(threading.Thread(target= commn.display_received_msg ))
threadObj.append(threading.Thread(target= ui.startUI ))

for obj in threadObj: 
        obj.start()


