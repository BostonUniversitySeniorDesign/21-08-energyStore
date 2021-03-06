####################################################################
# USER DEFINITIONS FOR OUTPUT
####################################################################
###############################################
# Output of simulation
PRINTS = False
GRAPHS = False

###############################################
# For running the simulation without solar or battery
SOLAR = True
BATTERY = True

###############################################
# Getting monthly pricing output
MONTHLY = True

# desired name of the monthly output file 
monthly_out_filename = "monthly_prices_O.txt"   # this should have .txt as the extension!

###############################################
# For running simulation with optimized pricing scheme 
# These files are the OUTPUT of the ML model
OPT_PRICING = True

opt_pricing_house1 = 'house1_data_OPT.csv'  # this should have .csv as the extension!
opt_pricing_house2 = 'house2_data_OPT.csv'  # this should have .csv as the extension!
opt_pricing_house3 = 'house3_data_OPT.csv'  # this should have .csv as the extension!
opt_pricing_house4 = 'house4_data_OPT.csv'  # this should have .csv as the extension!

###############################################
# For enabling data output for 4 houses separately
# These files will be used as INPUT in the ML model
HOUSE_OUT = False

house_out_1 = "house1_data.csv"     # this should have .csv as the extension!
house_out_2 = "house2_data.csv"     # this should have .csv as the extension!
house_out_3 = "house3_data.csv"     # this should have .csv as the extension!
house_out_4 = "house4_data.csv"     # this should have .csv as the extension!   

##### start date
# month hould be between 1 and 12
# day should be between 1 and 31 (depending on month)
# year should be either 2019 or 2020 
month = 10      
day = 13        
year = 2019

# optional number of intervals to use
pre_covid_count = 1440 * 189    # starting date: 10/13/2019, ending date: 4/19/20
covid_count = 1440 * 175        # starting date: 4/20/2020, ending date: 10/12/2020

# Length of the simulation (in minutes)
number_of_intervals = pre_covid_count

####################################################################
# END OF USER DEFINITIONS FOR OUTPUT
####################################################################

############################
### IMPORTS ###

import matplotlib.pyplot as plt
import os
import numpy as np
import pandas as pd
import csv
import time
import random
import datetime

# user defined
import pricing
import battery

####################################################################
# GENERICS FOR SIMMULATION
####################################################################
# set the starting date and time
dt = datetime.datetime.now()
dt = dt.replace(microsecond=0, second=0, minute=0,
                hour=0, day=day, month=month, year=year)



# set interval parameters
interval_length = 1  # (in minutes)
interval_count = number_of_intervals
# 1 hour 60
# 1 day 1440
# 189 days = 1440 * 189
# 30 days 43200
# 180 days 259200
# 365 days 525600

# set solar parameters
SOLAR_COST_COEFFICIENT = .85  # (percentage expressed as a decimal)



months = ["January", "February", "March",
          "April", "May", "June",
          "July", "August", "September",
          "October", "November", "December"
          ]

screen_len = 60  # for printing pretty stuff

####################################################################
# SIMMULATION SETUP
####################################################################
# set up timer
timer_start = time.time()

# set up battery object
battery = battery.Battery_obj()
MAX_INTERVAL_POWER = battery.MAX_CONTINUOUS_POWER * \
    (interval_length / 60)  # kWh

# store this info for use later
total_minutes = interval_count * interval_length

# All of these arrays are used to store information
NUM_HOUSES = 4  # do not change, this is hardcoded for our data
house_running_demand = [0] * NUM_HOUSES  # (kWh)

#  used for determining current energy usage tier
house_running_demand_monthly = [0] * (NUM_HOUSES + 1)  # (kWh)

######################################
# load csv data into pandas dataframes (houshold demand and solar production)
loc_weather = os.path.join(os.getcwd(), "Weather Data.xlsx")
loc_house1 = os.path.join(os.getcwd(), "house_usage_data/Andrea_house.csv")
loc_house2 = os.path.join(
    os.getcwd(), "house_usage_data/angiesParents_house.csv")
loc_house3 = os.path.join(os.getcwd(), "house_usage_data/Cynthia_house.csv")
loc_house4 = os.path.join(os.getcwd(), "house_usage_data/Justo_house.csv")

df_house1 = pd.read_csv(loc_house1)
df_house2 = pd.read_csv(loc_house2)
df_house3 = pd.read_csv(loc_house3)
df_house4 = pd.read_csv(loc_house4)

