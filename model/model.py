#!/usr/bin/env python3
############################
### IMPORTS ###
import datetime
import time
import csv
import pandas
import os

####################################################################
# GENERICS FOR SIMMULATION
####################################################################
# set the starting date and time
dt = datetime.datetime.now()
dt = dt.replace(microsecond=0, second=0, minute=0,
                hour=0, day=1, month=1, year=2020)

interval_length = 5  # (minutes)
interval_count = 5
# given interval_length == 5
# 1 hour 60/interval_length = 12
# 1 day 1440/interval_length = 288
# 30 days 43200/interval_length = 8640
# 180 days 259200/interval_length = 51840
# 365 days 525600/interval_length = 105120

####################################################################
# CLASSES
####################################################################

#Assuming this is a tesla powerwall
class Battery_obj:

    def __init__(self):
        # TODO figure out some guestimates for this
        # TODO ?? charging rates and such
        # Dynamic
        self.current_charge = 0.0  # (kWh)
        self.average_cost = 0.0  # (USD/kWh)
        self.interval_continuous_power = 0.0 # (kW)
        # Static
        self.CHARGE_EFF = 0.95  # (percentage expressed as a decimal)
        self.DISCHARGE_EFF = 0.95 # (percentage expressed as a decimal)
        self.MAX_CAPACITY = 13.5  # (kWh)
        self.MIN_CHARGE = 3.0  # (kWh)
        self.MAX_CONTINUOUS_POWER = 5.8 # (kW)

    # cost (dollars), 0 if from battery, otherwise get_maingrid_cost
    def charge(self, amount, cost):
        current_total_cost = self.current_charge * self.average_cost
        new_charge_cost = amount * cost
        self.current_charge += (amount * self.CHARGE_EFF)
        new_total_cost = current_total_cost + new_charge_cost
        if self.current_charge != 0:
            self.average_cost = new_total_cost / self.current_charge
        else:
            self.average_cost = 0.0

    def discharge(self, amount):
        self.current_charge -= amount
        return amount * self.average_cost  # return cost of this charge

####################################################################
# FUNCTIONS
####################################################################
# return the cost of power from the maingrid (dollars/kWh)
# using this as refrence https://www.sce.com/residential/rates/Time-Of-Use-Residential-Rate-Plans
# for now this is using the TOU-D-4-9PM plan, TODO: add other plans


def get_maingrid_cost(dt):

    month = dt.month
    if (month >= 6) and (month <= 9):
        summer = True
    else:
        summer = False
    day_num = dt.weekday()

    if day_num > 4:
        weekend = True
    else:
        weekend = False

    hour = dt.hour

    if summer:
        if (hour >= 16) and (hour <= 21):  # 4pm-9pm
            if weekend:  # summer, weekend, peak
                return 0.34
            else:  # summer, weekday, peak
                return 0.41
        else:  # summer, weekend and weekday, off-peak
            return 0.26
    else:
        if hour >= 21:  # winter, weekend and weekday, off-peak
            return 0.27
        elif hour >= 16:  # winter, weekend and weekday, peak
            return 0.36
        else:  # winter, weekend and weekday, super off-peak
            return 0.25


####################################################################
# MAIN
####################################################################
# set up timer
timer_start = time.time()

# set up battery object
battery = Battery_obj()
MAX_INTERVAL_POWER = battery.MAX_CONTINUOUS_POWER * (interval_length / 60) #kWh 

#store this info for use later
total_minutes = interval_count * interval_length

# All of these arrays are used to store information
number_of_houses = 4  # do not change, this is hardcoded for our data
house_running_cost_main_grid = [0] * number_of_houses
house_running_cost_micro_grid = [0] * number_of_houses
house_running_solar_produced = [0] * number_of_houses
house_running_demand = [0] * number_of_houses
solar_panel_area = [1, 1, 1, 1]

