#!/usr/bin/env python3
############################

### IMPORTS ###
# standard python libs
import socket
# locally defined libs
import defines


if __name__ == "__main__":

    
    ##################################
    # set up logging
    log_filename = (defines.LOG_NAME + ".log")
    format = "%(asctime)s [%(levelname)s]: %(message)s"
    logging.basicConfig(filename=log_filename, format=format, level=logging.DEBUG, datefmt="%H:%M:%s")
    log = logging.getLogger(defines.LOG_NAME)
    log.info("Main : logging start")




    socket_host = socket.gethostname()  # The server's hostname or IP address
    socket_port = defines.SOCKET_PORT        # The port used by the server

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((socket_host, socket_port))
        s.sendall(b'Hello, world')
        data = s.recv(1024)

    print('Received', repr(data))


