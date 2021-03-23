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

file_ = open("data.txt","a")

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
        # write to file
        file_.write("{},{},{},{},{},{},{},{},{},{}\n".format(date_,time_,rx_dict['M0'],rx_dict['M1'],rx_dict['M2'],rx_dict['M3'],rx_dict['M4'],rx_dict['M5'],rx_dict['M6'],rx_dict['M7']))
        #m7
        
        # Make a table for the state of relays
        relay_table = [['BATTERY', rx_dict['BATTERY']],['GRID', rx_dict['GRID']]]
        print(tabulate(relay_table, headers=['Relay', 'State'], tablefmt='orgtbl'))
        print()

        # Determine voltage scaling
        v_scaled = [0]*8
        for i in range(8):
            string='M{}'.format(i)
            v_scaled[i] = v_scale(rx_dict[string])

        # Make a table of scaled voltage measurements
        meter_table = [['M0', 'Inverter 0', rx_dict['M0'], v_scaled[0]], ['M1', 'Inverter 1', rx_dict['M1'], v_scaled[1]], ['M2', 'Inverter 2', rx_dict['M2'], v_scaled[2]], ['M3', 'Inverter 3', rx_dict['M3'], v_scaled[3]], ['M4', 'Battery Discharge', rx_dict['M4'], v_scaled[4]], ['M5', 'Battery Charge', rx_dict['M5'], v_scaled[5]], ['M6', 'Top of Bus', rx_dict['M6'], v_scaled[6]], ['M7', 'Top of Inverter', rx_dict['M7'], v_scaled[7]]]
        print(tabulate(meter_table, headers=['Meter', 'Name', 'Measured (10-bit)', 'Scaled (V)'], tablefmt='orgtbl'))
        print()

        # Get currents -> power to Inverters
        current_I0 = (v_scaled[6] - v_scaled[0])/.1
        current_I1 = (v_scaled[6] - v_scaled[1])/.1
        current_I2 = (v_scaled[6] - v_scaled[2])/.1
        current_I3 = (v_scaled[6] - v_scaled[3])/.1
        power_I0 = current_I0 * v_scaled[6]
        power_I1 = current_I1 * v_scaled[6]
        power_I2 = current_I2 * v_scaled[6]
        power_I3 = current_I3 * v_scaled[6]
        power_Inv = power_I0 + power_I1 + power_I2 + power_I3

        # Get current -> power from Battery
        current_bCharge = (v_scaled[6] - v_scaled[5])/.1
        current_bDischarge = (v_scaled[6] - v_scaled[4])/.1
        power_bCharge = current_bCharge * v_scaled[6]
        power_bDischarge = current_bDischarge * v_scaled[6]
        power_Batt = power_bDischarge - power_bCharge

        # Get current -> power from Grid
        current_Grid = (v_scaled[7] - v_scaled[6])/.1
        power_Grid = current_Grid * v_scaled[6]

        # Calculate current -> power from Solar Panels
        power_Solar = power_Inv - power_Grid - power_Batt

        power_table = [['House 0', power_I0], ['House 1', power_I1], ['House 2', power_I2], ['House 3', power_I3], ['Charging Battery', power_bCharge], ['Discharging Battery', power_bDischarge], ['Grid power', power_Grid], ['Solar power', power_Solar]]
        print(tabulate(power_table, headers=['thing', 'power (W)'], tablefmt='orgtbl'))
        # Print tables
        #print(relay_table)
        #print(meter_table)