######################################
# load csv data into pandas dataframes
house1_df = pandas.read_csv(os.path.join(os.getcwd(), "year1.txt"))
house2_df = pandas.read_csv(os.path.join(os.getcwd(), "year2.txt"))
house3_df = pandas.read_csv(os.path.join(os.getcwd(), "year3.txt"))
house4_df = pandas.read_csv(os.path.join(os.getcwd(), "year4.txt"))
df_list = [house1_df, house2_df, house3_df, house4_df]
x = 0
for df in df_list:
    # drop un-needed data
    df = df.drop(['Global_reactive_power', 'Voltage', 'Global_intensity',
                  'Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3'], axis=1)
    # string manipulation, this can probably be done better but it's okay for now
    for (columnName, columnData) in df.iteritems():
        if columnName == "Date":
            i = 0
            dates_new = ['']*len(columnData)
            for date in columnData:
                dates_new
                date_list = date.split('/')
                date_new = date_list[1] + '/' + date_list[0]
                dates_new[i] = date_new
                i += 1
    df = df.drop(['Date'], axis=1)
    df['Date'] = dates_new
    df_list[x] = df
    x += 1

####################################################################
# MAIN LOOP
####################################################################
print("Starting main loop")
while interval_count != 0:

    
    ##################################
    # For tracking battery charging & discharging
    battery.interval_continuous_power = 0


    ##################################
    # decrement interval
    print(interval_count)
    interval_count -= 1

    ##################################
    # Get demand for energy
    house_demand = [0] * number_of_houses
    for i in range(interval_length):  # iterate through interval length
        # get date & time
        date_ = str(dt.month) + '/' + str(dt.day)
        time_ = str(dt.time()).split('.')[0]
        print('date {} time {}'.format(date_, time_))
        for i_num_houses in range(number_of_houses):
            df_tmp = df_list[i]
            energy = float(df_tmp.loc[(df_tmp['Date'] == date_) & (
                df_tmp['Time'] == time_)]['Global_active_power'].item())/60 #energy is in kWh
            house_demand[i] += energy
            house_running_demand[i] += house_demand[i] #kWh
        dt += datetime.timedelta(minutes=1)  # increment date time

    ##################################
    # Get solar production per-household
    solar_energy = [0] * number_of_houses
    for i in range(number_of_houses):
        if num_panels[i] > 0:
            solar_energy[i] = 0  # TODO get solar produced by house
            house_running_solar_produced[i] += solar_energy[i]
            # power house w/ solar
            if solar_energy[i] > house_demand[i]:
                excess_energy = solar_energy[i] - house_demand[i]
                house_demand[i] = 0
            else:
                house_demand[i_solar] = house_demand[i] - \
                    solar_energy[i]
                excess_energy = 0
            # charge battery
            battery.charge(excess_energy, 0)

    ##################################
    # TODO charge battery from maingrid
    if battery.current_charge < battery.MIN_CHARGE:
        # charge battery to min_charge / TODO charge rates have to get important here
        pass

    ##################################
    # Power houses
    for i in range(number_of_houses):
        # battery is cheaper, has enough charge, and is above min charge
        if (battery.average_cost < get_maingrid_cost(dt)) and (battery.current_charge > (house_demand[i] * (1+battery.DISCHARGE_EFF))) and (battery.current_charge > battery.MIN_CHARGE):
            house_running_cost_micro_grid[i] += battery.discharge(
                house_demand[i] * (1+battery.DISCHARGE_EFF))
        else:
            house_running_cost_main_grid[i] += house_demand[i] * \
                get_maingrid_cost(dt)

    print("maingird: {}".format(house_running_cost_main_grid))
    print("microgird: {}".format(house_running_cost_micro_grid))

####################################################################
# END
####################################################################
timer_end = time.time()
screen_len = 60 #for printing pretty stuff


# Print a fancy border
print('\n\n')
for i in range(screen_len):
    print('*', end='')
print()

# Print simulation time
print('Simulated {} minutes in {} seconds\n'.format(total_minutes, timer_end-timer_start))

# Print statistics per household
for i in range(number_of_houses):
    for j in range(int(screen_len/2)):
        print('-', end='')
    print("\nHOUSE {}".format(i))
    print("total energy used: {}kWh".format(round(house_running_demand[i],2)))
    print("maingrid cost: ${}".format(round(house_running_cost_main_grid[i],2)))
    print("microgrid cost: ${}".format(round(house_running_cost_micro_grid[i],2)))
    print("solar produced: {}kWh".format(round(house_running_solar_produced[i],2)))
