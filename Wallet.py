#Wallet

import SocketUtils
import Transactions
import Signatures
import time
import threading
import Miner

head_blocks = [None]
wallets = [('localhost', 5006)]
miners = [('localhost', 5005)]


def walletServer(my_addr):
    global head_blocks
    server = SocketUtils.newServerConnection('localhost',5006)
    for i in range(10):
        newBlock = SocketUtils.recvObj(server)
        if newBlock :
            print("New block has been received by walletServer ")
            print(newBlock.data)
            break
    server.close()
    if head_blocks == [None] :
        head_blocks = [newBlock]
        print("head blocks is empty, therefore newBlock has been append")
    for b in head_blocks:
        if newBlock.previousHash == b.computeHash():
            newBlock.previousBlock = b
            head_blocks.remove(b)
            head_blocks.append(newBlock)
    return True

def getBalance(pu_key):
    currentBlock = Miner.findLongestBlockchain()
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
    Tx.add_input(pu_send, amt_recv)
    Tx.add_output(pu_recv, amt_recv)
    Tx.sign(pr_send)
    for addr_ip, port in miner_list :
        print("Sending to " + addr_ip + ":" + str(port))
        SocketUtils.sendObj(addr_ip, Tx, port)
    return True

if __name__ == "__main__" :

    miner_pr, miner_pu = Signatures.generate_keys()
    t1 = threading.Thread(target = Miner.minerServer, args = (('localhost', 5005),))
    t2 = threading.Thread(target = Miner.nonceFinder, args = (wallets, miner_pu))
    t3 = threading.Thread(target= walletServer, args=(('localhost', 5006),))
    t1.start()
    t2.start()
    t3.start()

    pr1, pu1 = Signatures.generate_keys()
    pr2, pu2 = Signatures.generate_keys()
    pr3, pu3 = Signatures.generate_keys()

    #Query balances
    bal1 = getBalance(pu1)
    bal2 = getBalance(pu2)
    bal3 = getBalance(pu3)
    
    #Send coins
    sendCoins(pu1, 1.0, pr1, pu2, 1.0, miners)
    sendCoins(pu1, 1.0, pr1, pu3, 0.3, miners)

    time.sleep(120)

    #Query balances
    new1 = getBalance(pu1)
    new2 = getBalance(pu2)
    new3 = getBalance(pu3)

    #Verify balances
    if abs(new1-bal1+1.3) > 0.00000001:
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

    Miner.break_now = True
    
    t1.join()
    t2.join()
    t3.join()

    print("Exit successful")
