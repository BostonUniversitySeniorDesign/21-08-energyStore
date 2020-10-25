#!/usr/bin/env python3
############################


# standard python libs
import socket
import logging
import time
#import gpiozero
# locally defined libs
import defines


####################################################################
# connect_socket
####################################################################
# This function returns a socket connected to a give host and port.
def connect_socket(host, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    i = 0
    while i < defines.CONNECTION_ATTEMPTS:
        try:
            i += 1
            client_socket.connect((host,port))
            logging.getLogger(defines.LOG_NAME).info("connected to {}:{} in {} second(s)".format(host, port, i))
            return (client_socket, True)
        except:
            time.sleep(1)
    logging.getLogger(defines.LOG_NAME).warning("failed to connect to {}:{} after {} second(s)".format(host, port, i))
    print("failed to connect to {}:{} after {} second(s)".format(host, port, i))
    return (0, False)


####################################################################
# set_switch_state
####################################################################
# This function sets the state of the switch. DESCRIBE LATER
def set_switch_state(state):
    print("TODO: define set_switch_state(state)")
    # this is where we will end up using gpiozero
    logging.getLogger(defines.LOG_NAME).info("switch set to state {}".format(state))
    return 


####################################################################
# get_switch_state
####################################################################
# This function checks and returns the current state of the switch,
# DESCRIBE LATER
def get_switch_state():
    print("TODO: define get_switch_state()")
    # this is where we will end up using gpiozero
    state = "MAINGRID"
    return state


####################################################################
# MAIN
####################################################################
if __name__ == "__main__":
    print("starting client/main.py")

    ##################################
    # IMMEDIATELY set switch to default 
    set_switch_state(defines.SWITCH_DEFAULT)
    STATE = get_switch_state()


    ##################################
    # set up logging
    Format = "%(asctime)s %(funcName)s: [%(levelname)s] %(message)s"
    logging.basicConfig(filename=defines.LOG_NAME, format=Format, level=logging.DEBUG, datefmt="%H:%M:%S")
    log = logging.getLogger(defines.LOG_NAME)
    log.info("logging started")
    print("logging to {}".format(defines.LOG_NAME))


    ##################################
    # get socket info 
    socket_host = socket.gethostname()  # The server's hostname or IP address
    socket_port = defines.SOCKET_PORT   # The port used by the server
    log.info("socket defined {}:{}".format(socket_host, socket_port))  

    
    ##################################
    # MAIN LOOP
    while True:

        ##################################
        # DEBUGGING BRANCH
        if defines.SOCKET_DEBUG:
    
            # open socket connection
            client_socket, result = connect_socket(socket_host, socket_port)
            if result: # if connection successful
                Response = client_socket.recv(1024)
                print(Response.decode('utf-8'))
            
                # get command, send to socket, print response
                command = input('Enter Command: ')
                client_socket.send(str.encode(command))
                message_rx = client_socket.recv(1024)
                print(message_rx.decode('utf-8'))
            
                # close socket connection
                client_socket.close()

        
        ##################################
        # AUTONOMOUS BRANCH
        else:
            # open socket connection
            client_socket, result = connect_socket(socket_host, socket_port)
            if result: # if connection successful
                message_rx = client_socket.recv(1024)
                log.info("recieved: {}".format(message_rx))
                print(message_rx.decode('utf-8'))
            
                # test the server echo default
                message_tx = "test echo"
                client_socket.send(str.encode(message_tx))
                log.info("send: {}".format(message_tx))
                message_rx = client_socket.recv(1024)
                log.info("recieved: {}".format(message_rx))
                print(message_rx.decode('utf-8'))
                time.sleep(1)

                # query server for state
                message_tx = "QUERY"
                client_socket.send(str.encode(message_tx))
                log.info("send: {}".format(message_tx))
                message_rx = client_socket.recv(1024)
                log.info("recieved: {}".format(message_rx))
                set_switch_state(message_rx)
                STATE = get_switch_state()
                print(message_rx.decode('utf-8'))
                time.sleep(1)

                # inform server of state
                message_tx = "STATUS {} {}".format(defines.UNIQUE_NAME, STATE) 
                client_socket.send(str.encode(message_tx))
                log.info("send: {}".format(message_tx))
                message_rx = client_socket.recv(1024)
                log.info("recieved: {}".format(message_rx))
                print(message_rx.decode('utf-8'))
                time.sleep(1)

                # close socket connection
                client_socket.close()
            
            else: # connection not successful, set switch to default
                log.warning("setting switch to default {}".format(defines.SWITCH_DEFAULT))
                set_switch_state(defines.SWITCH_DEFAULT)
                STATE = get_switch_state()

            # wait before looping again 
            wait_time = defines.SWITCHING_FREQ#*60
            time.sleep(wait_time)
