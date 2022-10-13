#EZCoin

import time
import Wallet

wallets = []
miners = []
my_ip = 'localhost' 

def startMiner() :
    #Start nonceFinder
    #Sart minerServer
    #Load tx_list
    #Load head_blocks
    #Load public keys
    return True

def startWallet() :
    #Start WalletServer
    #Load public and private keys
    #Load head_blocks
    return True

def stopMiner() :
    #Stop nonceFinder
    #Stop MinerServer
    #Save tx_list
    #Save head_blocks
    return True

def stopWallet() :
    #Stop walletServer
    #Save head_blocks
    return True

def getBalance(pu_key) :
    return 0.0

def sendCoins(pu_recv, amt, tx_fee) :
    return True

def makeNewKeys() :
    return None, None

if __name__ == "__main__":
    startMiner()
    startWallet()
    other_public = b'-----BEGIN PUBLIC KEY-----\nMIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEA214CylTA7WRA+QjOatF3\nkm/w3es6yXKbmugRNEwv9yZwfPJUoE1VppMjJttFr9VaKxmyIh7zW6s4MrpB7pcu\nUG4vceczZzZIbzU2gE1j+YD2n9uDHtHFCb6ec9KpQw7hG4McY+nfhFsxJ2ibhVuN\nSGMjmV6hfJ8+iO6WjMqaUntx0I7l9xycdQxat6qLESKFNq6AhI2Fb5CYKI0U59il\nVRWzVxV7e0hw3Idvu+TugdBoVDFtOXQ5lGDBc447Y8qTr2qPiBppPQrmMZ+O/fDx\niFBJajPLRSWeYqsMAetiyp94DoOVt+H8JjhMhsZeD3b3TBq4GfGq5IprYlWexGl1\nbwIDAQAB\n-----END PUBLIC KEY-----\n'
    time.sleep(2)
    print(getBalance(Wallet.my_public))
    sendCoins(other_public, 1.0, 0.001)
    print(getBalance(other_public))
    print(getBalance(Wallet.my_public))

    time.sleep(1)
    stopWallet()
    stopMiner()