house_usage_dfs = [df_house1, df_house2, df_house3, df_house4]

df_weatherdata = pd.read_excel(
    loc_weather, sheet_name="All Weather", usecols=['Date', 'Conditions'])
df_weather_fine = pd.read_excel(loc_weather, sheet_name="Fine", usecols=[
                                'Time', '5 Minute Energy (kWh)'])
df_weather_partly_cloudy = pd.read_excel(
    loc_weather, sheet_name="Partly Cloudy", usecols=['Time', '5 Minute Energy (kWh)'])
df_weather_mostly_cloudy = pd.read_excel(
    loc_weather, sheet_name="Mostly Cloudy", usecols=['Time', '5 Minute Energy (kWh)'])
df_weather_cloudy = pd.read_excel(loc_weather, sheet_name="Cloudy", usecols=[
                                  'Time', '5 Minute Energy (kWh)'])
df_weather_showers = pd.read_excel(loc_weather, sheet_name="Showers", usecols=[
                                   'Time', '5 Minute Energy (kWh)'])

weather_condition_dfs = [df_weather_fine, df_weather_cloudy,
                         df_weather_mostly_cloudy, df_weather_partly_cloudy, df_weather_showers]

# iterate through Dates in df_weatherdata and flip the dates to be strings
for (columnName, columnData) in df_weatherdata.iteritems():
    if columnName == "Date":
        i = 0
        dates_new = ['']*len(columnData)
        for date in columnData:
            if (isinstance(date, datetime.datetime)):
                day_ = date.month
                month_ = date.day

                if month_ < 10:
                    month_ = '0' + str(date.day)
                else:
                    month_ = str(date.day)

                if day_ < 10:
                    day_ = '0' + str(date.month)
                else:
                    day_ = str(date.month)

                date_new = month_ + '/' + day_
                dates_new[i] = date_new
                i += 1

            elif (isinstance(date, str)):
                date_list = date.split('/')
                date_new = date_list[1] + '/' + date_list[0]
                dates_new[i] = date_new
                i += 1

df_weatherdata = df_weatherdata.drop(['Date'], axis=1)
df_weatherdata['Date'] = dates_new


# get current date time and solar time to index into pandas df with
(date, time_i, solar_time) = pricing.get_Date_Time_solarTime(dt)

# need to get current day weather before any other iteration
daily_weather = df_weatherdata.loc[(
    df_weatherdata['Date'] == date)]['Conditions'].item()

####################################################################
# LIST FOR STORING SIMMULATION DATA
####################################################################
i_run = 0
# For time
date_historical = [0] * interval_count
# For running cost
total_cost_running = [([0] * interval_count), ([0] * interval_count),
                      ([0] * interval_count), ([0] * interval_count)]  # kWh
solar_cost_running = [([0] * interval_count), ([0] * interval_count),
                      ([0] * interval_count), ([0] * interval_count)]  # $
micro_cost_running = [([0] * interval_count), ([0] * interval_count),
                      ([0] * interval_count), ([0] * interval_count)]  # $
main_cost_running = [([0] * interval_count), ([0] * interval_count),
                     ([0] * interval_count), ([0] * interval_count)]  # $
# For running usage
total_used_running = [([0] * interval_count), ([0] * interval_count),
                      ([0] * interval_count), ([0] * interval_count)]  # kWh
solar_used_running = [([0] * interval_count), ([0] * interval_count),
                      ([0] * interval_count), ([0] * interval_count)]  # kWh
micro_used_running = [([0] * interval_count), ([0] * interval_count),
                      ([0] * interval_count), ([0] * interval_count)]  # kWh
main_used_running = [([0] * interval_count), ([0] * interval_count),
                     ([0] * interval_count), ([0] * interval_count)]  # kWh
# For solar production
solar_produced_running = [([0] * interval_count), ([0] * interval_count),
                          ([0] * interval_count), ([0] * interval_count)]  # kWh
solar_dumped = [0] * interval_count
# For battery
battery_charge_historical = [0] * interval_count
battery_avg_historical = [0] * interval_count

# For distributing hourly energy into 5 min periods
hourEnergy = [0] * NUM_HOUSES

# For keeping track of energy put onto the battery
battery_maingrid_usage = 0.0
battery_solar_energy = 0.0

