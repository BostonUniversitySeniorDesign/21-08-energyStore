##########################
# This is our simmulation
# may god help us lmao
##########################
import datetime
import time

################################
# GENERICS FOR SIMMULATION
################################
battery_charge = 0
number_of_houses = 4
house_running_cost = [0] * number_of_houses

#both of these probably date time things
dt = datetime.datetime.now()
dt = dt.replace(microsecond=0, second=0, minute=0, hour=0, day=1, month=1, year=2020)

interval_length = 5 #(minutes)
interval_count = 105120
#1 hour 60/interval_length = 12
#1 day 1440/interval_length = 288
#30 days 43200/interval_length = 8640
#180 days 259200/interval_length = 51840
#365 days 525600/interval_length = 105120

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

################################
# Functions for simmulation
################################
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

def house_data_call(date, time, interval_length, x):
    # return energy used starting at date, time
    # for length of time = interval_length
    # in units kWh
    # x is house num == year of data ie year1.txt, year2.txt
    return 1


battery = Battery_obj()

    
################################
# MAIN LOOP
################################
timer_start = time.time()
while interval_count != 0:

    #decrement interval
    print(interval_count)
    interval_count -= 1
    

    #TODO charge battery: for now we can ignore this probably
    #battery.charge(amount?, 0) #charge from solar for increment
    #TODO add some sort of logic for this
    amount = 4
    battery.charge(amount, get_maingrid_cost()) #charge from main grid
        

    #TODO discharge battery per 4 houses
    for x in range(number_of_houses):
        date_inq = dt.date()
        time_inq = dt.time()
        energy_used = house_data_call(date_inq, time_inq, interval_length, x)
        if (battery.average_cost < get_maingrid_cost()) and (battery.current_charge > energy_used):
            house_running_cost[x] += battery.discharge(energy_used)
        else:
            house_running_cost[x] += energy_used * get_maingrid_cost()


    #add increment_length  to current date time
    dt += datetime.timedelta(minutes=interval_length)
    print(dt)





##### END
timer_end = time.time()
print('finished in {} seconds'.format(timer_end-timer_start))

