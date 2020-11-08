import defines
#import monitor_top

#######################################################################
# Battery Obj
#######################################################################
# This is used to simulate the battery that powers the entire system


class Battery:

    def __init__(self):
        self.name = defines.BATTERY_NAME
        self.charge_rate = 0.0
        self.discharge_rate = 0.0
        self.curr_charge = 0.0
        self.max_capacity = defines.BATTERY_MAX_CAPACITY
        self.average_cost = 0.0

    def charge(self):
        # TODO
        # Here when charge is added, also need to update the avgCost of the Battery
        # - how often do we do this?
        pass

    def discharge(self):
        # TODO
        # update the current charge
        pass

    def updateAvgCost(self):
        # TODO

        pass
