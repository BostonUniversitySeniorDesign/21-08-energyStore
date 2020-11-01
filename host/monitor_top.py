#!/usr/bin/env python3
############################
# standard python libs
import logging
import time
import random
import threading
# locally defined imports
import defines


####################################################################
# get_temperature  
####################################################################
def monitor_temp():
    ### FILL THIS OUT ###
    return temperature


####################################################################
# get_charge
####################################################################
def monitor_charge():
    #TODO: fill this out
    charge = 4
    return charge

####################################################################
# battery_available 
####################################################################
def battery_available():
    charge = monitor_charge()
    if charge > defines.MINIMUM_CHARGE:
        return True
    else:
        return False

####################################################################
# monitor_top 
####################################################################
def monitor_top(empty):
    print("starting host/main.py")


    ##################################
    # set up logging
    log = logging.getLogger(defines.LOG_NAME)
    log.info("monitor thread started")

    ##################################
    # MAIN LOOP
    while True:

        global MAINGRID_COST
        global MICROGRID_COST
        MAINGRID_COST = 4
        MICORGRID_COST = 7


        ##################################
        # MODEL BRANCH
        if defines.MONITOR_MODEL:
            # This isn't logically sound but for now is a holding point for testing reading & writing data to other threads
            temperature = random.randint( (defines.AVERAGE_TEMP - defines.TEMP_DEVIATION), (defines.AVERAGE_TEMP + defines.TEMP_DEVIATION))
            charge = random.randint(0,10)


        ##################################
        # LIVE BRANCH
        else:
            temperature = monitor_temp()
            charge = monitor_charge()
            print("")


        # wait then run again
        wait_time = defines.MONITOR_FREQ #* 60
        time.sleep(wait_time)

