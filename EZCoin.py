#EZCoin

import time
import Wallet
import Miner
import Signatures
import threading

wallets = [('localhost', 5006)]
miners = [('localhost', 5005)]
my_ip = 'localhost'
my_private, my_public = None, None
tMinerClient = None
tMinerServer = None
tWalletServer = None

def startMiner() :
    global tMinerClient
    global tMinerServer
    Miner.tx_list = Miner.loadTxList("Txs.dat")
    Miner.head_blocks = Wallet.loadBlocks("AllBlocks.dat")
    my_public_addr = Signatures.loadPublic("public.key")
    tMinerServer = threading.Thread(target = Miner.minerServer, args = ((my_ip, 5005),))
    tMinerClient = threading.Thread(target = Miner.nonceFinder, args = (wallets, my_public_addr))
    tMinerServer.start()
    tMinerClient.start()
    return True

def startWallet() :
    global tWalletServer
    global my_private, my_public
    Wallet.head_blocks = Wallet.loadBlocks("AllBlocks.dat")
    my_private, my_public = Wallet.loadKeys("private.key", "public.key")
    tWalletServer = threading.Thread(target= Wallet.walletServer, args=(('localhost', 5006),))
    tWalletServer.start()
    return True

def stopMiner() :
    global tMinerClient
    global tMinerServer
    Miner.StopAll()
    Miner.saveTxList(Miner.tx_list, "Txs.dat")
    Wallet.saveBlocks(Miner.head_blocks, "AllBlocks.dat")
    tMinerServer.join()
    tMinerClient.join()
    return True

def stopWallet() :
    global tWalletServer
    Wallet.StopAll()
    Wallet.saveBlocks(Wallet.head_blocks, "AllBlocks.dat")
    tWalletServer.join()
    return True

def getBalance(pu_key) :
    return Wallet.getBalance(pu_key)

def sendCoins(pu_recv, amt, tx_fee) :
    Wallet.sendCoins(my_public, amt + tx_fee, my_private, pu_recv, amt, miners)
    return True

def makeNewKeys() :
    return Signatures.generate_keys()

if __name__ == "__main__":
    startMiner()
    startWallet()
    other_public = b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA214CylTA7WRA+QjOatF3\nkm/w3es6yXKbmugRNEwv9yZwfPJUoE1VppMjJttFr9VaKxmyIh7zW6s4MrpB7pcu\nUG4vceczZzZIbzU2gE1j+YD2n9uDHtHFCb6ec9KpQw7hG4McY+nfhFsxJ2ibhVuN\nSGMjmV6hfJ8+iO6WjMqaUntx0I7l9xycdQxat6qLESKFNq6AhI2Fb5CYKI0U59il\nVRWzVxV7e0hw3Idvu+TugdBoVDFtOXQ5lGDBc447Y8qTr2qPiBppPQrmMZ+O/fDx\niFBJajPLRSWeYqsMAetiyp94DoOVt+H8JjhMhsZeD3b3TBq4GfGq5IprYlWexGl1\nbwIDAQAB\n-----END PUBLIC KEY-----\n'
    time.sleep(2)
    print(getBalance(my_public))
    sendCoins(other_public, 1.0, 0.001)
    time.sleep(30)
    print(getBalance(other_public))
    print(getBalance(my_public))

    time.sleep(1)
    stopWallet()
    stopMiner()
