#SocketUtils

import socket
import pickle
import select

TCP_PORT_DEFAULT = 5005
BUFFER_SIZE = 1024
TIME_OUT = 10

def newServerConnection(ip_addr, tcp_port = TCP_PORT_DEFAULT):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind((ip_addr, tcp_port))
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

def sendObj(ip_addr, inObj, tcp_port = TCP_PORT_DEFAULT):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((ip_addr, tcp_port))
    inObj_pickled = pickle.dumps(inObj)
    s.send(inObj_pickled)
    s.close()
    return False

if __name__ == '__main__':
    server = newServerConnection('localhost')
    #print('Server new connection established')
    O = recvObj(server)
    print("Success!") #If returns after time, then successful
    #print(O)
    server.close()
    
