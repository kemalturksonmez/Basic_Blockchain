#!/usr/bin/env python3
"""
    @author: Kemal Turksonmez
"""
import os
class Transactions:
    def __init__(self, minerNum):
        self.spentFileLoc = str(minerNum) + '/SpentTransactions.txt'
        self.unspentFileLoc = str(minerNum) + '/UnspentTransactions.txt'
        if not os.path.isfile(self.unspentFileLoc):
            transFile = open(self.unspentFileLoc, 'w+')
            ogFile = open('transactionsOriginal.txt', 'r')
            line = ogFile.readline()
            #counter = 0
            while line != "":
                #if counter % 2 == minerNum % 2:
                transFile.write(line)
                #counter += 1
                line = ogFile.readline()
            ogFile.close()
            transFile.close()
            transFile = open(self.spentFileLoc, 'a+')
            transFile.close()
    
    # gets transactions from file
    def getUnspentTransactions(self):
        transFile = open(self.unspentFileLoc, 'r')
        transactions = []
        line = transFile.readline()
        while line != "":
            # get string and remove line break
            transactions.append(line.replace("\n", ""))
            line = transFile.readline()
        transFile.close()
        return transactions

    # gets transactions from file
    def getSpentTransactions(self):
        transFile = open(self.spentFileLoc, 'r')
        transactions = []
        line = transFile.readline()
        while line != "":
            # get string and remove line break
            transactions.append(line.replace("\n", ""))
            line = transFile.readline()
        transFile.close()
        return transactions

    # writes remaining set of transactions
    def overwriteSpentTransactions(self, transactions):
        transFile = open(self.spentFileLoc, 'w')
        for line in transactions:
            transFile.write(line + "\n")
        transFile.close()

    # write current unspent transations
    def overwriteUnspentTransactions(self, transactions):
        transFile = open(self.unspentFileLoc, 'w+')
        for line in transactions:
            transFile.write(line + "\n")
        transFile.close()