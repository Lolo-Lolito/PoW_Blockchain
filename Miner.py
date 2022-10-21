#Miner

import SocketUtils
import Transactions
import TxBlock
import pickle
import copy

wallet_list = [('localhost', 5006)]
tx_list = []
head_blocks = [None]
break_now = False
verbose = True
minerRewardTxSize = 552

def StopAll() :
    global break_now 
    break_now = True

def minerServer(my_addr):
    global tx_list
    global break_now
    try :
        tx_list = loadTxList("Txs.dat")
        if verbose : print("Miner : Loaded tx_list has " + str(len(tx_list)) + " Txs.")
    except :
        if verbose : print("Miner : No previous Txs. Starting from fresh")
        tx_list = []
    my_ip, my_port = my_addr
    # Open server connection
    server = SocketUtils.newServerConnection(my_ip, my_port)
    # Receive transactions
    while not break_now : 
        newTx = SocketUtils.recvObj(server)
        if isinstance(newTx, Transactions.Tx) and newTx.is_valid:
            tx_list.append(newTx)
            if verbose : print("Miner : Received tx \n")
    if verbose : print("Miner : saving " + str(len(tx_list)) + " txs to Txs.dat")
    saveTxList(tx_list, "Txs.dat")
    return True

def nonceFinder(wallet_list, my_public_addr):
    global break_now
    global tx_list
    try :
        head_blocks = TxBlock.loadBlocks("AllBlocks.dat")
    except :
        print("Miner : No previous blocks found. Starting fresh.")
        try :
            head_blocks = TxBlock.loadBlocks("Genesis.dat")
        except :
            head_blocks = [None]
    # Collect into block
    while not break_now :
        Block = TxBlock.TxBlock(TxBlock.findLongestBlockchain(head_blocks))
        placeholder = Transactions.Tx()
        placeholder.add_output(my_public_addr, 25.0)
        Block.addTx(placeholder)
        #TODO sort tx_list by tx fee per byte
        for tx in tx_list :
            Block.addTx(tx)
            if not Block.check_transaction() :
                Block.removeTx(tx)
                tx_list.remove(tx)
            if not Block.check_size() :
                Block.removeTx(tx)
                break
        Block.removeTx(placeholder)
        if verbose : print("Miner : new block has " + str(len(Block.data)) + " txs.")          
        # Calculation of miner reward
        total_in, total_out = Block.count_totals()
        minerRewardTx = Transactions.Tx()
        minerRewardTx.add_output(my_public_addr, 25.0 + total_in - total_out)
        Block.addTx(minerRewardTx)
        # Find nonce
        if verbose : print("Miner : Finding nonce...\n")
        Block.find_nonce(10000)
        if Block.good_nonce():
            if verbose : print("Miner : Good nonce has been found\n")
            head_blocks.remove(Block.previousBlock)
            head_blocks.append(Block)
            # Send that block to each in wallet list
            savPrev = Block.previousBlock
            Block.previousBlock = None
            for addr_ip, port in wallet_list :
                if verbose : print("Miner : Sending to " + addr_ip + ":" + str(port) + "\n")
                SocketUtils.sendObj(addr_ip, Block, port)
            Block.previousBlock = savPrev
            # Remove used txs from tx_list
            tx_list = [tx for tx in tx_list if not tx in Block.data]
    TxBlock.saveBlocks(head_blocks, "AllBlocks.dat")
    return  True

def loadTxList(filename) :
    loadfile = open(filename, "rb")
    tx_list = pickle.load(loadfile)
    loadfile.close()
    return tx_list

def saveTxList(the_list, filename) :
    savefile = open(filename, "wb")
    pickle.dump(the_list, savefile)
    savefile.close()
    return True

if __name__ == "__main__":

    import threading
    import time
    import Signatures
    
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

    new_tx_list = [Tx1, Tx2]
    saveTxList(new_tx_list, "Txs.dat")
    new_new_tx_list = loadTxList("Txs.dat")
    
    for tx in new_new_tx_list :
        try :
            SocketUtils.sendObj('localhost',tx)
            print("Wallet : Sent Tx \n")
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
    StopAll()
    time.sleep(10)
    server.close()
    
    t1.join()
    t2.join()

    print("Done!")
