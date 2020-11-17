#!/usr/bin/env python3
############################
### IMPORTS ###
import datetime
import random
import time
import csv
import pandas as pd
import os
import matplotlib.pyplot as plt
### user defined
import battery
import pricing

####################################################################
# GENERICS FOR SIMMULATION
####################################################################
# set the starting date and time
dt = datetime.datetime.now()
dt = dt.replace(microsecond=0, second=0, minute=0, hour=0, day=1, month=1, year=2020)

# set interval parameters
interval_length = 5  # (minutes)
interval_count = 8640
# given interval_length == 5
# 1 hour 60/interval_length = 12
# 1 day 1440/interval_length = 288
# 30 days 43200/interval_length = 8640
# 180 days 259200/interval_length = 51840
# 365 days 525600/interval_length = 105120

# set solar parameters
SOLAR_COST_COEFFICIENT = .85 #(percentage expressed as a decimal)

PRINTS=True
GRAPHS=True

screen_len = 60  # for printing pretty stuff

####################################################################
# SIMMULATION SETUP
####################################################################
# set up timer
timer_start = time.time()

# set up battery object
battery = battery.Battery_obj()
MAX_INTERVAL_POWER = battery.MAX_CONTINUOUS_POWER * (interval_length / 60)  # kWh

# store this info for use later
total_minutes = interval_count * interval_length

# All of these arrays are used to store information
NUM_HOUSES = 4  # do not change, this is hardcoded for our data
house_running_demand = [0] * NUM_HOUSES #(kWh)

#  used for determining curret energy usage tier
house_running_demand_monthly = [0] * (NUM_HOUSES + 1) #(kWh)   

######################################
# load csv data into pandas dataframes (houshold demand and solar production)
loc_weather = os.path.join(os.getcwd(), "Weather Data.xlsx")
loc_house1 = os.path.join(os.getcwd(), "house_usage_data/Andrea_house.csv")
loc_house2 = os.path.join(os.getcwd(), "house_usage_data/angiesParents_house.csv")
loc_house3 = os.path.join(os.getcwd(), "house_usage_data/Cynthia_house.csv")
loc_house4 = os.path.join(os.getcwd(), "house_usage_data/Justo_house.csv")

df_house1 = pd.read_csv(loc_house1)
df_house2 = pd.read_csv(loc_house2)
df_house3 = pd.read_csv(loc_house3)
df_house4 = pd.read_csv(loc_house4)

house_usage_dfs = [df_house1, df_house2, df_house3, df_house4]

df_weatherdata = pd.read_excel(loc_weather, sheet_name="All Weather",usecols=['Date', 'Conditions'])
df_weather_fine = pd.read_excel(loc_weather, sheet_name="Fine",usecols=['Time', '5 Minute Energy (kWh)'])
df_weather_partly_cloudy = pd.read_excel(loc_weather, sheet_name="Partly Cloudy",usecols=['Time', '5 Minute Energy (kWh)'])
df_weather_mostly_cloudy = pd.read_excel(loc_weather, sheet_name="Mostly Cloudy",usecols=['Time', '5 Minute Energy (kWh)'])
df_weather_cloudy = pd.read_excel(loc_weather, sheet_name="Cloudy",usecols=['Time', '5 Minute Energy (kWh)'])
df_weather_showers = pd.read_excel(loc_weather, sheet_name="Showers",usecols=['Time', '5 Minute Energy (kWh)'])

