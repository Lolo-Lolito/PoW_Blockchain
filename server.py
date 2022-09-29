#server.py

import TxBlock
import socket

TCP_PORT = 5005

def recvObj(ip_addr):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip_addr, TCP_PORT))
    s.listen()
    new_sock, addr = s.accept()
    return new_sock.recv()

if __name__ == '__main__':
    newB = recvObj('localhost')
    print(newB.data[0])
    print(newB.data[1])
    if(newB.is_valid()):
        print("Success. Tx is valid")
    else :
        print("Error. Tx is invalid")
    if newB.data[0].inputs[0][1] == 2.3:
        print("Success. Input value matches")
    else:
        print("Error! Wrong input value for block 1")
    if newB.data[0].outputs[0][1] == 1.0:
        print("Success. Output value matches")
    else:
        print("Error! Wrong input value for block 1")
    if newB.data[0].outputs[1][1] == 1.1:
        print("Success. Output value matches")
    else:
        print("Error! Wrong output value for block 1")
    if newB.data[1].inputs[0][1] == 2.3:
        print("Success. Input value matches")
    else:
        print("Error! Wrong input value for block 1")
    if newB.data[1].inputs[1][1] == 1.0:
        print("Success. Input value matches")
    else:
        print("Error! Wrong input value for block 1")
    if newB.data[1].outputs[0][1] == 3.1:
        print("Success. Output value matches")
    else:
        print("Error! Wrong output value for block 1")
    
