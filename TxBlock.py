#TxBlock

from Blockchain import CBlock
from Signatures import generate_keys, sign, verify
from Transactions import Tx
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives import hashes
import pickle
import time
import random
import copy
import Wallet

reward = 25.0
zeroHashNumber = 1
nextCharLimit = 3
blockSizeLimit = 10000
verbose = False

class TxBlock (CBlock):
    nonce = "AAAAAAAAAA"

    def __init__(self, previousBlock) :
        super(TxBlock, self).__init__([],previousBlock)

    def addTx(self, Tx_in) :
        self.data.append(Tx_in)

    def removeTx(self, Tx_in) :
        self.data.remove(Tx_in)

    def count_totals(self):
        total_in = 0
        total_out = 0
        for tx in self.data:
            for addr, amt in tx.inputs:
                total_in = total_in + amt
            for addr, amt in tx.outputs:
                total_out = total_out + amt     
        return total_in, total_out

    def check_size(self):
        l_block = copy.deepcopy(self)
        l_block.previousBlock = None
        if len(pickle.dumps(l_block)) > blockSizeLimit :
            return False
        return True

    def getBalance(self, pu_key):
        currentBlock = self
        balance = 0.0
        while currentBlock != None :
            for tx in currentBlock.data :
                for pu, amt in tx.inputs :
                    if pu == pu_key:
                        balance = balance - amt
                for pu, amt in tx.outputs :
                    if pu == pu_key :
                        balance = balance + amt
            currentBlock = currentBlock.previousBlock
        return balance

    def check_balance(self) :
        for tx in self.data :
            for addrInput, sendAmt in tx.inputs :
                if self.getBalance(addrInput) < 0 : return False
            for addrOutput, recvAmt in tx.outputs :
                if self.getBalance(addrOutput) < 0 : return False
        return True

    def is_valid(self):
        if not super(TxBlock, self).is_valid():
            if verbose : print("Error : Block basis is invalid")
            return False
        for tx in self.data:
            if not tx.is_valid():
                if verbose : print("Error : a Tx is invalid")
                return False
        total_in, total_out = self.count_totals()
        if total_out - total_in - reward > 0.000000000001:
            if verbose : print("Error : Block total amount distribution is invalid")
            return False
        if not self.check_size():
            if verbose : print("Error : Block exceeds block limit")
            return False
        if not self.check_balance():
            if verbose : print("Error : Error in balance")
            return False
        return True

    def good_nonce(self):
        expectedHash = bytes("".join(['\x00' for i in range(zeroHashNumber)]),"utf-8")
        digest = hashes.Hash(hashes.SHA256())
        digest.update(bytes(str(self.data),"utf-8"))
        digest.update(bytes(str(self.nonce),"utf-8"))
        digest.update(bytes(str(self.previousHash),"utf-8"))
        calculatedHash = digest.finalize()
        for i in range(len(expectedHash)) :
            if calculatedHash[i] != expectedHash[i] :
                return False
        return int(calculatedHash[zeroHashNumber]) < nextCharLimit

    def find_nonce(self, n_iter):
        nonceLength = 10
        for i in range(n_iter) :
            self.nonce = [chr(random.randint(0,0xFF)) for i in range(nonceLength)]
            self.nonce = "".join(self.nonce)
            if self.good_nonce() == True :
                break
        return self.nonce

def findLongestBlockchain(head_blocks):
    longest = -1
    long_head = None
    for b in head_blocks:
        current = b
        this_len = 0
        while current != None :
            this_len = this_len + 1
            current = current.previousBlock
        if this_len > longest :
            long_head = b
            longest = this_len
    return long_head

def saveBlocks(block_list, filename) :
    savefile = open(filename, "wb")
    pickle.dump(block_list, savefile)
    savefile.close()
    return True

def loadBlocks(filename) :
    loadfile = open(filename, "rb")
    block_list = pickle.load(loadfile)
    loadfile.close()
    return block_list