weather_condition_dfs = [df_weather_fine, df_weather_cloudy, df_weather_mostly_cloudy, df_weather_partly_cloudy, df_weather_showers]

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
                # print("datetime: {} \t {}".format(date, date_new))
            elif (isinstance(date, str)):
                date_list = date.split('/')
                date_new = date_list[1] + '/' + date_list[0]
                dates_new[i] = date_new
                i += 1
                # print("string: {}\t new: {}".format(date, date_new))
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
total_cost_running = [([0] * interval_count), ([0] * interval_count), ([0] * interval_count), ([0] * interval_count)] #kWh
solar_cost_running = [([0] * interval_count), ([0] * interval_count), ([0] * interval_count), ([0] * interval_count)] #$
micro_cost_running = [([0] * interval_count), ([0] * interval_count), ([0] * interval_count), ([0] * interval_count)] #$
main_cost_running = [([0] * interval_count), ([0] * interval_count), ([0] * interval_count), ([0] * interval_count)] #$
# For running usage
total_used_running = [([0] * interval_count), ([0] * interval_count), ([0] * interval_count), ([0] * interval_count)] #kWh
solar_used_running = [([0] * interval_count), ([0] * interval_count), ([0] * interval_count), ([0] * interval_count)] #kWh
micro_used_running = [([0] * interval_count), ([0] * interval_count), ([0] * interval_count), ([0] * interval_count)] #kWh
main_used_running = [([0] * interval_count), ([0] * interval_count), ([0] * interval_count), ([0] * interval_count)] #kWh
# For solar production
solar_produced_running = [([0] * interval_count), ([0] * interval_count), ([0] * interval_count), ([0] * interval_count)] #kWh
# For battery
battery_charge_historical = [0] * interval_count
battery_avg_historical = [0] * interval_count


