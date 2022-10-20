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
verbose = True
my_private, my_public = Signatures.generate_keys()

def StopAll() :
    global break_now
    break_now = True

def walletServer(my_addr):
    global break_now
    global head_blocks
    try :
        head_blocks = TxBlock.loadBlocks("WalletBlocks.dat")
    except :
        if verbose : print("Wallet : No previous blocks found. Starting fresh.")
        head_blocks = TxBlock.loadBlocks("Genesis.dat")
    server = SocketUtils.newServerConnection('localhost',5006)
    while not break_now :
        newBlock = SocketUtils.recvObj(server)
        if isinstance(newBlock, TxBlock.TxBlock) :
            if verbose : print("Wallet : New block has been received by walletServer \n")
            found = False
            for b in head_blocks:
                if b == None :
                    if not newBlock.is_valid():
                        if verbose : print("Error! New block is invalid.")
                    else :
                        head_blocks.remove(b)
                        head_blocks.append(newBlock)
                        found = True
                        if verbose : print("Wallet : head blocks is empty, therefore newBlock is head block \n")             
                elif newBlock.previousHash == b.computeHash():
                    newBlock.previousBlock = b
                    if not newBlock.is_valid():
                        if verbose : print("Error! New block is invalid.")
                    else :
                        found = True
                        head_blocks.remove(b)
                        head_blocks.append(newBlock)
                else :
                    currentBlock = b
                    while currentBlock != None :
                        if newBlock.previousHash == currentBlock.computeHash():
                            newBlock.previousBlock = currentBlock
                            if not newBlock.is_valid():
                                if verbose : print("Error! New block is invalid.")
                                break
                            else :
                                if not newBlock in head_blocks :
                                    if verbose : print("Wallet : New head block has been found.")
                                    head_blocks.append(newBlock)
                                    found = True
                                break
                        currentBlock = currentBlock.previousBlock
            if not found :
                if verbose : print("Error! Could'nt find a parent for newBlock")
                #TODO handle orphaned blocks
    server.close()
    TxBlock.saveBlocks(head_blocks, "WalletBlocks.dat")
    return True

def getBalance(pu_key):
    currentBlock = TxBlock.findLongestBlockchain(head_blocks)
    return currentBlock.getBalance(pu_key)

def sendCoins(pu_send, amt_send, pr_send, pu_recv, amt_recv, miner_list):
    Tx = Transactions.Tx()
    Tx.add_input(pu_send, amt_send)
    Tx.add_output(pu_recv, amt_recv)
    Tx.sign(pr_send)
    for addr_ip, port in miner_list :
        if verbose : print("Wallet : Sending to " + addr_ip + ":" + str(port) + "\n")
        SocketUtils.sendObj(addr_ip, Tx, port)
    return True

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

    pr1, pu1 = Signatures.loadKeys("private.key", "public.key")
    pr2, pu2 = Signatures.generate_keys()
    pr3, pu3 = Signatures.generate_keys()

    #Query balances
    bal1 = getBalance(pu1)
    bal2 = getBalance(pu2)
    bal3 = getBalance(pu3)
    
    #Send coins
    sendCoins(miner_pu, 10, miner_pr, pu1, 10, miners)
    sendCoins(pu1, 0.1, pr1, pu2, 0.1, miners)
    sendCoins(pu1, 0.1, pr1, pu2, 0.1, miners)
    sendCoins(pu1, 0.1, pr1, pu2, 0.1, miners)
    sendCoins(pu1, 0.1, pr1, pu2, 0.1, miners)
    sendCoins(pu1, 0.1, pr1, pu2, 0.1, miners)
    sendCoins(pu1, 0.1, pr1, pu2, 0.1, miners)
    sendCoins(pu1, 0.1, pr1, pu2, 0.1, miners)
    sendCoins(pu1, 0.1, pr1, pu2, 0.1, miners)
    sendCoins(pu1, 0.1, pr1, pu2, 0.1, miners)
    sendCoins(pu1, 0.1, pr1, pu2, 0.1, miners)
    sendCoins(pu1, 0.1, pr1, pu3, 0.03, miners)
    sendCoins(pu1, 0.1, pr1, pu3, 0.03, miners)
    sendCoins(pu1, 0.1, pr1, pu3, 0.03, miners)
    sendCoins(pu1, 0.1, pr1, pu3, 0.03, miners)
    sendCoins(pu1, 0.1, pr1, pu3, 0.03, miners)
    sendCoins(pu1, 0.1, pr1, pu3, 0.03, miners)
    sendCoins(pu1, 0.1, pr1, pu3, 0.03, miners)
    sendCoins(pu1, 0.1, pr1, pu3, 0.03, miners)
    sendCoins(pu1, 0.1, pr1, pu3, 0.03, miners)
    sendCoins(pu1, 0.1, pr1, pu3, 0.03, miners)

    time.sleep(60)

    #Save/Load all blocks
    TxBlock.saveBlocks(head_blocks, "WalletBlocks.dat")
    head_blocks = TxBlock.loadBlocks("WalletBlocks.dat")
    
    #Query balances
    new1 = getBalance(pu1)
    new2 = getBalance(pu2)
    new3 = getBalance(pu3)

    #Verify balances
    if abs(new1-bal1+2.0-10) > 0.00000001:
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

    num_heads = len(head_blocks)
    sister = TxBlock.TxBlock(head_blocks[0].previousBlock.previousBlock)
    sister.previousBlock = None
    SocketUtils.sendObj('localhost', sister, 5006)
    time.sleep(10)
    if(len(head_blocks) == num_heads + 1):
        print("Success! New head_block created")
    else:
        print("Error! Failed to add sister block")

    StopAll()
    
    t1.join()
    t2.join()
    t3.join()

    print("Exit successful")
