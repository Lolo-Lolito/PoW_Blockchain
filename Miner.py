#Miner

import SocketUtils
import Transactions
import TxBlock
import Signatures
import threading
import time


wallet_list = [('localhost', 5006)]
tx_list = []
head_blocks = [None]
break_now = False

def findLongestBlockchain():
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

def minerServer(my_addr):
    global tx_list
    global break_now
    global lock
    my_ip, my_port = my_addr
    # Open server connection
    server = SocketUtils.newServerConnection(my_ip, my_port)
    # Receive transactions
    while not break_now : 
        newTx = SocketUtils.recvObj(server)
        if isinstance(newTx, Transactions.Tx) and newTx.is_valid:
            tx_list.append(newTx)
            print("Received tx")
    return False

def nonceFinder(wallet_list, my_public_addr):
    global break_now
    # Collect into block
    while not break_now :
        Block = TxBlock.TxBlock(findLongestBlockchain())
        for tx in tx_list : 
                Block.addTx(tx)
        # Calculation of miner reward
        total_in, total_out = Block.count_totals()
        minerRewardTx = Transactions.Tx()
        minerRewardTx.add_output(my_public_addr, 25.0 + total_in - total_out)
        Block.addTx(minerRewardTx)
        # Find nonce
        print("Finding nonce...")
        Block.find_nonce(100000)
        if Block.good_nonce():
            print("Good nonce has been found")
            # Send that block to each in wallet list
            for addr_ip, port in wallet_list :
                print("Sending to " + addr_ip + ":" + str(port))
                SocketUtils.sendObj(addr_ip, Block, port)
            head_blocks.remove(Block.previousBlock)
            head_blocks.append(Block)
    return  True

if __name__ == "__main__":

    my_pr, my_pu = Signatures.generate_keys()
    t1 = threading.Thread(target = minerServer, args = (('localhost', 5005),))
    t2 = threading.Thread(target = nonceFinder, args = (wallet_list, my_pu))
    server = SocketUtils.newServerConnection('localhost',5006)
    t1.start()
    t2.start()
    pr1, pu1 = Signatures.generate_keys()
    pr2, pu2 = Signatures.generate_keys()
    pr3, pu3 = Signatures.generate_keys()

    Tx1 = Transactions.Tx()
    Tx2 = Transactions.Tx()

    Tx1.add_input(pu1, 4.0)
    Tx1.add_input(pu2, 1.0)
    Tx1.add_output(pu3, 4.8)
    Tx2.add_input(pu3, 4.0)
    Tx2.add_output(pu2, 4.0)
    Tx2.add_reqd(pu1)

    Tx1.sign(pr1)
    Tx1.sign(pr2)
    Tx2.sign(pr1)
    Tx2.sign(pr3)

    try :
        SocketUtils.sendObj('localhost',Tx1)
        print("Sent Tx1")
        SocketUtils.sendObj('localhost',Tx2)
        print("Sent Tx2")
    except:
        print("Error: Connection unsuccessful")

    for i in range(10):
        newBlock = SocketUtils.recvObj(server)
        if newBlock :
            break

    if newBlock.is_valid():
        print("Success! Block is valid")
    else :
        print("Error: Block is invalid")
    if newBlock.good_nonce():
        print("Success! Nonce is valid")
    else :
        print("Error: Block is invalid")
    for tx in newBlock.data:
        try :
            if tx.inputs[0][0] == pu1 and tx.inputs[0][1] == 4.0 :
                print("Tx1 is present")
        except :
                pass
        try :
            if tx.inputs[0][0] == pu3 and tx.inputs[0][1] == 4.0 :
                print("Tx2 is present")
        except :
                pass

    time.sleep(20)
    break_now = True
    time.sleep(10)
    server.close()
    
    t1.join()
    t2.join()

    print("Done!")
