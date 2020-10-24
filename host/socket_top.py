#!/usr/bin/env python3
############################


### IMPORTS ###
# standard python libs
import socket
import logging
# locally defined imports
import defines

#
class host_socket:
    # predefines to make our destructor behave
    _sock = None

    # construct with hostname and port
    def __init__(self, socket_hostname, socket_port):
        logging.getLogger(defines.LOG_NAME).info("host_socket intialized")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.bind((socket_hostname, socket_port))

    # destructor to make sure the socket is closed after program termination
    def __del__(self):
        logging.getLogger(defines.LOG_NAME).info("shutting down host_socket")
        if getattr(self, '_sock', None):
            self.sock.shutdown()
            self.sock.close()
        logging.getLogger(defines.LOG_NAME).info("host_socket destroyed")

def socket_top(socket_hostname, socket_port):
   
    ##################################
    # set up logging
    log = logging.getLogger(defines.LOG_NAME)
    log.info("socket thread started")

    ##################################
    # set up socket
    host = host_socket(socket_hostname, socket_port)


    while True:
        host.sock.listen()
        connection, address = host.sock.accept()
        with connection:
            print('connected by', address)
            while True:
                data = connection.recv(1024)
                if not data:
                    break
                rx_handler(data, connection)
            #connection.close()

# This function is responsible for handling all data recieved from socket connections
def rx_handler(message_rx, connection):

    # message handling
    message = message_rx.decode() #convert message from type(bytes) to type(string)
    logging.getLogger(defines.LOG_NAME).info("rx_handler : message recieved = {}".format(message))

    # handling a QUERY request
    if message == "QUERY":
        # find out which state the client switch should be in - currently hardcoded
        state = "MAINGRID" #two states are MAINGRID and MICROGRID
        # state in final form needs to be grabbed from a global variable managed by another thread
        message_tx = state.encode('utf-8')

    connection.sendall(message_tx)

    return
