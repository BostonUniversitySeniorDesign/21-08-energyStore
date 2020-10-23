#!/usr/bin/env python3
############################


### IMPORTS ###
# standard python libs
import socket
import logging
# locally defined imports
import defines

def socket_top(socket):
   
    ##################################
    # set up logging
    log = logging.getLogger(defines.LOG_NAME)
    log.info("socket_top : socket thread started")

    socket.listen()
    conn, addr = socket.accept()
    with conn:
        print('connected by', addr)
        while True:
            data = conn.recv(1024)
            if not data:
                break
            conn.sendall(data)






#working ideas, not really sure what the final structer here is gonna look like
def rx_handler(message_rx):
    return ""
def tx_handler():
    return""
