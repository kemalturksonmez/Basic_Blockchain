# -*- coding: utf-8 -*-
"""
Created on Mon May  4 22:29:24 2020

@author: asadc
"""

import os

try:
        os.remove('1/log.json')
        os.remove('1/SpentTransactions.txt')
        os.remove('1/UnspentTransactions.txt')
except:
        pass

try:
        os.remove('2/log.json')
        os.remove('2/SpentTransactions.txt')
        os.remove('2/UnspentTransactions.txt')
except:
        pass

try:
        os.remove('3/log.json')
        os.remove('3/SpentTransactions.txt')
        os.remove('3/UnspentTransactions.txt')
except:
        pass

