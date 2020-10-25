#!/usr/bin/env python3
############################


# standard python libs
import socket
import logging
import threading
# locally defined imports
import defines


#######################################################################
# host_obj
#######################################################################
# This class is mostly used to leverage destructors, both sockets and
# logging can cause issues when not properly destructed. By holding
# these objects inside of this defined class, we can ensure the objects
# are properly destructed incase of any runtime errors
class host_obj: # should probably make this a singleton!!!!
    # predefines to make our destructor behave
    _sockect = None

    # construct with hostname and port
    def __init__(self):
        self.hostname = socket.gethostname()
        self.port = defines.SOCKET_PORT
        self.log = logging.getLogger(defines.LOG_NAME)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((self.hostname, self.port))

    # destructor to make sure the socket is closed after program termination
    def __del__(self):
        self.log.info("host_obj destructor called")
        if getattr(self, '_socket', None):
            self.socket.shutdown()
            self.socket.close()

    ####################################################################
    # enter and exit are used to make sure our destructor is called even
    # in the special case of a keyboard interupt. It's eseential that
    # the destructor is always called so our socket isn't left open
    def __enter__(self):
        self.log.info("host_obj entered")

    def __exit__(self, Type, value, traceback):
        self.log.info("host_obj exited")
        if getattr(self, '_socket', None):
            self.socket.shutdown()
            self.socket.close()


##################################################################
# connection_handler
##################################################################
# This function is responsible for handling any socket connections
# it is spawned as a daemon everytime socket_top recieves a new 
# connection
def connection_handler(connection):
    # inital message 
    connection.send(str.encode('connected'))
    # main loop    
    while True:
        # get message from client
        message_rx = connection.recv(2048)
        if not message_rx:
            break
        message = message_rx.decode('utf-8')
        message = message.split(' ') #split message into list
        # 
        if message[0] == "QUERY":
            reply = "MAINGRID" #define this later
        elif message[0] == "STATUS":
            reply = "Confirmed: client {} in state {}".format(message[1],message[2]) 
        else:
            reply = 'Server echo: {}'.format(message)
        # send reply
        connection.sendall(str.encode(reply))
    connection.close()


##################################################################
# socket_top
##################################################################
# This is the functional top of our socket thread. Everytime a new
# connection is accepted by our socket, a new thread is spawned to
# manage the connection.
def socket_top(socket_hostname, socket_port):
    print("starting host/socket_top.py")
    logging.getLogger(defines.LOG_NAME).info("socket thread started")

    host = host_obj()

    with host:

        host.socket.listen(defines.CLIENT_COUNT)
        host.log.info("Host socket listening for {} clients".format(defines.CLIENT_COUNT))
    
        threads = list()

        while True:
            Client, address = host.socket.accept()
            host.log.info("Connected to: {}:{}".format(Client,address))
            thread = threading.Thread(target=connection_handler, args=(Client,), daemon=True)
            threads.append(thread)
            thread.start()
        host.socket.close()
