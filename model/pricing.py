####################################################################
# FUNCTIONS
####################################################################
# return the cost of power from the maingrid (dollars/kWh)
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
