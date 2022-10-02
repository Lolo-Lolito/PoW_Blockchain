#SocketUtils

import socket
import pickle
import select

TCP_PORT = 5005
BUFFER_SIZE = 1024
TIME_OUT = 10

def newServerConnection(ip_addr):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip_addr, TCP_PORT))
    s.listen()
    return s

def recvObj(socket):
    readable, writable, exceptional = select.select([socket],[], [socket], TIME_OUT)
    if socket in readable :
        new_sock, addr = socket.accept()
        all_data = b''
        while True:
            data = new_sock.recv(BUFFER_SIZE)
            if not data :
                break
            all_data = all_data + data
        return pickle.loads(all_data)
    return None

def sendBlock(ip_addr, blk):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip_addr, TCP_PORT))
    blk_pickled = pickle.dumps(blk)
    s.send(blk_pickled)
    s.close()
    return False

if __name__ == '__main__':
    server = newServerConnection('localhost')
    #print('Server new connection established')
    O = recvObj(server)
    print("Success!") #If returns after time, then successful
    #print(O)
    server.close()
    