####################################################################
# SIMMULATION LOOP
####################################################################
print("Starting main loop")
house_list = [0, 1, 2, 3]
while interval_count != 0:

    ##################################
    # decrement interval and print
    print()
    for j in range(int(screen_len/2)):
        print('-', end='')
    print("\nRunning interval: {}".format(interval_count))
    print("date: {}".format(dt))
    interval_count -= 1

    ##################################
    # TODO For tracking battery charging & discharging
    battery.interval_continuous_power = 0

    ##################################
    # Get demand for energy per-household
    # step datetime 5 minutes for every interval 
    house_demand_total = [0] * NUM_HOUSES

    # Every hour we do something with house energy
    if (dt.minute % 60) == 0:
        for i in range(NUM_HOUSES):
            curr_house = house_usage_dfs[i]
            house_demand_total[i] += float(curr_house.loc[(curr_house['Date'] == date) & (curr_house['Time'] == time_i)]['Usage'].item()) #kWh
            house_running_demand_monthly[i] += float(curr_house.loc[(curr_house['Date'] == date) & (curr_house['Time'] == time_i)]['Usage'].item()) #kWh

    ##################################
    # Get solar production per-household
    solar_energy_battery = [0] * NUM_HOUSES
    solar_used = [0] * NUM_HOUSES
    house_demand = [0] * NUM_HOUSES

    # use current weather to index into solar to get every 5 minutes
    solarProduced=0 #kWh
    if daily_weather == "Fine":
        solarProduced = float(df_weather_fine[(df_weather_fine['Time'] == solar_time)]['5 Minute Energy (kWh)'].item())

    elif daily_weather == "Partly Cloudy":
        solarProduced = float(df_weather_partly_cloudy[(df_weather_partly_cloudy['Time'] == solar_time)]['5 Minute Energy (kWh)'].item())

    elif daily_weather == "Mostly Cloudy":
        solarProduced = float(df_weather_mostly_cloudy[(df_weather_mostly_cloudy['Time'] == solar_time)]['5 Minute Energy (kWh)'].item())

    elif daily_weather == "Cloudy":
        solarProduced = float(df_weather_cloudy[(df_weather_cloudy['Time'] == solar_time)]['5 Minute Energy (kWh)'].item())

    elif daily_weather == "Showers":
        solarProduced = float(df_weather_showers[(df_weather_showers['Time'] == solar_time)]['5 Minute Energy (kWh)'].item())
    else:
        print("ERROR")

    # Get solar produced per house
    solar_profit = [0] * NUM_HOUSES
    random.shuffle(house_list)
    for i in house_list:
        if i_run != 0:
            solar_produced_running[i][i_run] = solar_produced_running[i][i_run-1] + solarProduced
        else:
            solar_produced_running[i][i_run] = solarProduced
        
        # have excess solar
        if solarProduced > house_demand_total[i]:
            excess_energy = solarProduced - house_demand_total[i]
            solar_profit[i] = house_demand_total[i] * (SOLAR_COST_COEFFICIENT * pricing.get_maingrid_cost(dt, house_running_demand_monthly[i]))
            if solar_profit[i] < 0:
                print("mike")
            solar_used[i] = house_demand_total[i]
            if i_run != 0:
                solar_cost_running[i][i_run] = solar_cost_running[i][i_run-1] + solar_profit[i]
                solar_used_running[i][i_run] = solar_used_running[i][i_run-1] + solar_used[i]
            else:
                solar_cost_running[i][i_run] = solar_profit[i]
                solar_used_running[i][i_run] = solar_used[i]
            house_demand[i] = 0

        # No excess solar
        else:
            solar_profit[i] = solarProduced * (SOLAR_COST_COEFFICIENT * pricing.get_maingrid_cost(dt, house_running_demand_monthly[i]))
            if i_run != 0:
                solar_cost_running[i][i_run] = solar_cost_running[i][i_run-1] + solar_profit[i]
                solar_used_running[i][i_run] = solar_used_running[i][i_run-1] + solarProduced
            else:
                solar_cost_running[i][i_run] = solar_profit[i]
                solar_used_running[i][i_run] = solarProduced
            solar_used[i] = solarProduced
            house_demand[i] = house_demand_total[i] - solarProduced
            excess_energy = 0

        # case of over charging
        if (battery.interval_continuous_power + excess_energy) > MAX_INTERVAL_POWER:
            excess_energy = 0
            #TODO sell back to grid?
        # charge battery
        battery.charge(excess_energy, 0)
        solar_energy_battery[i] = excess_energy

    curr_day = dt.day
    current_month = dt.month

    # increment date time every 5 minutes
    dt += datetime.timedelta(minutes=5)

    # get current date time and solar time to index into pandas df with
    (date, time_i, solar_time) = pricing.get_Date_Time_solarTime(dt)

    # reset monthly sum of energy when month changes
    if (current_month != dt.month):
        for j in range(NUM_HOUSES + 1):
            house_running_demand_monthly[j] = 0.0

    if (curr_day != dt.day):
        # every 24 hours we get the new weather condition
        daily_weather = df_weatherdata.loc[(df_weatherdata['Date'] == date)]['Conditions'].item()



    ##################################
    # Power houses
    main_grid_used = [0] * NUM_HOUSES
    micro_grid_used = [0] * NUM_HOUSES
    for i in house_list:
        # battery is cheaper, has enough charge, and is above min charge, and no risk of undercharge
        if (battery.average_cost < pricing.get_maingrid_cost(dt, house_running_demand_monthly[i])) and (battery.current_charge > (house_demand[i] * (1/battery.DISCHARGE_EFF))) and (battery.current_charge > battery.MIN_CHARGE) and (abs(battery.interval_continuous_power - (house_demand[i]/battery.DISCHARGE_EFF)) < MAX_INTERVAL_POWER):
            micro_grid_used[i] = (house_demand[i] * (1/battery.DISCHARGE_EFF))
            if i_run != 0:
                micro_used_running[i][i_run] = micro_used_running[i][i_run-1] + micro_grid_used[i]
                micro_cost_running[i][i_run] = micro_cost_running[i][i_run-1] + (battery.discharge(house_demand[i] * (1/battery.DISCHARGE_EFF)))
                main_cost_running[i][i_run] = main_cost_running[i][i_run-1]
                main_used_running[i][i_run] = main_used_running[i][i_run-1]
            else:
                micro_used_running[i][i_run] = micro_grid_used[i]
                micro_cost_running[i][i_run] = battery.discharge(house_demand[i] * (1/battery.DISCHARGE_EFF))
                main_cost_running[i][i_run] = 0
                main_used_running[i][i_run] = 0
        else:
            main_grid_used[i] = house_demand[i]
            if i_run != 0:
                micro_used_running[i][i_run] = micro_used_running[i][i_run-1]
                micro_cost_running[i][i_run] = micro_cost_running[i][i_run-1]
                main_cost_running[i][i_run] = (house_demand[i] * pricing.get_maingrid_cost(dt, house_running_demand_monthly[i])) + main_cost_running[i][i_run-1]
                main_used_running[i][i_run] = main_used_running[i][i_run-1] + main_grid_used[i]
            else:
                micro_used_running[i][i_run] = 0
                micro_cost_running[i][i_run] = 0
                main_cost_running[i][i_run] = house_demand[i] * pricing.get_maingrid_cost(dt, house_running_demand_monthly[i])
                main_used_running[i][i_run] = main_grid_used[i]

    # if battery less than min charge or (between 12am-5am and charge less than desired charge
    if (battery.current_charge < battery.MIN_CHARGE) or ((dt.hour < 5) & (battery.current_charge < battery.DESIRED_CHARGE)):
        amount = MAX_INTERVAL_POWER - battery.interval_continuous_power #respect max interval power
        house_running_demand_monthly[4] += amount
        battery.charge(amount, pricing.get_maingrid_cost(dt, house_running_demand_monthly[4]))  

    # get total running cost
    for i in range(NUM_HOUSES):
        total_cost_running[i][i_run] = solar_cost_running[i][i_run] + micro_cost_running[i][i_run] + main_cost_running[i][i_run]
        total_used_running[i][i_run] = solar_used_running[i][i_run] + micro_used_running[i][i_run] + main_used_running[i][i_run]

    ##################################
    # Printing for this interval
    tmp_list = [0] * NUM_HOUSES
    if PRINTS:
        print("\nINTERVAL TOTALS:")

        print("Solar     Produced: {} kWh".format(solarProduced)) 
    
        tmp_print = [round(num,2) for num in house_demand_total]
        print("Household demand: {} kWh".format(tmp_print))
 
        tmp_print = [round(num,2) for num in solar_used]
        print("Solar     used: {} kWh".format(tmp_print))
    
        tmp_print = [round(num,2) for num in solar_energy_battery]
        print("Solar     stored in battery: {} kWh".format(tmp_print))

        tmp_print = [round(num,2) for num in micro_grid_used]
        print("Microgrid used: {} kWh".format(tmp_print))

        tmp_print = [round(num,2) for num in main_grid_used]
        print("Maingrid  used: {} kWh".format(tmp_print))

        ##################################
        # Printing running totals
        print("\nRUNNING TOTALS:")
    
        print("Battery charge: {} kWh".format(round(battery.current_charge,2)))
        print("Battery average cost: {} $/kWh".format(round(battery.average_cost,2)))
    
        for i in range(NUM_HOUSES):
            tmp_list[i] = main_used_running[i][i_run]
        tmp_print = [round(num,2) for num in tmp_list]
        print("maingird  running used:  {} kWh".format(tmp_print))
    
        for i in range(NUM_HOUSES):
            tmp_list[i] = main_cost_running[i][i_run]
        tmp_print = [round(num,2) for num in tmp_list]
        print("maingird  running cost: ${}".format(tmp_print))
   
        for i in range(NUM_HOUSES):
            tmp_list[i] = micro_used_running[i][i_run] 
        tmp_print = [round(num,2) for num in tmp_list]
        print("microgird running used:  {} kWh".format(tmp_print))
    
        for i in range(NUM_HOUSES):
            tmp_list[i] = micro_cost_running[i][i_run]
        tmp_print = [round(num,2) for num in tmp_list]
        print("microgird running cost: ${}".format(tmp_print))
    
        for i in range(NUM_HOUSES):
            tmp_list[i] = solar_used_running[i][i_run]
        tmp_print = [round(num,2) for num in tmp_list]
        print("Solar     running used:  {} kWh".format(tmp_print))
    
        for i in range(NUM_HOUSES):
            tmp_list[i] = solar_cost_running[i][i_run]
        tmp_print = [round(num,2) for num in tmp_list]
        print("solar     running cost: ${}".format(tmp_print))

    ##################################
    # Recording some historical values
    # record date
    date_historical[i_run] = dt
    # record battery state
    battery_charge_historical[i_run] = battery.current_charge
    battery_avg_historical[i_run] = battery.average_cost
    i_run += 1