# used for writing to the monthly cost file
total_monthly_cost = [0] * NUM_HOUSES
total_monthly_cost_TOTAL = [0] * NUM_HOUSES

# for running simulation with optimized pricing data
pricing_idx = 0

if OPT_PRICING:
    price_1 = '../ML/' + opt_pricing_house1
    price_2 = '../ML/' + opt_pricing_house2
    price_3 = '../ML/' + opt_pricing_house3
    price_4 = '../ML/' + opt_pricing_house4

    pricing_df1 = pd.read_csv(price_1)
    pricing_df2 = pd.read_csv(price_2)
    pricing_df3 = pd.read_csv(price_3)
    pricing_df4 = pd.read_csv(price_4)


if MONTHLY:
    fid = open(monthly_out_filename, 'w')


if HOUSE_OUT:
    house_fid1 = open(house_out_1, 'w')
    house_fid2 = open(house_out_2, 'w')
    house_fid3 = open(house_out_3, 'w')
    house_fid4 = open(house_out_4, 'w')

####################################################################
# SIMMULATION LOOP
####################################################################
print("Starting main loop")
house_list = [0, 1, 2, 3]

while interval_count != 0:

    # set the pricing for the interval if optimized
    if OPT_PRICING:
        opt_price1 = pricing_df1["energy_price"].iloc[pricing_idx]
        opt_price2 = pricing_df2["energy_price"].iloc[pricing_idx]
        opt_price3 = pricing_df3["energy_price"].iloc[pricing_idx]
        opt_price4 = pricing_df4["energy_price"].iloc[pricing_idx]

        opt_pricing = [opt_price1, opt_price2, opt_price3, opt_price4]
        

    ##################################
    # decrement interval and print
    print()
    for j in range(int(screen_len/2)):
        print('-', end='')
    print("\nRunning interval: {}".format(interval_count))
    print("date: {}".format(dt))
    interval_count -= 1

    ##################################
    # For tracking battery charging & discharging
    battery.interval_continuous_power = 0

    ###############################################################
    # Get demand for energy per-household
    # step datetime 5 minutes for every interval
    house_demand_total = [0] * NUM_HOUSES

    # Every hour we do something with house energy
    if (dt.minute % 60) == 0:
        hourEnergy = [0] * NUM_HOUSES
        for i in range(NUM_HOUSES):
            curr_house = house_usage_dfs[i]
            # house usage for an hour
            hourEnergy[i] = float(curr_house.loc[(curr_house['Date'] == date) & (
                curr_house['Time'] == time_i)]['Usage'].item())  # kWh

    ###############################################################
    # Get solar production per-household
    solar_energy_battery = [0] * NUM_HOUSES
    solar_used = [0] * NUM_HOUSES
    house_demand = [0] * NUM_HOUSES

    # every 5 mintues get the solar array data
    if (dt.minute % 5) == 0:
        # use current weather to index into solar to get every 5 minutes
        solarProduced = 0  # kWh
        if daily_weather == "Fine":
            solarProduced = float(df_weather_fine[(
                df_weather_fine['Time'] == solar_time)]['5 Minute Energy (kWh)'].item())

        elif daily_weather == "Partly Cloudy":
            solarProduced = float(df_weather_partly_cloudy[(
                df_weather_partly_cloudy['Time'] == solar_time)]['5 Minute Energy (kWh)'].item())

        elif daily_weather == "Mostly Cloudy":
            solarProduced = float(df_weather_mostly_cloudy[(
                df_weather_mostly_cloudy['Time'] == solar_time)]['5 Minute Energy (kWh)'].item())

        elif daily_weather == "Cloudy":
            solarProduced = float(df_weather_cloudy[(
                df_weather_cloudy['Time'] == solar_time)]['5 Minute Energy (kWh)'].item())

        elif daily_weather == "Showers":
            solarProduced = float(df_weather_showers[(
                df_weather_showers['Time'] == solar_time)]['5 Minute Energy (kWh)'].item())
        else:
            print("ERROR")

    # TO RUN SIMULATION WITHOUT SOLAR
    if SOLAR is False:
        solarProduced = 0.0

    # set housedemand total and solar produced for ONE minute intervals
    for i in range(NUM_HOUSES):
        house_demand_total[i] += (hourEnergy[i] / (60 / interval_length))
        house_running_demand_monthly[i] += (hourEnergy[i] /
                                            (60 / interval_length))

    # adjust solar pool for scale and for intervals
    solarPool = (solarProduced / 5) * 2.5
    solarCheck = solarPool

    # Get solar produced per house
    solar_profit = [0] * NUM_HOUSES
    random.shuffle(house_list)
    for i in house_list:
        if i_run != 0:
            solar_produced_running[i][i_run] = solar_produced_running[i][i_run-1] + (
                solarPool / 4)
        else:
            solar_produced_running[i][i_run] = (solarPool / 4)

        # still have solar energy to meet full house demand in the pool for the given period
        if solarPool > house_demand_total[i]:

            # Take
            solarPool -= house_demand_total[i]

            # battery_solar_energy += excess_energy # to keep track of how much excess is saved
            if OPT_PRICING:
                solar_profit[i] = house_demand_total[i] * (
                    SOLAR_COST_COEFFICIENT * opt_pricing[i])

            else:
                solar_profit[i] = house_demand_total[i] * (
                    SOLAR_COST_COEFFICIENT * pricing.get_maingrid_cost(dt, house_running_demand_monthly[i]))

            solar_used[i] = house_demand_total[i]
            if i_run != 0:
                solar_cost_running[i][i_run] = solar_cost_running[i][i_run -
                                                                    1] + solar_profit[i]
                solar_used_running[i][i_run] = solar_used_running[i][i_run -
                                                                    1] + solar_used[i]
            else:
                solar_cost_running[i][i_run] = solar_profit[i]
                solar_used_running[i][i_run] = solar_used[i]

            house_demand[i] = 0

            # if any extra solar from the 5 min period thats not in use, add it to the battery
            if i == (NUM_HOUSES - 1):
                excess_energy = solarPool
            else:
                excess_energy = 0

        # Not enough solar energy to meet full house demand
        else:
            if OPT_PRICING:
                    solar_profit[i] = solarPool * (SOLAR_COST_COEFFICIENT *
                                            opt_pricing[i])
            else:
                solar_profit[i] = solarPool * (SOLAR_COST_COEFFICIENT *
                                            pricing.get_maingrid_cost(dt, house_running_demand_monthly[i]))
            if i_run != 0:
                solar_cost_running[i][i_run] = solar_cost_running[i][i_run -
                                                                    1] + solar_profit[i]
                solar_used_running[i][i_run] = solar_used_running[i][i_run-1] + solarPool
            else:
                solar_cost_running[i][i_run] = solar_profit[i]
                solar_used_running[i][i_run] = solarPool

            solar_used[i] = solarPool
            house_demand[i] = house_demand_total[i] - solarPool
            excess_energy = 0

        # only charge battery with solar during certain hours
        if (dt.hour >= 9 and (dt.hour < 16 and dt.minute < 30)):
            # case of over charging
            if ((battery.interval_continuous_power + excess_energy) > MAX_INTERVAL_POWER):
                # solar_dumped[i] += excess_energy
                excess_energy = 0

            if BATTERY is False:
                excess_energy = 0

            # charge battery with excess solar
            battery.charge(excess_energy, 0)
            solar_energy_battery[i] = excess_energy
            excess_energy = 0

        # record the unused solar energy
        solar_dumped[i_run] += excess_energy

    ################################################################
    # Charging/Discharging the battery && Powering the Houses
    main_grid_used = [0] * NUM_HOUSES
    micro_grid_used = [0] * NUM_HOUSES

    # charge the battery from 9am to 3:30pm from the grid, power houses from solar and grid
    # or (battery.current_charge <= battery.MIN_CHARGE)):
    if ((dt.hour >= 9 and (dt.hour < 16 and dt.minute < 30))):
        ################
        # CHARGE BATTERY

        # respect max interval power
        amount = MAX_INTERVAL_POWER - battery.interval_continuous_power
        house_running_demand_monthly[4] += amount

        # TO RUN SIMULATION WITHOUT BATTERY
        if BATTERY is False:
            amount = 0

        # if OPT_PRICING:
        #     battery.charge(amount, opt_price)
        # else:
        battery.charge(amount, pricing.get_maingrid_cost(
            dt, house_running_demand_monthly[4]))

        # keeping track of main grid energy added to the battery
        battery_maingrid_usage += amount

        ################
        # POWER HOUSES
        for i in house_list:
            # power houses from grid (after they've already used available solar)
            main_grid_used[i] = house_demand[i]
            if i_run != 0:
                micro_used_running[i][i_run] = micro_used_running[i][i_run-1]
                micro_cost_running[i][i_run] = micro_cost_running[i][i_run-1]
                if OPT_PRICING:
                    main_cost_running[i][i_run] = (house_demand[i] * opt_pricing[i]) + main_cost_running[i][i_run-1]
                else:
                    main_cost_running[i][i_run] = (house_demand[i] * pricing.get_maingrid_cost(
                        dt, house_running_demand_monthly[i])) + main_cost_running[i][i_run-1]
                main_used_running[i][i_run] = main_used_running[i][i_run -
                                                                1] + main_grid_used[i]
            else:
                micro_used_running[i][i_run] = 0
                micro_cost_running[i][i_run] = 0
                if OPT_PRICING:
                    main_cost_running[i][i_run] = house_demand[i] * \
                        opt_pricing[i]
                else:
                    main_cost_running[i][i_run] = house_demand[i] * \
                        pricing.get_maingrid_cost(
                            dt, house_running_demand_monthly[i])
                main_used_running[i][i_run] = main_grid_used[i]

    # discharge the battery from 3:30pm all the way until 9am
    # power houses with the battery (after available solar has powered houses)
    else:
        #####################################
        # DISCHARGE BATTERY / POWER HOUSES
        for i in house_list:
            # check if battery has enough charge, and is above min charge, and no risk of undercharge
            if (battery.current_charge > (house_demand[i] * (1/battery.DISCHARGE_EFF))) and (battery.current_charge > battery.MIN_CHARGE) and (abs(battery.interval_continuous_power - (house_demand[i]/battery.DISCHARGE_EFF)) < MAX_INTERVAL_POWER):

                # power the houses from battery
                micro_grid_used[i] = (
                    house_demand[i] * (1/battery.DISCHARGE_EFF))
                if i_run != 0:
                    micro_used_running[i][i_run] = micro_used_running[i][i_run -
                                                                        1] + micro_grid_used[i]
                    micro_cost_running[i][i_run] = micro_cost_running[i][i_run-1] + \
                        (battery.discharge(
                            house_demand[i] * (1/battery.DISCHARGE_EFF)))
                    main_cost_running[i][i_run] = main_cost_running[i][i_run-1]
                    main_used_running[i][i_run] = main_used_running[i][i_run-1]
                else:
                    micro_used_running[i][i_run] = micro_grid_used[i]
                    micro_cost_running[i][i_run] = battery.discharge(
                        house_demand[i] * (1/battery.DISCHARGE_EFF))
                    main_cost_running[i][i_run] = 0
                    main_used_running[i][i_run] = 0
            # If battery is a no go, use the grid!
            else:
                # power houses from grid (after they've already used available solar)
                main_grid_used[i] = house_demand[i]
                if i_run != 0:
                    micro_used_running[i][i_run] = micro_used_running[i][i_run-1]
                    micro_cost_running[i][i_run] = micro_cost_running[i][i_run-1]
                    if OPT_PRICING:
                        main_cost_running[i][i_run] = (house_demand[i] * opt_pricing[i]) + main_cost_running[i][i_run-1]
                    else:
                        main_cost_running[i][i_run] = (house_demand[i] * pricing.get_maingrid_cost(
                            dt, house_running_demand_monthly[i])) + main_cost_running[i][i_run-1]
                    main_used_running[i][i_run] = main_used_running[i][i_run -
                                                                    1] + main_grid_used[i]
                else:
                    micro_used_running[i][i_run] = 0
                    micro_cost_running[i][i_run] = 0
                    if OPT_PRICING:
                        main_cost_running[i][i_run] = house_demand[i] * \
                                                    opt_pricing[i]
                    else:
                        main_cost_running[i][i_run] = house_demand[i] * \
                            pricing.get_maingrid_cost(
                                dt, house_running_demand_monthly[i])
                    main_used_running[i][i_run] = main_grid_used[i]


    # get total running cost
    for i in range(NUM_HOUSES):
        total_cost_running[i][i_run] = solar_cost_running[i][i_run] + \
            micro_cost_running[i][i_run] + main_cost_running[i][i_run]
        total_used_running[i][i_run] = solar_used_running[i][i_run] + \
            micro_used_running[i][i_run] + main_used_running[i][i_run]

        # add the cost of each interval here
        total_monthly_cost[i] += (total_cost_running[i][i_run] -
                                total_cost_running[i][i_run - 1])

    ##################################
    # Grabbing data to use with ML model

    if HOUSE_OUT:
        row = 'datetime,energy_price,battery_charge,household_demand,solar_produced\n'
        if i_run != 0:
            # convert dt object to float 
            timestamp = datetime.datetime.timestamp(dt)

            str_timestamp = str(timestamp) + ','
            str_price = str(pricing.get_maingrid_cost(dt,0)) + ','
            str_battery_charge = str(battery.current_charge) + ','
            str_house1 = str(house_demand_total[0]) + ','
            str_house2 = str(house_demand_total[1]) + ','
            str_house3 = str(house_demand_total[2]) + ','
            str_house4 = str(house_demand_total[3]) + ','
            str_solar = str(solarCheck) + '\n'

            row_house_1 = str_timestamp + str_price + str_battery_charge + str_house1 + str_solar
            row_house_2 = str_timestamp + str_price + str_battery_charge + str_house2 + str_solar
            row_house_3 = str_timestamp + str_price + str_battery_charge + str_house3 + str_solar
            row_house_4 = str_timestamp + str_price + str_battery_charge + str_house4 + str_solar
        else:
            row_house_1 = row
            row_house_2 = row
            row_house_3 = row
            row_house_4 = row

        house_fid1.write(row_house_1)
        house_fid2.write(row_house_2)
        house_fid3.write(row_house_3)
        house_fid4.write(row_house_4)


    ##################################
    # Recording some historical values
    # record date
    date_historical[i_run] = dt
    # record battery state
    battery_charge_historical[i_run] = battery.current_charge
    battery_avg_historical[i_run] = battery.average_cost

    # incremementing datetime and adjusting monthly tracker of house demand + reset weather for the day
    curr_day = dt.day
    current_month = dt.month

    # increment date time every 1 minute
    dt += datetime.timedelta(minutes=interval_length)

    # get current date time and solar time to index into pandas df with
    (date, time_i, solar_time) = pricing.get_Date_Time_solarTime(dt)

    # reset monthly sum of energy when month changes
    #   also get monthly sum of prices for each house
    if (current_month != dt.month):
        for j in range(NUM_HOUSES + 1):
            house_running_demand_monthly[j] = 0.0

        # also get monthly sum of prices for each house
        if MONTHLY:
            s0 = "Month: {}\n".format(months[current_month - 1])
            s1 = "\tHouse1: ${:.2f}\n".format(total_monthly_cost[0])
            s2 = "\tHouse2: ${:.2f}\n".format(total_monthly_cost[1])
            s3 = "\tHouse3: ${:.2f}\n".format(total_monthly_cost[2])
            s4 = "\tHouse4: ${:.2f}\n".format(total_monthly_cost[3])

            to_write = s0 + s1 + s2 + s3 + s4
            fid.write(to_write)

        for k in range(NUM_HOUSES):
            total_monthly_cost_TOTAL[k] += total_monthly_cost[k]
            total_monthly_cost[k] = 0

    if (curr_day != dt.day):
        # every 24 hours we get the new weather condition
        daily_weather = df_weatherdata.loc[(
            df_weatherdata['Date'] == date)]['Conditions'].item()

    ##################################
    # Printing for this interval
    tmp_list = [0] * NUM_HOUSES
    if PRINTS:
        print("\nINTERVAL TOTALS:")

        print("Solar     Produced: {} kWh".format(solarProduced))

        tmp_print = [round(num, 2) for num in house_demand_total]
        print("Household demand: {} kWh".format(tmp_print))

        tmp_print = [round(num, 2) for num in solar_used]
        print("Solar     used: {} kWh".format(tmp_print))

        tmp_print = [round(num, 2) for num in solar_energy_battery]
        print("Solar     stored in battery: {} kWh".format(tmp_print))

        tmp_print = [round(num, 2) for num in micro_grid_used]
        print("Microgrid used: {} kWh".format(tmp_print))

        tmp_print = [round(num, 2) for num in main_grid_used]
        print("Maingrid  used: {} kWh".format(tmp_print))

        ##################################
        # Printing running totals
        print("\nRUNNING TOTALS:")

        print("Battery charge: {} kWh".format(
            round(battery.current_charge, 2)))
        print("Battery average cost: {} $/kWh".format(round(battery.average_cost, 2)))

        for i in range(NUM_HOUSES):
            tmp_list[i] = main_used_running[i][i_run]
        tmp_print = [round(num, 2) for num in tmp_list]
        print("maingird  running used:  {} kWh".format(tmp_print))

        for i in range(NUM_HOUSES):
            tmp_list[i] = main_cost_running[i][i_run]
        tmp_print = [round(num, 2) for num in tmp_list]
        print("maingird  running cost: ${}".format(tmp_print))

        for i in range(NUM_HOUSES):
            tmp_list[i] = micro_used_running[i][i_run]
        tmp_print = [round(num, 2) for num in tmp_list]
        print("microgird running used:  {} kWh".format(tmp_print))

        for i in range(NUM_HOUSES):
            tmp_list[i] = micro_cost_running[i][i_run]
        tmp_print = [round(num, 2) for num in tmp_list]
        print("microgird running cost: ${}".format(tmp_print))

        for i in range(NUM_HOUSES):
            tmp_list[i] = solar_used_running[i][i_run]
        tmp_print = [round(num, 2) for num in tmp_list]
        print("Solar     running used:  {} kWh".format(tmp_print))

        for i in range(NUM_HOUSES):
            tmp_list[i] = solar_cost_running[i][i_run]
        tmp_print = [round(num, 2) for num in tmp_list]
        print("solar     running cost: ${}".format(tmp_print))

    i_run += 1

    pricing_idx += 1

