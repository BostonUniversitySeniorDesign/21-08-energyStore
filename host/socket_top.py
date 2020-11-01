#!/usr/bin/env python3
############################


# standard python libs
import socket
import logging
import threading
import datetime
import os
# locally defined imports
import defines
import battery
#######################################################################
# set csv file for logging 
#######################################################################
csv_path = os.path.join(os.getcwd(), "logs/", str(defines.STATES_CSV))
if not os.path.exists(csv_path):
    file_tmp = open(csv_path, "w")
    file_tmp.write("date,time,unit,state\n")
    file_tmp.close()

    

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
        try:
            self.socket.bind((self.hostname, self.port))
        except: #this exception only handles the is the port is already in use
            #throw in lots of prints and logging here
            stream = os.popen("lsof | head -n 1").read()
            keys = " ".join(stream.split())
            pid_index = keys.split().index("PID")

            stream = os.popen("lsof | grep {}:{}".format(self.hostname, self.port)).read()
            keys = " ".join(stream.split())
            pid = keys.split()[pid_index]

            stream = os.popen("kill {}".format(pid)).read()
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

    ##################################
    # Main loop for handling 
    # connections
    while True:
        # get message from client
        message_rx = connection.recv(2048)
        if not message_rx:
            break
        message = message_rx.decode('utf-8')
        message = message.split(' ') #split message into list
         

        if message[0] == "QUERY": #Tell home unit which state to be in
            maingrid_cost = get_maingrid_cost()
            microgrid_cost = get_microgrid_cost()
            #print("maincost {}, microgridcost {}".format(MAINGRID_COST,MICROGRID_COST))
            if (MICROGRID_COST < MAINGRID_COST) and battery.battery_available():
                reply = "MICROGRID" 
            else:
                reply = "MAINGRID"

        elif message[0] == "STATUS": #write status of home unit to csv
            reply = "Confirmed: client {} in state {}".format(message[1],message[2])
            write_line = "{},{},{},{}\n".format(datetime.date.today(), datetime.datetime.now().strftime("%H:%M:%S"), message[1], message[2])
            with open(csv_path, "a") as tmp_file:
                tmp_file.write(write_line)
                tmp_file.close()

        else: #home unit sent bad message, echo it
            reply = 'Server echo: {}'.format(message)

        # send reply
        connection.sendall(str.encode(reply))
    connection.close()


#######################################################################
# get_maingrid_cost
#######################################################################
# return the cost of power from the maingrid (dollars/kWh)
# using this as refrence https://www.sce.com/residential/rates/Time-Of-Use-Residential-Rate-Plans
# for now this is using the TOU-D-4-9PM plan, TODO: add other plans
def get_maingrid_cost():

    month = datetime.datetime.today().month
    if (month >= june) and (month <= 9):
        summer = True
    else:
        summer = False

    day_num = datetime.datetime.today().weekday()
    if day_num > 4:
        weekend = True
    else:
        weekend = False
    
    hour = datetime.datetime.now().hour
    
    if summer:
        if (hour >= 16) and (hour <= 21): #4pm-9pm
            if weekend: #summer, weekend, peak
                return 0.34
            else: #summer, weekday, peak
                return 0.41
        else:#summer, weekend and weekday, off-peak
            return 0.26
    else:
        if hour >= 21: #winter, weekend and weekday, off-peak
            return 0.27
        elif hour >= 16: #winter, weekend and weekday, peak 
            return 0.36
        else: #winter, weekend and weekday, super off-peak
            return 0.25


#######################################################################
# get_microgrid_cost
#######################################################################
# return the cost of power from the microgrid (dollars/kWh)
def get_microgrid_cost():
    return 0.1


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