####################################################################
# END
timer_end = time.time()
####################################################################
# Print a fancy border
print('\n\n')
for i in range(screen_len):
    print('*', end='')
print()

# Print simulation time
print('Simulated {} minutes in {} seconds\n'.format(total_minutes, timer_end-timer_start))

# Print statistics per household
for i in range(NUM_HOUSES):
    for j in range(int(screen_len/2)):
        print('-', end='')
    print("\nHOUSE {}".format(i+1))
    print("total     energy used:  {}kWh".format(round(total_used_running[i][i_run-1], 2)))
    print("maingrid  energy used:  {}kWh".format(round(main_used_running[i][i_run-1], 2)))
    print("maingrid  energy cost: ${}".format(round(main_cost_running[i][i_run-1], 2)))
    print("microgrid energy used:  {}kWh".format(round(micro_used_running[i][i_run-1], 2)))
    print("microgrid energy cost: ${}".format(round(micro_cost_running[i][i_run-1], 2)))
    print("solar     energy made:  {}kWh".format(round(solar_produced_running[i][i_run-1], 2)))
    print("solar     energy used:  {}kWh".format(round(solar_used_running[i][i_run-1], 2)))
    print("solar     energy cost: ${}".format(round(solar_cost_running[i][i_run-1], 2)))