####################################################################
# END
timer_end = time.time()

# For getting monthly cost
if MONTHLY:
    # if the simulation ended mid month
    if (total_monthly_cost[0] != 0) or (total_monthly_cost[1] != 0) or (total_monthly_cost[2] != 0) or (total_monthly_cost[3] != 0):
        s0 = "Month: {}\n".format(months[current_month - 1])
        s1 = "\tHouse1: ${:.2f}\n".format(total_monthly_cost[0])
        s2 = "\tHouse2: ${:.2f}\n".format(total_monthly_cost[1])
        s3 = "\tHouse3: ${:.2f}\n".format(total_monthly_cost[2])
        s4 = "\tHouse4: ${:.2f}\n".format(total_monthly_cost[3])

        to_write = s0 + s1 + s2 + s3 + s4
        fid.write(to_write)

    if total_monthly_cost_TOTAL[0] == 0 and total_monthly_cost_TOTAL[1] == 0 and \
        total_monthly_cost_TOTAL[2] == 0 and total_monthly_cost_TOTAL[3] == 0:
        for k in range(NUM_HOUSES):
            total_monthly_cost_TOTAL[k] = total_monthly_cost[k]


    s5 = "\n\nTOTALS\n"
    for k in range(NUM_HOUSES):
        s5 += "House{}: ${:.2f}\n".format((k+1),total_monthly_cost_TOTAL[k])

    fid.write(s5)
    fid.close()

