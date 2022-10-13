#Wallet

import SocketUtils
import Transactions
import TxBlock
import pickle
import Signatures

head_blocks = [None]
wallets = [('localhost', 5006)]
miners = [('localhost', 5005)]
break_now = False
verbose = False
my_private, my_public = Signatures.generate_keys()

def StopAll() :
    global break_now
    break_now = True

def walletServer(my_addr):
    global break_now
    global head_blocks
    server = SocketUtils.newServerConnection('localhost',5006)
    while not break_now :
        newBlock = SocketUtils.recvObj(server)
        if isinstance(newBlock, TxBlock.TxBlock) :
            if verbose : print("Wallet : New block has been received by walletServer \n")
            if head_blocks == [None] :
                if not newBlock.is_valid():
                    print("Error! New block is invalid.")
                else :
                    head_blocks = [newBlock]
                    if verbose : print("Wallet : head blocks is empty, therefore newBlock is head block \n")
            for b in head_blocks:
                if newBlock.previousHash == b.computeHash():
                    newBlock.previousBlock = b
                    if not newBlock.is_valid():
                        print("Error! New block is invalid.")
                    else :
                        head_blocks.remove(b)
                        head_blocks.append(newBlock)
    server.close()
    return True

def getBalance(pu_key):
    currentBlock = TxBlock.findLongestBlockchain(head_blocks)
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

def sendCoins(pu_send, amt_send, pr_send, pu_recv, amt_recv, miner_list):
    Tx = Transactions.Tx()
    Tx.add_input(pu_send, amt_send)
    Tx.add_output(pu_recv, amt_recv)
    Tx.sign(pr_send)
    for addr_ip, port in miner_list :
        if verbose : print("Wallet : Sending to " + addr_ip + ":" + str(port) + "\n")
        SocketUtils.sendObj(addr_ip, Tx, port)
    return True

def loadKeys(pr_file, pu_file) :
    return Signatures.loadPrivate(pr_file), Signatures.loadPublic(pu_file)

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

    import time
    import threading
    import Miner
    import Signatures
        
    miner_pr, miner_pu = Signatures.generate_keys()
    t1 = threading.Thread(target = Miner.minerServer, args = (('localhost', 5005),))
    t2 = threading.Thread(target = Miner.nonceFinder, args = (wallets, miner_pu))
    t3 = threading.Thread(target= walletServer, args=(('localhost', 5006),))
    t1.start()
    t2.start()
    t3.start()

    pr1, pu1 = loadKeys("private.key", "public.key")
    pr2, pu2 = Signatures.generate_keys()
    pr3, pu3 = Signatures.generate_keys()

    #Query balances
    bal1 = getBalance(pu1)
    bal2 = getBalance(pu2)
    bal3 = getBalance(pu3)
    
    #Send coins
    sendCoins(pu1, 1.0, pr1, pu2, 1.0, miners)
    sendCoins(pu1, 1.0, pr1, pu3, 0.3, miners)

    time.sleep(60)

    #Save/Load all blocks
    saveBlocks(head_blocks, "AllBlocks.dat")
    head_blocks = loadBlocks("AllBlocks.dat")
    
    #Query balances
    new1 = getBalance(pu1)
    new2 = getBalance(pu2)
    new3 = getBalance(pu3)

    #Verify balances
    if abs(new1-bal1+2.0) > 0.00000001:
        print("Error: Wrong balance for pu1")
    else :
        print("Success. Good balance for pu1")
    if abs(new2-bal2-1.0) > 0.00000001:
        print("Error: Wrong balance for pu2")
    else :
        print("Success. Good balance for pu2")
    if abs(new3-bal3-0.3) > 0.00000001:
        print("Error: Wrong balance for pu3")
    else :
        print("Success. Good balance for pu3")

    Miner.StopAll()
    StopAll()
    
    t1.join()
    t2.join()
    t3.join()

    print("Exit successful")