####################################################################
# CHARTS, GRAPHS, & PLOTS
####################################################################
if GRAPHS:
    ######################################
    # Plotting battery charge & avg cost 
    fig_bat, axs_bat = plt.subplots()
    axs_bat2 = axs_bat.twinx()
    axs_bat.plot(date_historical, battery_avg_historical, 'g-')
    axs_bat2.plot(date_historical, battery_charge_historical, 'b-')
    axs_bat.set_xlabel('Date Time')
    axs_bat.set_ylabel('Cost of energy $/kWh')
    axs_bat2.set_ylabel('Charge kWh')

    ######################################
    # Plotting home energy usage
    fig_eng, axs_eng = plt.subplots(2,2)
    # Plotting home energy cost 
    fig_cost, axs_cost = plt.subplots(2,2)
    # Making pie charts
    pie_labels = 'Solar', 'Maingrid', 'Microgrid'
    fig_pie, axs_pie = plt.subplots(2,2)
    pie_data = [0] * NUM_HOUSES

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
        
        axs_eng[r,c].plot(date_historical, total_used_running[i], label="total")
        axs_eng[r,c].plot(date_historical, solar_used_running[i], label="solar")
        axs_eng[r,c].plot(date_historical, micro_used_running[i], label="micro")
        axs_eng[r,c].plot(date_historical, main_used_running[i], label="main") 
        axs_eng[r,c].set_xlabel('Date Time')
        axs_eng[r,c].set_ylabel('Energy Used kWh')
        axs_eng[r,c].set_title('House {}'.format(i+1))
        axs_eng[r,c].legend()

        axs_cost[r,c].plot(date_historical, total_cost_running[i], label="total")
        axs_cost[r,c].plot(date_historical, solar_cost_running[i], label="solar")
        axs_cost[r,c].plot(date_historical, micro_cost_running[i], label="micro")
        axs_cost[r,c].plot(date_historical, main_cost_running[i], label="main") 
        axs_cost[r,c].set_xlabel('Date Time')
        axs_cost[r,c].set_ylabel('Energy Cost $')
        axs_cost[r,c].set_title('House {}'.format(i+1))
        axs_cost[r,c].legend()

        pie_data[i] = [solar_cost_running[i][i_run-1], main_cost_running[i][i_run-1], micro_cost_running[i][i_run-1]] # TODO make this a percent
        axs_pie[r,c].pie(pie_data[0], labels=pie_labels, autopct='%.1f')
        axs_pie[r,c].set_title('House {}'.format(i+1))

    # Plot
    plt.show()