####################################################################
# Print a fancy border
print('\n\n')
for i in range(screen_len):
    print('*', end='')
print()

# Print simulation time
print('Simulated {} minutes in {} seconds\n'.format(
    total_minutes, timer_end-timer_start))

totalSolar = 0
# Print statistics per household
for i in range(NUM_HOUSES):
    for j in range(int(screen_len/2)):
        print('-', end='')
    print("\nHOUSE {}".format(i+1))
    print("total     energy used:  {}kWh".format(
        round(total_used_running[i][i_run-1], 2)))
    print("maingrid  energy used:  {}kWh".format(
        round(main_used_running[i][i_run-1], 2)))
    print("maingrid  energy cost: ${}".format(
        round(main_cost_running[i][i_run-1], 2)))
    print("microgrid energy used:  {}kWh".format(
        round(micro_used_running[i][i_run-1], 2)))
    print("microgrid energy cost: ${}".format(
        round(micro_cost_running[i][i_run-1], 2)))
    print("solar     energy made:  {}kWh".format(
        round(solar_produced_running[i][i_run-1], 2)))

    totalSolar += solar_produced_running[i][i_run-1]

    print("solar     energy used:  {}kWh".format(
        round(solar_used_running[i][i_run-1], 2)))
    print("solar     energy cost: ${}".format(
        round(solar_cost_running[i][i_run-1], 2)))

