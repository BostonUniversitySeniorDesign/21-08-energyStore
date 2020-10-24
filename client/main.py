#!/usr/bin/env python3
############################

### IMPORTS ###
# standard python libs
import socket
import logging
import time
# locally defined libs
import defines


def socket_connect(sock, host, port):
    #get log
    log = logging.getLogger(defines.LOG_NAME)

    #try to connect to socket at host & port
    attempts = 0
    while attempts < defines.CONNECTION_ATTEMPTS:
        try:
            attempts+=1
            print("trying to connect to host")
            sock.connect((socket_host, socket_port))
            log.info("connected to host {} port {} after {} second(s)".format(host, port, attempts))
            return True 
        except Exception as e:
            log.warning("{}".format(e))
            time.sleep(1)
    print("timed out trying to connect to host")
    log.error("unable to connect to host {} port {} after {} second(s)".format(host, port, attempts))
    return False

def set_switch_state(state):
    print("TODO: define set_switch_state(state)")

def get_switch_state():
    print("TODO: define set_switch_state()")
    state = "MAINGRID"
    return state;

if __name__ == "__main__":

    ##################################
    # IMMEDIATELY set switch to default 
    set_switch_state(defines.SWITCH_DEFAULT)
    
    ##################################
    # set up logging
    log_filename = (defines.LOG_NAME + ".log")
    format = "%(asctime)s %(funcName)s: [%(levelname)s] %(message)s"
    logging.basicConfig(filename=log_filename, format=format, level=logging.DEBUG, datefmt="%H:%M:%s")
    log = logging.getLogger(defines.LOG_NAME)
    log.info("logging start")


    ##################################
    # set up socket
    log.info("defining client socket")
    socket_host = socket.gethostname()  # The server's hostname or IP address
    socket_port = defines.SOCKET_PORT   # The port used by the server
    socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    ##################################
    # MAIN LOOP
    while True:
        
        # try to get connection to host
        if socket_connect(socket, socket_host, socket_port):
            # send a query for which state we should be in
            socket.sendall(b'QUERY')
            state_new = socket.recv(1024)
            #socket.close()
            # set switch to proper state
            set_switch_state(state_new)
            # check we are in proper state
            if get_switch_state() != state_new:
                log.critical("SWITCH NOT IN PROPER STATE: switch is {}, switch should be {}".format(get_switch_state(),state_new))
            else:
                log.info("switch in proper state {}".format(get_switch_state()))
            
        else: # couldn't connect to host
            log.error("unable to connect to host, setting switch to {}".format(defines.SWITCH_DEFAULT))
            set_switch_state(defines.SWITCH_DEFAULT) # default to MAINGRID
            if get_switch_state() != defines.SWITCH_DEFAULT:
                log.critical("SWITCH NOT IN PROPER STATE: switch is {}, switch should be MAINGRID".format(get_switch_state()))
        
        wait = defines.SWITCHING_FREQ #* 60
        time.sleep(wait)
