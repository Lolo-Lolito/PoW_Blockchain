#EZCoin

import time
import Wallet
import Miner
import Signatures
import threading
import TxBlock

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
    try :
        my_public_addr = Signatures.loadPublic("public.key")
    except :
        print("No public.key Need to generate?")
    tMinerServer = threading.Thread(target = Miner.minerServer, args = ((my_ip, 5005),))
    tMinerClient = threading.Thread(target = Miner.nonceFinder, args = (wallets, my_public_addr))
    tMinerServer.start()
    tMinerClient.start()
    return True

def startWallet() :
    global tWalletServer
    global my_private, my_public
    my_private, my_public = Signatures.loadKeys("private.key", "public.key")
    tWalletServer = threading.Thread(target= Wallet.walletServer, args=((my_ip, 5006),))
    tWalletServer.start()
    return True

def stopMiner() :
    global tMinerClient
    global tMinerServer
    Miner.StopAll()
    if tMinerServer : tMinerServer.join()
    if tMinerClient : tMinerClient.join()
    tMinerServer = None
    tMierClient = None
    return True

def stopWallet() :
    global tWalletServer
    Wallet.StopAll()
    if tWalletServer : tWalletServer.join()
    tWalletServer = None
    return True

def getBalance(pu_key) :
    if not tWalletServer :
        print("Start the server by calling startWallet before checking balances")
        return 0.0
    return Wallet.getBalance(pu_key)

def sendCoins(pu_recv, amt, tx_fee) :
    Wallet.sendCoins(my_public, amt + tx_fee, my_private, pu_recv, amt)
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
    time.sleep(20)
    print(getBalance(other_public))
    print(getBalance(my_public))

    time.sleep(1)
    stopWallet()
    stopMiner()

    print(TxBlock.findLongestBlockchain(Miner.head_blocks).nonce)
    print(TxBlock.findLongestBlockchain(Miner.head_blocks).previousBlock.nonce)
    print(TxBlock.findLongestBlockchain(Miner.head_blocks).previousBlock.previousBlock.nonce)
    
