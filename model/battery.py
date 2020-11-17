# Assuming this is a 3 tesla powerwall
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
        self.MAX_CAPACITY = 40.5  # (kWh) 40.5
        self.DESIRED_CHARGE = 18.0 # (kWh) TODO figure out a way to calc this
        self.MIN_CHARGE = 9.0  # (kWh)
        self.MAX_CONTINUOUS_POWER = 17.4 # (kW) 17.4

    # cost (dollars), 0 if from battery, otherwise get_maingrid_cost
    def charge(self, amount, cost):
        if self.current_charge < self.MAX_CAPACITY:
            current_total_cost = self.current_charge * self.average_cost
            new_charge_cost = amount * cost
            self.current_charge += (amount * self.CHARGE_EFF)
            self.interval_continuous_power += amount
            new_total_cost = current_total_cost + new_charge_cost
            if self.current_charge != 0:
                self.average_cost = new_total_cost / self.current_charge
            else:
                self.average_cost = 0.0

    def discharge(self, amount):
        self.interval_continuous_power -= amount
        self.current_charge -= amount
        return amount * self.average_cost  # return cost of this charge
