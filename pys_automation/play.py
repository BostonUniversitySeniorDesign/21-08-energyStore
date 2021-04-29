#!/usr/bin/env python3.9
########################
# IMPORTS
########################
from tabulate import tabulate
import datetime
import json
import serial
import time

########################
# GENERICS
ARDUINO = serial.Serial(port='/dev/tty.usbmodem11101', baudrate=115200, timeout=.1)

def v_scale(measure):
    ## SCALING using M8 as a fixed refrence to the SHUNT_V ##
    percent = measure / 1023
    voltage = percent * 5
    scaled = voltage * 3

    return scaled


def write_read(x):
    ARDUINO.write(bytes(x, 'utf-8'))
    time.sleep(0.05)
    data = ARDUINO.readline()
    return data

while True:
    time.sleep(1)

    # rx-tx with arduino
    tx = input("Enter a number: ") # Taking input from user
    rx = write_read(tx).decode('utf-8')
    now=datetime.datetime.now()
    date_=now.strftime("%m/%d/%Y")
    time_=now.strftime("%H:%M:%S")
    print(rx) # printing the value
    #time = datetime.datetime.now() # Quickly get current time

    if rx:
        # load json as a dictionary
        rx_dict = json.loads(rx)
        # Write to file
        file_.write("{},{},{},{},{},{},{},{},{},{},{}".format(date_,time_,rx_dict['Home0'],rx_dict['Home1'],rx_dict['Home2'],rx_dict['Home3'],rx_dict['Grid'],rx_dict['Charge'],rx_dict['Discharge'],rx_dict['BATTERY'],rx_dict['GRID']))

        # Make a table for the state of relays
        relay_table = [['BATTERY', rx_dict['BATTERY']],['GRID', rx_dict['GRID']]]
        print(tabulate(relay_table, headers=['Relay', 'State'], tablefmt='orgtbl'))
        print()

        # Make a table for the power
        power_solar = (rx_dict['Home0'] + rx_dict['Home1'] + rx_dict['Home2'] + rx_dict['Home3'] + rx_dict['Charge']) - (rx_dict['Grid'] + rx_dict['Discharge'])
        power_table = [['Home0', rx_dixt['Home0']], ['Home1', rx_dict['Home1']], ['Home2', rx_dict['Home2']], ['Home3', rx_dcit['Home3']], ['Grid', rx_dict['Grid']], ['Charge', rx_dict['Charge']], ['Discharge', rx_dict['Discharge']], ['Solar', power_solar]]
        print(tabulate(power_table, headers=['Name', 'Power (mW)'], tablefmt='orgtbl'))
        print()
