#Miner

import SocketUtils
import Transactions
import TxBlock
import Signatures

wallet_list = ['localhost']
tx_list = []
head_blocks = [None]

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

def minerServer(my_ip, wallet_list, my_public_addr):
    # Open server connection
    server = SocketUtils.newServerConnection(my_ip)
    # Receive transactions
    for i in range(10) : 
        newTx = SocketUtils.recvObj(server)
        if isinstance(newTx, Transactions.Tx) and newTx.is_valid:
            tx_list.append(newTx)
        if len(tx_list) >= 2 :
            break
    print("Tx1 and Tx2 have been received")
    # Collect into block
    Block = TxBlock.TxBlock(findLongestBlockchain())
    for tx in tx_list : 
        Block.addTx(tx)
    print("Tx1 and Tx2 have been added into a new block")
    # Calculation of miner reward
    total_in, total_out = Block.count_totals()
    minerRewardTx = Transactions.Tx()
    minerRewardTx.add_output(my_public_addr, 25.0 + total_in - total_out)
    Block.addTx(minerRewardTx)
    # Find nonce
    for i in range(10):
        Block.find_nonce()
        if Block.good_nonce():
            break
    if not Block.good_nonce():
        print("Error: Couldn't find nonce")
    print("Nonce has been found")
    # Send that block to each in wallet list
    for addr_ip in wallet_list :
        SocketUtils.sendObj(addr_ip, Block, 5006)
    head_blocks.remove(Block.previousBlock)
    head_blocks.append(Block)
    return False

my_pr, my_pu = Signatures.generate_keys()
minerServer('localhost', wallet_list, my_pu)
