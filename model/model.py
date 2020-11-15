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

# set interval parameters
interval_length = 5  # (minutes)
<<<<<<< HEAD
interval_count = 12
=======
interval_count = 5
>>>>>>> 8f40f9a06da22dcc58d045f8e8b766146efbeb50
# given interval_length == 5
# 1 hour 60/interval_length = 12
# 1 day 1440/interval_length = 288
# 30 days 43200/interval_length = 8640
# 180 days 259200/interval_length = 51840
# 365 days 525600/interval_length = 105120

# set solar parameters
solar_area = [1, 1, 1, 1] #solar panel area (m2)
solar_efficiency = [1, 1, 1, 1] #solare panel efficiency (decimal)


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
# using this as refrence https://www.sdge.com/whenmatters

# takes the current date as a datetime object,
# along with the usage so far for the current month
# to determine the tier: tier 1 under 130%


def get_maingrid_cost(dt):

    # TODO: add Tier 1 and tier 2 pricing based on their monthy usage so far:
    #   Coastal, summer (June 1 - Oct 31), all electric
    #       130% of Baseline is 234 kWh monthly
    #   Coastal, winter (Nov 1 - May 31), all electric
    #       130% of Baseline is 343 kWh monthly

    # get current month and day
    month = dt.month
    hour = dt.hour

    # Peak hours defined as 4PM to 9PM
    if (hour >= 4) and (hour <= 9):
        peak = True
    else:
        peak = False

    # Pricing differs per month
    if (month == 1) or (month == 2):    # january and february
        if peak:
            return .21262
        else:
            return .20864

    elif (month == 3) or (month == 4):  # march and april
        if peak:
            return .20775
        else:
            return .20376

    elif (month == 5):                  # may
        if peak:
            return .22034
        else:
            return .21522

    elif (month >= 6) and (month <= 10):  # june to october
        if peak:
            return .34163
        else:
            return .27906

    elif (month >= 11):                  # november and december
        if peak:
            return .23040
        else:
            return .22528


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
# load csv data into pandas dataframes (houshold demand)
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

######################################
# load csv data into pandas dataframes (solar)
solar_df = pandas.read_csv(os.path.join(os.getcwd(), "2018_solar_LA.csv"))


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

<<<<<<< HEAD
    # TODO: Add in TOU pricing for summer and winter
    #   Keep track of energy usage MONTHY to see if any house goes over 130% energy usage for the month
    #   If they go over, they move from tier 1 pricing to tier 2 pricing
    #   Back to tier 1 at the start of a new month

=======
    ##################################
>>>>>>> 8f40f9a06da22dcc58d045f8e8b766146efbeb50
    # Get solar production per-household
    solar_energy = [0] * number_of_houses
    GHI = #TODO get ghi from solar_df
    for i in range(number_of_houses):
        solar_energy[i] = solar_area[i] * solar_efficiency[i] * GHI 
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
<<<<<<< HEAD
print('finished in {} seconds'.format(timer_end-timer_start))
for x in range(number_of_houses):
    print('house {} paid {} dollars for their energy consumed in {} minutes'.format(
        x, house_running_cost_main_grid[x], interval_count_historic * interval_length))
=======
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
>>>>>>> 8f40f9a06da22dcc58d045f8e8b766146efbeb50
