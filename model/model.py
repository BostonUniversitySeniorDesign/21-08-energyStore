#!/usr/bin/env python3
############################
### IMPORTS ###
import datetime
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

PRINTS=True

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
# Utility function for getting the index for the pandas df
def get_Date_Time_solarTime(dt):
    day_t = dt.day
    month_t = dt.month

    if month_t < 10:
        month_t = '0' + str(dt.month)
    else:
        month_t = str(dt.month)

    if day_t < 10:
        day_t = '0' + str(dt.day)
    else:
        day_t = str(dt.day)

    date = month_t + '/' + day_t
    # dataframes store time two different ways so we need both of these
    time = str(dt.time()).split()[0]
    solar_time = dt.time()
    return (date, time, solar_time)


# Returns the cost of power from the maingrid (dollars/kWh)
# using this as refrence https://www.sdge.com/whenmatters

# takes the current date as a datetime object,
# along with the usage so far for the current month
# to determine the tier: tier 1 under 130%
def get_maingrid_cost(dt, monthly_usage):

    # get current month and day
    month = dt.month
    hour = dt.hour

    # determine energy tier 
    if (month >= 6) and (month <= 10): # Coastal, summer (June 1 - Oct 31), all electric
        # 130% of Baseline is 234 kWh monthly
        if monthly_usage > 234:
            tier = 2
        else:
            tier = 1
    else:                             #   Coastal, winter (Nov 1 - May 31), all electric
        # 130% of Baseline is 343 kWh monthly
        if monthly_usage > 343:
            tier = 2
        else:
            tier = 1

    # Peak hours defined as 4PM to 9PM
    if (hour >= 4) and (hour <= 9):
        peak = True
    else:
        peak = False

    # Pricing differs per month
    if (month == 1) or (month == 2):    # january and february
        if peak:                            # peak
            if tier == 1:
                return .21262               
            else:
                return .37274
        else:                               # off peak
            if tier == 1:
                return .20864
            else:
                return .36576

    elif (month == 3) or (month == 4):  # march and april
        if peak:                            # peak
            if tier == 1:
                return .20775
            else:
                return .36419
        else:
            if tier == 1:                   # off peak
                return .20376
            else:
                return .35721
        
    elif (month == 5):                  # may
        if peak:
            if tier == 1:
                return .22034
            else:
                return .29994
        else:
            if tier == 1:
                return .21522
            else:
                return .29296

    elif (month >= 6) and (month <= 10):  # june to october
        if peak:
            if tier == 1:
                return .34163
            else:
                return .46503
        else:
            if tier == 1:
                return .27906
            else:
                return .37986

    elif (month >= 11):                  # november and december
        if peak:
            if tier == 1:
                return .23040
            else:
                return .31363
        else:
            if tier == 1:
                return .22528
            else:
                return .30666


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

# keeps track of solar profit
solar_profit = [0] * number_of_houses

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
(date, time_i, solar_time) = get_Date_Time_solarTime(dt)

# need to get current day weather before any other iteration
daily_weather = df_weatherdata.loc[(
    df_weatherdata['Date'] == date)]['Conditions'].item()

####################################################################
# LIST FOR STORING SIMMULATION DATA
####################################################################
i_running = 0
# For time
date_historical = [0] * interval_count
# For running cost
solar_profit_historical = [([0] * interval_count), ([0] * interval_count), ([0] * interval_count), ([0] * interval_count)] #$
#house_running_cost_micro micro_cost_historical = [([0] * interval_count), ([0] * interval_count), ([0] * interval_count), ([0] * interval_count)] #$
#house_running_cost_main main_cost_historical = [([0] * interval_count), ([0] * interval_count), ([0] * interval_count), ([0] * interval_count)] #$
# For running usage
solar_used_running = [([0] * interval_count), ([0] * interval_count), ([0] * interval_count), ([0] * interval_count)] #kWh
# For other
solar_produced_running = [([0] * interval_count), ([0] * interval_count), ([0] * interval_count), ([0] * interval_count)] #kWh
battery_charge_historical = [0] * interval_count
battery_avg_historical = [0] * interval_count


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
    # Get demand for energy per-household
    # step datetime 5 minutes for every interval 
    print("Calculating energy usage")
    house_demand_total = [0] * number_of_houses

    # Every hour we do something with house energy
    if (dt.minute % 60) == 0:
        for i in range(number_of_houses):
            curr_house = house_usage_dfs[i]
            house_demand_total[i] += float(curr_house.loc[(curr_house['Date'] == date) & (curr_house['Time'] == time_i)]['Usage'].item()) #kWh
            house_running_demand_monthly[i] += float(curr_house.loc[(curr_house['Date'] == date) & (curr_house['Time'] == time_i)]['Usage'].item()) #kWh

    ##################################
    # Get solar production per-household
    solar_produced = [0] * number_of_houses
    solar_energy_battery = [0] * number_of_houses
    solar_used = [0] * number_of_houses
    house_demand = [0] * number_of_houses

    # use current weather to index into solar to get every 5 minutes
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

    # Get solar produced per house
    for i in range(number_of_houses):
        solar_produced[i] = solarProduced # (kWh)
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
            # solar_used_running[i] += solar_produced[i]
            solar_used[i] = solar_produced[i]
            house_demand[i] = house_demand_total[i] - solar_produced[i]
            excess_energy = 0

        # charge battery
        battery.charge(excess_energy, 0)
        solar_energy_battery[i] = excess_energy

    curr_day = dt.day
    current_month = dt.month

    # increment date time every 5 minutes
    dt += datetime.timedelta(minutes=5)

    # get current date time and solar time to index into pandas df with
    (date, time_i, solar_time) = get_Date_Time_solarTime(dt)

    # reset monthly sum of energy when month changes
    if (current_month != dt.month):
        for j in range(number_of_houses):
            house_running_demand_monthly[j] = 0.0

    if (curr_day != dt.day):
        # every 24 hours we get the new weather condition
        daily_weather = df_weatherdata.loc[(
            df_weatherdata['Date'] == date)]['Conditions'].item()


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
        # print("GHI: {} Wh/m2".format(round(GHI,2)))
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
'''
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
'''