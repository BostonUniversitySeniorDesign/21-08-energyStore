#!/usr/bin/env python3
############################
### IMPORTS ###
import datetime
import time
import csv
import pandas
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
dt = dt.replace(microsecond=0, second=0, minute=0,
                hour=0, day=1, month=1, year=2020)

# set interval parameters
interval_length = 5  # (minutes)
interval_count = 1
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

PRINTS=True

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
number_of_houses = 4  # do not change, this is hardcoded for our data
# for running cost
house_running_cost_main_grid = [0] * number_of_houses #($)
house_running_cost_micro_grid = [0] * number_of_houses #($)
house_running_solar_produced = [0] * number_of_houses #($)
# for running usage
house_running_demand = [0] * number_of_houses #(kWh)
house_running_main_grid_usage = [0] * number_of_houses #(kWh)
house_running_micro_grid_usage = [0] * number_of_houses #(kWh)

#  used for determining curret energy usage tier
house_running_demand_monthly = [0] * number_of_houses #(kWh)   
current_month = dt.month

####################################################################
# LOADING DATA
####################################################################
# load csv data into pandas dataframes (houshold demand)
house1_df = pandas.read_csv(os.path.join(os.getcwd(), "data/year1.txt"))
house2_df = pandas.read_csv(os.path.join(os.getcwd(), "data/year2.txt"))
house3_df = pandas.read_csv(os.path.join(os.getcwd(), "data/year3.txt"))
house4_df = pandas.read_csv(os.path.join(os.getcwd(), "data/year4.txt"))
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
# load csv data into pandas dataframes (solar production)
solar_df = pandas.read_csv(os.path.join(os.getcwd(), "2018_solar_LA.csv"))
solar_profit = [0] * number_of_houses

####################################################################
# LIST FOR STORING SIMMULATION DATA
####################################################################
# For creating long running graphs
i_running = 0
date_historical = [0] * interval_count
# solar price and usage
solar_produced_running = [([0] * interval_count), ([0] * interval_count), ([0] * interval_count), ([0] * interval_count)] #kWh
solar_used_running = [([0] * interval_count), ([0] * interval_count), ([0] * interval_count), ([0] * interval_count)] #kWh
solar_profit_historical = [([0] * interval_count), ([0] * interval_count), ([0] * interval_count), ([0] * interval_count)] #$
# battery price and usage
battery_charge_historical = [0] * interval_count
battery_avg_historical = [0] * interval_count
# grid price and history


