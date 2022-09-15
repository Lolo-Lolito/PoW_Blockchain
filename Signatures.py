#Signatures.py

from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization

def generate_keys():
    private =  rsa.generate_private_key(65537,2048)
    public = private.public_key()
    public_ser = public.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo)
    return private, public_ser

def sign(message, private):
    message = bytes(str(message), "utf-8")
    sig = private.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH),
            hashes.SHA256())
    return sig

def verify(message, sig, public_ser):
    message = bytes(str(message), "utf-8")
    public = serialization.load_pem_public_key(public_ser)
    try:
        public.verify(
            sig,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256())
        return True
    except InvalidSignature:
        return False
    except:
        print("Error executing publickey.verify")
        return False

if __name__ == '__main__':
    pr, pu = generate_keys()
    message = "This is a secret message"
    sig = sign(message, pr)
    correct = verify(message, sig , pu)
    if correct :
        print("Success! Good sig")
    else:
        print("Error! Signature is bad")

    pr2, pu2 = generate_keys()
    sig2 = sign(message, pr2)
    correct = verify(message, sig2, pu)
    if correct :
        print("Error! Bad signature checks out!")
    else:
        print("Success! Bad sig detected")

    badmess = message + "Q"
    correct = verify(badmess, sig, pu)
    if correct :
        print("Error! Tampered message checks out!")
    else:
        print("Success! Tampered message detected")
