#!/usr/bin/env python3
############################

### IMPORTS ###
# standard python libs
import socket
import logging
import time
# locally defined libs
import defines

def set_switch_state(state):
    print("TODO: define set_switch_state(state)")

def get_switch_state():
    print("TODO: define get_switch_state()")
    state = "MAINGRID"
    return state;

if __name__ == "__main__":
    print("starting client/main.py")

    ##################################
    # IMMEDIATELY set switch to default 
    set_switch_state(defines.SWITCH_DEFAULT)
    STATE = get_switch_state()


    ##################################
    # set up client socket
    socket_host = socket.gethostname()  # The server's hostname or IP address
    socket_port = defines.SOCKET_PORT   # The port used by the server
    #client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    #client_socket.connect((socket_host,socket_port))
    #Response = client_socket.recv(1024)
    #print(Response.decode('utf-8'))

    while True:

        if defines.SOCKET_DEBUG:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((socket_host,socket_port))
            Response = client_socket.recv(1024)
            print(Response.decode('utf-8'))
            Input = input('Say Something: ')
            client_socket.send(str.encode(Input))
            Response = client_socket.recv(1024)
            print(Response.decode('utf-8'))
            client_socket.close()
        else:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect((socket_host,socket_port))
            Response = client_socket.recv(1024)
            print(Response.decode('utf-8'))
            msg_tx = "empty"
            client_socket.send(str.encode(msg_tx))
            Response = client_socket.recv(1024)
            print(Response.decode('utf-8'))
            time.sleep(1)

            msg_tx = "QUERY"
            client_socket.send(str.encode(msg_tx))
            Response = client_socket.recv(1024)
            print(Response.decode('utf-8'))
            time.sleep(1)

            msg_tx = "STATUS {} {}".format(defines.UNIQUE_NAME, STATE) 
            client_socket.send(str.encode(msg_tx))
            Response = client_socket.recv(1024)
            print(Response.decode('utf-8'))
            time.sleep(1)
            client_socket.close()
        #client_socket.close()
