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
interval_count = 288
# given interval_length == 5
# 1 hour 60/interval_length = 12
# 1 day 1440/interval_length = 288
# 30 days 43200/interval_length = 8640
# 180 days 259200/interval_length = 51840
# 365 days 525600/interval_length = 105120

# set solar parameters
solar_area = [36, 36, 36, 36]  # solar panel area (m2)
solar_efficiency = [.85, .85, .85, .85]  # solar panel efficiency (decimal)
SOLAR_COST_COEFFICIENT = .85 #  (percentage expressed as a decimal)

screen_len = 60  # for printing pretty stuff


####################################################################
# CLASSES
####################################################################

# Assuming this is a tesla powerwall
class Battery_obj:

    def __init__(self):
        # TODO figure out some guestimates for this
        # TODO ?? charging rates and such
        # Dynamic
        self.current_charge = 0.0  # (kWh)
        self.average_cost = 0.0  # (USD/kWh)
        self.interval_continuous_power = 0.0  # (kW)
        # Static
        self.CHARGE_EFF = 0.95  # (percentage expressed as a decimal)
        self.DISCHARGE_EFF = 0.95  # (percentage expressed as a decimal)
        self.MAX_CAPACITY = 13.5  # (kWh)
        self.MIN_CHARGE = 3.0  # (kWh)
        self.MAX_CONTINUOUS_POWER = 5.8  # (kW)

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
MAX_INTERVAL_POWER = battery.MAX_CONTINUOUS_POWER * (interval_length / 60)  # kWh

# store this info for use later
total_minutes = interval_count * interval_length

# All of these arrays are used to store information
number_of_houses = 4  # do not change, this is hardcoded for our data
# for running cost
house_running_cost_main_grid = [0] * number_of_houses #($)
house_running_cost_micro_grid = [0] * number_of_houses #($)
house_running_solar_produced = [0] * number_of_houses #($)
# for running usage
house_running_demand = [0] * number_of_houses #(kWh)
house_running_main_grid_usage = [0] * number_of_houses #(kWh)
house_running_micro_grid_usage = [0] * number_of_houses #(kWh)
solar_used_running = [0] * number_of_houses #(kWh)

solar_produced_running = [0] * number_of_houses 

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
solar_profit = [0] * number_of_houses

