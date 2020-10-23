#!/usr/bin/env python3
############################


### IMPORTS ###
# standard python libs
import socket
import logging
import threading
import time        #temporarily need this for pausing stuff
# locally defined imports
import defines     #this is basically a config file
import socket_top  #thread dedicated to socket
import monitor_top #thred dedicated to battery monitoring


### MAIN ###
if __name__  == "__main__":
    print("starting host/main.py")


    ##################################
    # set up logging
    log_filename = (defines.LOG_NAME + ".log")
    format = "%(asctime)s [%(levelname)s]: %(message)s"
    logging.basicConfig(filename=log_filename, format=format, level=logging.DEBUG, datefmt="%H:%M:%S")
    log = logging.getLogger(defines.LOG_NAME)
    log.info("Main : logging start")


    ##################################
    # set up socket
    log.info("Main : initializing host socket")
    socket_port = defines.SOCKET_PORT
    socket_hostname = socket.gethostname()
    log.info("Main : socket_hostname = {}, socket_port = {}".format(socket_hostname, socket_port))
    socket_host = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    socket_host.bind((socket_hostname,socket_port))


    ##################################
    # set up threading
    #NEED thread for ML?
    log.info("Main : starting socket thread")
    socket_thread = threading.Thread(target=socket_top.socket_top, args=(socket_host,), daemon=True)
    socket_thread.start()
    log.info("Main : starting monitor thread")
    monitor_thread = threading.Thread(target=monitor_top.monitor_top, args=("",), daemon=True)
    monitor_thread.start()

    ##################################
    # pause then end
    time_sleep = 10
    print("pausing for {} seconds".format(time_sleep))
    time.sleep(time_sleep)
    print("DONE")