####################################################################
# SIMMULATION LOOP
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
            #print("indx {}".format((df_tmp['Date'] == date_) & (df_tmp['Time'])))
            # for checking energy tier
            house_running_demand_monthly[j] += float(df_tmp.loc[(df_tmp['Date'] == date_) & (df_tmp['Time'] == time_)]['Global_active_power'].item())/60 #energy is in kWh
        current_month = dt.month
        # get GHI
        GHI += float(solar_df.loc[(solar_df['Date'] == date_) & (solar_df['Time'] == hour_)]['GHI'].item())/60 #TODO check that strings are hitting for all hours
        dt += datetime.timedelta(minutes=1)  # increment date time

        # reset monthly sum of energy when month changes
        if (current_month != dt.month):
            for j in range(number_of_houses):
                house_running_demand_monthly[j] = 0.0


    ##################################
    # Get solar production per-household
    solar_produced = [0] * number_of_houses
    solar_energy_battery = [0] * number_of_houses
    solar_used = [0] * number_of_houses
    house_demand = [0] * number_of_houses

    # Get solar produced per house
    for i in range(number_of_houses):
        solar_produced[i] = solar_area[i] * solar_efficiency[i] * GHI / 1000  # (kWh)
        if i_running != 0:
            solar_produced_running[i][i_running] = solar_produced_running[i][(i_running - 1)] + solar_produced[i]
        else:
            solar_produced_running[i][i_running] = solar_produced[i]
        
        # have excess solar
        if solar_produced[i] > house_demand_total[i]:
            excess_energy = solar_produced[i] - house_demand_total[i]
            solar_profit[i] += house_demand_total[i] * (SOLAR_COST_COEFFICIENT * pricing.get_maingrid_cost(dt, house_running_demand_monthly[i]))
            solar_used[i] = house_demand_total[i]
            if i_running != 0:
                solar_used_running[i][i_running] = solar_used_running[i][(i_running -1)] + solar_used[i]
            else:
                solar_used_running[i][i_running] = solar_used[i]
            house_demand[i] = 0

        # No excess solar
        else:
            solar_profit[i] += solar_produced[i] * (SOLAR_COST_COEFFICIENT * pricing.get_maingrid_cost(dt, house_running_demand_monthly[i]))
            if i_running != 0:
                solar_used_running[i][i_running] = solar_used_running[i][(i_running -1)] + solar_produced[i]
            else:
                solar_used_running[i][i_running] = solar_produced[i]
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
        if (battery.average_cost < pricing.get_maingrid_cost(dt, house_running_demand_monthly[i])) and (battery.current_charge > (house_demand[i] * (1/battery.DISCHARGE_EFF))) and (battery.current_charge > battery.MIN_CHARGE):
            house_running_cost_micro_grid[i] += battery.discharge(house_demand[i] * (1/battery.DISCHARGE_EFF))
            micro_grid_used[i] = (house_demand[i] * (1/battery.DISCHARGE_EFF))
            house_running_micro_grid_usage[i] += micro_grid_used[i]
        else:
            house_running_cost_main_grid[i] += house_demand[i] * pricing.get_maingrid_cost(dt, house_running_demand_monthly[i])
            main_grid_used[i] = house_demand[i]
            house_running_main_grid_usage[i] += main_grid_used[i]

    
    ##################################
    # Printing for this interval
    tmp_list = [0] * number_of_houses
    if PRINTS:
        print("\nINTERVAL TOTALS:")

        solar_print = [round(num,2) for num in solar_produced]
        print("GHI: {} Wh/m2".format(round(GHI,2)))
        print("Solar Produced: {} kWh".format(solar_print)) 
    
        house_print = [round(num,2) for num in house_demand_total]
        print("Household demand: {} kWh".format(house_print))
    
        solar_print = [round(num,2) for num in solar_used]
        print("Solar used by house: {} kWh".format(solar_print))
    
        solar_print = [round(num,2) for num in solar_energy_battery]
        print("Solar stored in battery: {} kWh".format(solar_print))

        micro_print = [round(num,2) for num in micro_grid_used]
        print("Microgrid energy used: {} kWh".format(micro_print))

        main_print = [round(num,2) for num in main_grid_used]
        print("Maingrid energy used: {} kWh".format(main_print))

        ##################################
        # Printing running totals
        print("\nRUNNING TOTALS:")
    
        print("Battery charge: {} kWh".format(round(battery.current_charge,2)))
        print("Battery average cost: {} $/kWh".format(round(battery.average_cost,2)))
    
        main_print = [round(num,2) for num in house_running_main_grid_usage]
        print("maingird running usage: {} kWh".format(main_print))
    
        main_print = [round(num,2) for num in house_running_cost_main_grid]
        print("maingird running cost: ${}".format(main_print))
    
        micro_print = [round(num,2) for num in house_running_micro_grid_usage]
        print("microgird running usage: {} kWh".format(micro_print))
    
        micro_print = [round(num,2) for num in house_running_cost_micro_grid]
        print("microgird running cost: ${}".format(micro_print))
    
        for i in range(number_of_houses):
            tmp_list[i] = solar_used_running[i][i_running]
        solar_print = [round(num,2) for num in tmp_list]
        print("Solar running usage: {} kWh".format(solar_print))
    
        solar_profit_print = [round(num,2) for num in solar_profit]
        print("solar running profit: ${}".format(solar_profit_print))

    ##################################
    # Recording some historical values
    # record date
    date_historical[i_running] = dt
    # record battery state
    battery_charge_historical[i_running] = battery.current_charge
    battery_avg_historical[i_running] = battery.average_cost
    i_running += 1

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
for i in range(number_of_houses):
    for j in range(int(screen_len/2)):
        print('-', end='')
    print("\nHOUSE {}".format(i))
    print("total energy used: {}kWh".format(round(house_running_demand[i], 2)))
    print("maingrid cost: ${}".format(round(house_running_cost_main_grid[i], 2)))
    print("microgrid cost: ${}".format(round(house_running_cost_micro_grid[i], 2)))
    print("solar produced: {}kWh".format(round(house_running_solar_produced[i], 2)))

####################################################################
# CHARTS, GRAPHS, & PLOTS
####################################################################
# Making pie charts
pie_labels = 'Solar', 'Maingrid', 'Microgrid'
fig_pie, axs_pie = plt.subplots(2,2)
pie_data = [0] * number_of_houses
for i in range(number_of_houses):
    pie_data[i] = [solar_profit[i], house_running_cost_main_grid[i], house_running_cost_micro_grid[i]] # TODO make this a percent
axs_pie[0,0].pie(pie_data[0], labels=pie_labels, autopct='%.1f')
axs_pie[0,1].pie(pie_data[1], labels=pie_labels, autopct='%.1f')
axs_pie[1,0].pie(pie_data[2], labels=pie_labels, autopct='%.1f')
axs_pie[1,1].pie(pie_data[3], labels=pie_labels, autopct='%.1f')

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
fig_eng, axs_bat = plt.subplots(2,2)

######################################
# Plotting home energy cost 
fig_cost, axs_cost = plt.subplots(2,2)

# Plot
plt.show()
