#Blockchain.py

from cryptography.hazmat.primitives import hashes

class someClass:
    string = None
    num = 12345
    def __init__(self, mystring):
        self.string = mystring
    def __repr__(self):
        return self.string + "-" + str(self.num)
    
class CBlock:
    data = None
    nonce = ''
    previousHash = None
    previousBlock = None
    def __init__(self, data, previousBlock):
        self.data = data
        self.previousBlock = previousBlock
        if self.previousBlock != None:
            self.previousHash = self.previousBlock.computeHash()
    def computeHash(self):
        digest = hashes.Hash(hashes.SHA256())
        digest.update(bytes(str(self.data),"utf-8"))
        digest.update(bytes(str(self.nonce),"utf-8"))
        digest.update(bytes(str(self.previousHash),"utf-8"))
        computedHash = digest.finalize()
        return computedHash
    def is_valid(self):
        if self.previousBlock == None :
            return True
        return self.previousBlock.computeHash() == self.previousHash

if __name__ == '__main__':
    root = CBlock('I am root', None)
    B1 = CBlock('I am a child', root)
    B2 = CBlock('I am B1s brother', root)
    B3 = CBlock(12354, B1)
    B4 = CBlock(someClass('Hi there!'), B3)
    B5 = CBlock('Top Block', B4)

    for b in [B1, B2, B3 , B4, B5]:
        if b.previousBlock.computeHash() == b.previousHash:
            print("Success! Hash is good.")
        else:
            print("ERROR! Hash is no good")

    B3.data = 12345
    if B4.previousBlock.computeHash() == B4.previousHash:
            print("ERROR! Couldn't detect tampering")
    else:
            print("Succes! Tampering detected")

    B4.data.num = 999999
    if B5.previousBlock.computeHash() == B5.previousHash:
            print("ERROR! Couldn't detect tampering")
    else:
            print("Succes! Tampering detected")
