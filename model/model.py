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
dt = dt.replace(microsecond=0, second=0, minute=0, hour=0, day=1, month=1, year=2020)

interval_length = 5 #(minutes)
interval_count = 105120
# given interval_length == 5
#1 hour 60/interval_length = 12
#1 day 1440/interval_length = 288
#30 days 43200/interval_length = 8640
#180 days 259200/interval_length = 51840
#365 days 525600/interval_length = 105120

####################################################################
# CLASSES
####################################################################
class Battery_obj:

    def __init__(self):
        #TODO figure out some guestimates for this
        self.name = "SIM_BATTERY"
        self.charge_rate = 0.0 #(units?)
        self.discharge_rate = 0.0 #(units?)
        self.current_charge = 0.0 #(kWh)
        self.max_capacity = 0.0 #(kWh)
        self.average_cost = 0.0 #(USD/kWh)

    # cost (dollars), 0 if from battery, otherwise get_maingrid_cost
    def charge(self, amount, cost):
        # TODO
        # Here when charge is added, also need to update the avgCost of the Battery
        # - how often do we do this?
        # also update avg charge
        pass

    def discharge(self, amount):
        self.curr_charge -= amount
        return amount * self.average_cost #return cost of this charge

####################################################################
# FUNCTIONS 
####################################################################
# return the cost of power from the maingrid (dollars/kWh)
# using this as refrence https://www.sce.com/residential/rates/Time-Of-Use-Residential-Rate-Plans
# for now this is using the TOU-D-4-9PM plan, TODO: add other plans
def get_maingrid_cost():

    month = datetime.datetime.today().month
    if (month >= 6) and (month <= 9):
        summer = True
    else:
        summer = False
    day_num = datetime.datetime.today().weekday()

    if day_num > 4:
        weekend = True
    else:
        weekend = False
    
    hour = datetime.datetime.now().hour
    
    if summer:
        if (hour >= 16) and (hour <= 21): #4pm-9pm
            if weekend: #summer, weekend, peak
                return 0.34
            else: #summer, weekday, peak
                return 0.41
        else:#summer, weekend and weekday, off-peak
            return 0.26
    else:
        if hour >= 21: #winter, weekend and weekday, off-peak
            return 0.27
        elif hour >= 16: #winter, weekend and weekday, peak 
            return 0.36
        else: #winter, weekend and weekday, super off-peak
            return 0.25

####################################################################
# MAIN
####################################################################
# set up battery object
battery = Battery_obj()

#set up timer
timer_start = time.time()
interval_count_historic = interval_count

number_of_houses = 4 #do not change, this is hardcoded for our data 
house_running_cost_main_grid = [0] * number_of_houses
house_running_cost_micro_grid = [0] * number_of_houses

#load csv data into pandas dataframes
print("loading data for household energy usage")
house1_df = pandas.read_csv(os.path.join(os.getcwd(),"year1.txt"))
house2_df = pandas.read_csv(os.path.join(os.getcwd(),"year2.txt"))
house3_df = pandas.read_csv(os.path.join(os.getcwd(),"year3.txt"))
house4_df = pandas.read_csv(os.path.join(os.getcwd(),"year4.txt"))
#collect dataframes into list and modify
df_list = [house1_df, house2_df, house3_df, house4_df]
x = 0
for df in df_list:
    #drop un-needed data 
    df = df.drop(['Global_reactive_power', 'Voltage', 'Global_intensity', 'Sub_metering_1', 'Sub_metering_2', 'Sub_metering_3'], axis=1)
    #string manipulation, this can probably be done better but it's okay for now
    for (columnName, columnData) in df.iteritems():
        if columnName == "Date":
            i = 0
            dates_new = ['']*len(columnData)
            for date in columnData:
                dates_new 
                date_list = date.split('/')
                date_new = date_list[1] + '/' + date_list[0]
                dates_new[i] = date_new
                i+=1
            print(dates_new)
    df = df.drop(['Date'], axis=1)
    df['Date'] = dates_new
    df_list[x] = df
    x+=1

####################################################################
# MAIN LOOP
####################################################################
print("Starting main loop")
while interval_count != 0:

    ##################################
    #decrement interval
    #print(interval_count)
    interval_count -= 1
    

    #TODO charge battery: for now we can ignore this probably
    #battery.charge(amount?, 0) #charge from solar for increment
    #TODO add some sort of logic for this
    amount = 4
    battery.charge(amount, get_maingrid_cost()) #charge from main grid

    #TODO get demand for energy
    house_demand = [0] * number_of_houses
    for i_interval in range(interval_length): #iterate through interval length
        #get date & time
        date_ = str(dt.month) + '/' + str(dt.day)
        time_ = str(dt.time()).split('.')[0]
        print('date {} time {}'.format(date_,time_))
        for i_num_houses in range(number_of_houses):
            df_tmp = df_list[i_num_houses]
            energy = float(df_tmp.loc[(df_tmp['Date']==date_) & (df_tmp['Time']==time_)]['Global_active_power'].item())/60
            house_demand[i_num_houses] += energy 
        dt += datetime.timedelta(minutes=1) #increment date time
    
    #TODO discharge battery per 4 houses
    for j_num_houses in range(number_of_houses):
        #energy_used == house_demand
        if (battery.average_cost < get_maingrid_cost()) and (battery.current_charge > house_demand[j_num_houses]):
            house_running_cost_micro_grid[j_num_houses] += battery.discharge(house_demand[j_num_houses])
        else:
            house_running_cost_main_grid[j_num_houses] += house_demand[j_num_houses] * get_maingrid_cost()
    print("maingird: {}".format(house_running_cost_main_grid))
    print("microgird: {}".format(house_running_cost_micro_grid))

##################################
# END
timer_end = time.time()
print('finished in {} seconds'.format(timer_end-timer_start))
for x in range(number_of_houses):
    print('house {} paid {} dollars for their energy consumed in {} minutes'.format(x, house_running_cost[x], interval_count_historic * interval_length))