if __name__ == "__main__" :
    pr1, pu1 = generate_keys()
    pr2, pu2 = generate_keys()
    pr3, pu3 = generate_keys()

    Tx1 = Tx()
    Tx1.add_input(pu1, 1)
    Tx1.add_output(pu2, 1)
    Tx1.sign(pr1)

    if Tx1.is_valid():
        print("Success ! Tx is valid")

    message = b"Some text"
    sig = sign(message, pr1)

    savefile = open("tx.dat", "wb")
    pickle.dump(Tx1, savefile)
    savefile.close()

    loadfile = open("tx.dat", "rb")
    newTx = pickle.load(loadfile)

    if newTx.is_valid():
        
        print("Success ! Loaded Tx is valid")
        
    loadfile.close()

    root = TxBlock(None)
    mine1 = Tx()
    mine1.add_output(pu1, 8.0)
    mine1.add_output(pu2, 8.0)
    mine1.add_output(pu3, 8.0)

    root.addTx(Tx1)
    root.addTx(mine1)

    Tx2 = Tx()
    Tx2.add_input(pu2,1.1)
    Tx2.add_output(pu3, 1)
    Tx2.sign(pr2)
    root.addTx(Tx2)

    B1 = TxBlock(root)

    Tx3 = Tx()
    Tx3.add_input(pu3,1.1)
    Tx3.add_output(pu1, 1)
    Tx3.sign(pr3)
    B1.addTx(Tx3)
    Tx4 = Tx()
    Tx4.add_input(pu1,1)
    Tx4.add_output(pu2, 1)
    Tx4.add_reqd(pu3)
    Tx4.sign(pr1)
    Tx4.sign(pr3)
    B1.addTx(Tx4)
    start = time.time()
    print(B1.find_nonce(1000000))
    elapsed = time.time() - start
    print("elapsed time :" + str(elapsed) + " s.")
    if elapsed < 60:
        print("ERROR! Mining is too fast")
    if B1.good_nonce():
        print("Sucess! Nonce is good !")
    else :
        print("ERROR! Bad nonce")

    savefile = open("block.dat", "wb")
    pickle.dump(B1,savefile)
    savefile.close()

    loadfile = open("block.dat", "rb")
    load_B1 = pickle.load(loadfile)

    loadfile.close()

    for b in [root, B1, load_B1, load_B1.previousBlock]:
        if b.is_valid():
            print("Success ! Valid block")
        else :
            print("ERROR! Bad block")

    if load_B1.good_nonce():
        print("Sucess! Nonce is good after save and load!")
    else :
        print("ERROR! Bad nonce after save and load!")
        
    B2 = TxBlock(B1)
    Tx5 = Tx()
    Tx5.add_input(pu3,1)
    Tx5.add_output(pu1, 100)
    Tx5.sign(pr3)
    B2.addTx(Tx5)

    load_B1.previousBlock.addTx(Tx4)
    for b in [B2, load_B1]:
        if b.is_valid():
            print("ERROR! Bad block verified.")
        else:
            print("Success! Bad blocks detected")

    # Test mining reward and tx fees
    pr4, pu4 = generate_keys()
    B3 = TxBlock(B2)
    B3.addTx(Tx2)
    B3.addTx(Tx3)
    B3.addTx(Tx4)
    Tx6 = Tx()
    Tx6.add_output(pu4, 25)
    B3.addTx(Tx6)
    if B3.is_valid() :
        print("Success ! Block reward succeeds")
    else:
        print("ERROR! Block reward fail")

    B4 = TxBlock(B3)
    B4.addTx(Tx2)
    B4.addTx(Tx3)
    B4.addTx(Tx4)
    Tx7 = Tx()
    Tx7.add_output(pu4, 25.2)
    B4.addTx(Tx7)
    if B4.is_valid() :
        print("Success ! Tx fees succeeds")
    else:
        print("ERROR! Tx fees fail")

    #Greedy minor
    B5 = TxBlock(B4)
    B5.addTx(Tx2)
    B5.addTx(Tx3)
    B5.addTx(Tx4)
    Tx8 = Tx()
    Tx8.add_output(pu4, 26.2)
    B5.addTx(Tx8)
    if not B5.is_valid() :
        print("Success ! Greedy minor detetected")
    else:
        print("ERROR! Greedy minor not detected")      
    
    B6 = TxBlock(B4)
    this_pu = pu4
    this_pr = pr4
    for i in range(30) :
        newTx = Tx()
        new_pr, new_pu = generate_keys()
        newTx.add_input(this_pu, 0.3)
        newTx.add_output(new_pu, 0.3)
        newTx.sign(this_pr)
        B6.addTx(newTx)
        this_pu, this_pr = new_pu, new_pr
        savePrev = B6.previousBlock
        B6.previousBlock = None
        this_size = len(pickle.dumps(B6))
        B6.previousBlock = savePrev
        if B6.is_valid() and this_size > 10000 :
            print("Error ! Big blocks are valid: size = " + str(this_size))
        elif (not B6.is_valid()) and this_size <= 10000 :
            print("Error! Small blocks are invalid: size = " + str(this_size))
        else:
            print("Success! Block size check passed.")

    overspend = Tx()
    overspend.add_input(pu1, 45.0)
    overspend.add_output(pu2, 44.5)
    overspend.sign(pr1)
    B7 = TxBlock(B1)
    B7.addTx(overspend)
    if B7.is_valid() :
        print("Error! Overspend not detected")
    else :
        print("Success! Overspend detected")

    overspend1 = Tx()
    overspend1.add_input(pu1, 5.0)
    overspend1.add_output(pu2, 4.5)
    overspend1.sign(pr1)
    overspend2 = Tx()
    overspend2.add_input(pu1, 15.0)
    overspend2.add_output(pu3, 14.5)
    overspend2.sign(pr1)
    overspend3 = Tx()
    overspend3.add_input(pu1, 5.0)
    overspend3.add_output(pu4, 4.5)
    overspend3.sign(pr1)
    overspend4 = Tx()
    overspend4.add_input(pu1, 8.0)
    overspend4.add_output(pu2, 4.5)
    overspend4.sign(pr1)
    B8 = TxBlock(B1)
    B8.addTx(overspend1)
    B8.addTx(overspend2)
    B8.addTx(overspend3)
    B8.addTx(overspend4)
    if B8.is_valid() :
        print("Error! Overspend not detected")
    else :
        print("Success! Overspend detected")    