print("\n\nMaingrid energy used by the Battery {}kWh".format(
    round(battery_maingrid_usage)))
print("Solar energy dump: {}kWh".format(round(np.sum(solar_dumped), 2)))
print("Total Solar energy made: {}kWh".format(
    round(totalSolar, 2)))

####################################################################
# CHARTS, GRAPHS, & PLOTS
####################################################################
if GRAPHS:
    ######################################
    # Plotting battery charge & avg cost
    fig_bat, axs_bat = plt.subplots()
    axs_bat2 = axs_bat.twinx()
    lns1 = axs_bat.plot(date_historical, battery_avg_historical,
                        'g-', label='Battery Avg Cost ($)')
    lns2 = axs_bat2.plot(
        date_historical, battery_charge_historical, 'b-', label='Battery Charge (kW)')

    lns = lns1+lns2
    labs = [l.get_label() for l in lns]
    axs_bat.legend(lns, labs, loc='lower right',
                   bbox_to_anchor=(1.05, 1), borderaxespad=0.)

    axs_bat.set_xlabel('Date Time')
    axs_bat.set_ylabel('Cost of energy $/kWh')
    axs_bat2.set_ylabel('Charge kWh')
    axs_bat.set_title('Battery Charge and Cost vs. Time')

    ######################################
    # Plotting home energy usage
    fig_eng, axs_eng = plt.subplots(2, 2)

    # Plotting home energy cost
    fig_cost, axs_cost = plt.subplots(2, 2)

    # Making pie charts
    pie_labels = 'Solar', 'Maingrid', 'Microgrid'
    fig_pie1, axs_pie1 = plt.subplots(2, 2)
    fig_pie2, axs_pie2 = plt.subplots(2, 2)
    pie_data1 = [0] * NUM_HOUSES
    pie_data2 = [0] * NUM_HOUSES

    for i in range(NUM_HOUSES):
        if i == 0:
            r = 0
            c = 0
        elif i == 1:
            r = 0
            c = 1
        elif i == 2:
            r = 1
            c = 0
        elif i == 3:
            r = 1
            c = 1

        axs_eng[r, c].plot(
            date_historical, total_used_running[i], label="total")
        axs_eng[r, c].plot(
            date_historical, solar_used_running[i], label="solar")
        axs_eng[r, c].plot(
            date_historical, micro_used_running[i], label="micro")
        axs_eng[r, c].plot(date_historical, main_used_running[i], label="main")
        axs_eng[r, c].set_xlabel('Date Time')
        axs_eng[r, c].set_ylabel('Energy Used kWh')
        axs_eng[r, c].set_title('House {}'.format(i+1))
        axs_eng[r, c].legend()

        axs_cost[r, c].plot(
            date_historical, total_cost_running[i], label="total")
        axs_cost[r, c].plot(
            date_historical, solar_cost_running[i], label="solar")
        axs_cost[r, c].plot(
            date_historical, micro_cost_running[i], label="micro")
        axs_cost[r, c].plot(
            date_historical, main_cost_running[i], label="main")
        axs_cost[r, c].set_xlabel('Date Time')
        axs_cost[r, c].set_ylabel('Energy Cost $')
        axs_cost[r, c].set_title('House {}'.format(i+1))
        axs_cost[r, c].legend()

        pie_data1[i] = [solar_cost_running[i][i_run-1], main_cost_running[i]
                        [i_run-1], micro_cost_running[i][i_run-1]]  # TODO make this a percent
        axs_pie1[r, c].pie(pie_data1[i], labels=pie_labels, autopct='%.1f')
        axs_pie1[r, c].set_title('House {}'.format(i+1))

        pie_data2[i] = [solar_used_running[i][i_run-1], main_used_running[i]
                        [i_run-1], micro_used_running[i][i_run-1]]  # TODO make this a percent
        axs_pie2[r, c].pie(pie_data2[i], labels=pie_labels, autopct='%.1f')
        axs_pie2[r, c].set_title('House {}'.format(i+1))

        fig_cost.suptitle('Energy Cost ($) per House vs. Time')
        fig_eng.suptitle('Energy Usage (kWh) per House vs. Time')
        fig_pie1.suptitle('Energy Cost Distribution per House')
        fig_pie2.suptitle('Energy Usage Distribution per House')

    # Plot
    plt.show()