####################################################################
# MAIN LOOP
####################################################################
print("Starting main loop")
while interval_count != 0:

    ##################################
    # For tracking battery charging & discharging
    battery.interval_continuous_power = 0

    ##################################
    # decrement interval and print
    print()
    for j in range(int(screen_len/2)):
        print('-', end='')
    print("\nRunning interval: {}".format(interval_count))
    print("date: {}".format(dt))
    interval_count -= 1

    ##################################
    # Get demand for energy and GHI while
    # stepping date&time
    print("Calculating energy usage and GHI")
    house_demand_total = [0] * number_of_houses
    GHI = 0 #(wh/m2)
    for i in range(interval_length):  # iterate through interval length
        # string manipluation for date and time indexing
        date_ = str(dt.month) + '/' + str(dt.day)
        time_ = str(dt.time()).split('.')[0]
        hour_ = dt.hour
        # get home demand
        for j in range(number_of_houses):
            df_tmp = df_list[j]
            house_demand_total[j] += float(df_tmp.loc[(df_tmp['Date'] == date_) & (df_tmp['Time'] == time_)]['Global_active_power'].item())/60 #energy is in kWh
        # get GHI
        GHI += float(solar_df.loc[(solar_df['Date'] == date_) & (solar_df['Time'] == hour_)]['GHI'].item())/60 #TODO check that strings are hitting for all hours
        dt += datetime.timedelta(minutes=1)  # increment date time
    print("GHI: {}Wh/m2".format(round(GHI,2)))
    
    # TODO: Add in TOU pricing for summer and winter
    #   Keep track of energy usage MONTHY to see if any house goes over 130% energy usage for the month
    #   If they go over, they move from tier 1 pricing to tier 2 pricing
    #   Back to tier 1 at the start of a new month

    ##################################
    # Get solar production per-household
    print("Calculating solar energy production")
    # Set up
    solar_produced = [0] * number_of_houses
    solar_energy_battery = [0] * number_of_houses
    solar_used = [0] * number_of_houses
    house_demand = [0] * number_of_houses

    # Get solar produced per house
    for i in range(number_of_houses):
        solar_produced[i] = solar_area[i] * solar_efficiency[i] * GHI / 1000  # (kWh)
        solar_produced_running[i] += solar_produced[i]
        
        # have excess solar
        if solar_produced[i] > house_demand_total[i]:
            excess_energy = solar_produced[i] - house_demand_total[i]
            solar_profit[i] += house_demand_total[i] * (SOLAR_COST_COEFFICIENT * get_maingrid_cost(dt))
            solar_used[i] = house_demand_total[i]
            solar_used_running[i] += solar_used[i]
            house_demand[i] = 0

        # No excess solar
        else:
            solar_profit[i] += solar_produced[i] * (SOLAR_COST_COEFFICIENT * get_maingrid_cost(dt))
            solar_used_running[i] += solar_produced[i]
            solar_used[i] = solar_produced[i]
            house_demand[i] = house_demand_total[i] - solar_produced[i]
            excess_energy = 0

        # charge battery
        battery.charge(excess_energy, 0)
        solar_energy_battery[i] = excess_energy

    ##################################
    # TODO charge battery from maingrid
    if battery.current_charge < battery.MIN_CHARGE:
        # charge battery to min_charge / TODO charge rates have to get important here
        pass

    ##################################
    # Power houses
    main_grid_used = [0] * number_of_houses
    micro_grid_used = [0] * number_of_houses
    for i in range(number_of_houses):
        # battery is cheaper, has enough charge, and is above min charge
        if (battery.average_cost < get_maingrid_cost(dt)) and (battery.current_charge > (house_demand[i] * (1/battery.DISCHARGE_EFF))) and (battery.current_charge > battery.MIN_CHARGE):
            house_running_cost_micro_grid[i] += battery.discharge(house_demand[i] * (1/battery.DISCHARGE_EFF))
            micro_grid_used[i] = (house_demand[i] * (1/battery.DISCHARGE_EFF))
            house_running_micro_grid_usage[i] += micro_grid_used[i]
        else:
            house_running_cost_main_grid[i] += house_demand[i] * get_maingrid_cost(dt)
            main_grid_used[i] = house_demand[i]
            house_running_main_grid_usage[i] += main_grid_used[i]


    ##################################
    # Printing for this interval
    print("\nINTERVAL TOTALS:")

    solar_print = [round(num,2) for num in solar_produced]
    print("Solar Produced: {}kWh".format(solar_print)) 
    
    house_print = [round(num,2) for num in house_demand_total]
    print("Household demand: {}kWh".format(house_print))
    
    solar_print = [round(num,2) for num in solar_used]
    print("Solar used by house: {}kWh".format(solar_print))
    
    solar_print = [round(num,2) for num in solar_energy_battery]
    print("Solar stored in battery: {}kWh".format(solar_print))

    micro_print = [round(num,2) for num in micro_grid_used]
    print("Microgrid energy used: {}kWh".format(micro_print))

    main_print = [round(num,2) for num in main_grid_used]
    print("Maingrid energy used: {}kWh".format(main_print))

    ##################################
    # Printing running totals
    print("\nRUNNING TOTALS:")
    
    print("Battery charge: {}kWh".format(round(battery.current_charge,2)))
    print("Battery average cost: {}$/kWh".format(round(battery.average_cost,2)))
    
    main_print = [round(num,2) for num in house_running_main_grid_usage]
    print("maingird running usage: {}kWh".format(main_print))
    
    main_print = [round(num,2) for num in house_running_cost_main_grid]
    print("maingird running cost: ${}".format(main_print))
    
    micro_print = [round(num,2) for num in house_running_micro_grid_usage]
    print("microgird running usage: {}kWh".format(micro_print))
    
    micro_print = [round(num,2) for num in house_running_cost_micro_grid]
    print("microgird running cost: ${}".format(micro_print))
    
    solar_print = [round(num,2) for num in solar_used_running]
    print("Solar running usage: {}kWh".format(solar_print))
    
    solar_profit_print = [round(num,2) for num in solar_profit]
    print("solar running profit: ${}".format(solar_profit_print))

####################################################################
# END
####################################################################
timer_end = time.time()


# Print a fancy border
print('\n\n')
for i in range(screen_len):
    print('*', end='')
print()

# Print simulation time
print('Simulated {} minutes in {} seconds\n'.format(
    total_minutes, timer_end-timer_start))

# Print statistics per household
for i in range(number_of_houses):
    for j in range(int(screen_len/2)):
        print('-', end='')
    print("\nHOUSE {}".format(i))
    print("total energy used: {}kWh".format(round(house_running_demand[i], 2)))
    print("maingrid cost: ${}".format(round(house_running_cost_main_grid[i], 2)))
    print("microgrid cost: ${}".format(round(house_running_cost_micro_grid[i], 2)))
    print("solar produced: {}kWh".format(round(house_running_solar_produced[i], 2)))
