#!/usr/bin/env python3
"""
    @author: Kemal Turksonmez
"""
import os
import json
from block import Block
class Log:
    def __init__(self):
        if not os.path.isfile('log.json'):
            logfile = open('log.json', 'w+')
            logfile.close()
    
    # returns chain from file
    def getChain(self):
        logfile = open('log.json', 'r')
        data = logfile.read()
        print(data)
        if not data == "":
            chain = json.loads(data)
            return chain
        return []
    
    # overwrites chain with new chain
    def overwriteChain(self, chain):
        logfile = open('log.json', 'w')
        logfile.write("[\n")
        for block in chain:
            logfile.write(json.dumps(block.__dict__, sort_keys=True, indent=3))
            if block != chain[-1]:
                logfile.write(",\n")
        logfile.write("\n]")
        logfile.close()


    