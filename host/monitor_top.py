#!/usr/bin/env python3
############################

### IMPORTS ###
# standard python libs
import logging
# locally defined imports
import defines

def monitor_top(empty):
    print("starting host/main.py")


    ##################################
    # set up logging
    log = logging.getLogger(defines.LOG_NAME)
    log.info("monitor thread started")



# calling this function returns the current 
# temperature measured at the battery
def monitor_temp():
    ### FILL THIS OUT ###
    return temperature

# calling this function returns the current
# charge measured at the battery
def monitor_charge():
    ### FILL THIS OUT ###
    return charge
