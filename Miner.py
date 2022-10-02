#Miner

import SocketUtils
import TxBlock

wallet_list = ['localhost']

def minerServer(my_ip, wallet_list):
    # Open server connection
    server = SocketUtils.newServerConnection(my_ip)
    # Receive 2 transactions
    Tx1 = SocketUtils.recvObj(server)
    Tx2 = SocketUtils.recvObj(server)
    print("Tx1 and Tx2 have been received")
    # Collect into block
    Block = TxBlock.TxBlock(None)
    Block.addTx(Tx1)
    Block.addTx(Tx2)
    print("Tx1 and Tx2 have been added into a new block")
    # Find nonce
    Block.find_nonce()
    print("Nonce has been found")
    # Send that block to each in wallet list
    for addr_ip in wallet_list :
        SocketUtils.sendObj(addr_ip, Block, 5006)
    return False

if __name__ == '__main__':
    minerServer('localhost', wallet_list)
