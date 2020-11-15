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
interval_count = 12
# given interval_length == 5
# 1 hour 60/interval_length = 12
# 1 day 1440/interval_length = 288
# 30 days 43200/interval_length = 8640
# 180 days 259200/interval_length = 51840
# 365 days 525600/interval_length = 105120

####################################################################
# CLASSES
####################################################################


class Battery_obj:

    def __init__(self):
        # TODO figure out some guestimates for this
        # TODO ?? charging rates and such
        # Dynamic
        self.current_charge = 0.0  # (kWh)
        self.average_cost = 0.0  # (USD/kWh)
        # Static
        self.CHARGE_EFF = 0.0  # (units?)
        self.DISCHARGE_EFF = 0.0  # (units?)
        self.MAX_CAPACITY = 0.0  # (kWh)
        self.MIN_CHARGE = 0.0  # (kWh)

    # cost (dollars), 0 if from battery, otherwise get_maingrid_cost
    def charge(self, amount, cost):
        # TODO update average charge
        self.current_charge += (amount * self.CHARGE_EFF)

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
# set up battery object
battery = Battery_obj()

# set up timer
timer_start = time.time()
interval_count_historic = interval_count

number_of_houses = 4  # do not change, this is hardcoded for our data
house_running_cost_main_grid = [0] * number_of_houses
house_running_cost_micro_grid = [0] * number_of_houses
num_panels = [1, 1, 1, 1]

# load csv data into pandas dataframes
print("loading data for household energy usage")
house1_df = pandas.read_csv(os.path.join(os.getcwd(), "year1.txt"))
house2_df = pandas.read_csv(os.path.join(os.getcwd(), "year2.txt"))
house3_df = pandas.read_csv(os.path.join(os.getcwd(), "year3.txt"))
house4_df = pandas.read_csv(os.path.join(os.getcwd(), "year4.txt"))
# collect dataframes into list and modify
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
    # decrement interval
    print(interval_count)
    interval_count -= 1

    # Get demand for energy
    house_demand = [0] * number_of_houses
    for i_interval in range(interval_length):  # iterate through interval length
        # get date & time
        date_ = str(dt.month) + '/' + str(dt.day)
        time_ = str(dt.time()).split('.')[0]
        print('date {} time {}'.format(date_, time_))
        for i_num_houses in range(number_of_houses):
            df_tmp = df_list[i_num_houses]
            energy = float(df_tmp.loc[(df_tmp['Date'] == date_) & (
                df_tmp['Time'] == time_)]['Global_active_power'].item())/60
            house_demand[i_num_houses] += energy
        dt += datetime.timedelta(minutes=1)  # increment date time

    # TODO: Add in TOU pricing for summer and winter
    #   Keep track of energy usage MONTHY to see if any house goes over 130% energy usage for the month
    #   If they go over, they move from tier 1 pricing to tier 2 pricing
    #   Back to tier 1 at the start of a new month

    # Get solar production per-household
    solar_energy = [0] * number_of_houses
    for i_solar in range(number_of_houses):
        if num_panels[i_solar] > 0:
            solar_energy[i_solar] = 0  # TODO get solar produced by house
            # power house w/ solar
            if solar_energy[i_solar] > house_demand[i_solar]:
                excess_energy = solar_energy[i_solar] - house_demand[i_solar]
                house_demand[i_solar] = 0
            else:
                house_demand[i_solar] = house_demand[i_solar] - \
                    solar_energy[i_solar]
                excess_energy = 0
            # charge battery
            battery.charge(excess_energy, 0)

    # TODO charge battery from maingrid
    if battery.current_charge < battery.MIN_CHARGE:
        # charge battery to min_charge / TODO charge rates have to get important here
        pass

    for j_num_houses in range(number_of_houses):
        # battery is cheaper, has enough charge, and is above min charge
        if (battery.average_cost < get_maingrid_cost(dt)) and (battery.current_charge > (house_demand[j_num_houses] * (1+battery.DISCHARGE_EFF))) and (battery.current_charge > battery.MIN_CHARGE):
            house_running_cost_micro_grid[j_num_houses] += battery.discharge(
                house_demand[j_num_houses] * (1+battery.DISCHARGE_EFF))
        else:
            house_running_cost_main_grid[j_num_houses] += house_demand[j_num_houses] * \
                get_maingrid_cost(dt)

    print("maingird: {}".format(house_running_cost_main_grid))
    print("microgird: {}".format(house_running_cost_micro_grid))

####################################################################
# END
####################################################################
timer_end = time.time()
print('finished in {} seconds'.format(timer_end-timer_start))
for x in range(number_of_houses):
    print('house {} paid {} dollars for their energy consumed in {} minutes'.format(
        x, house_running_cost_main_grid[x], interval_count_historic * interval_length))
