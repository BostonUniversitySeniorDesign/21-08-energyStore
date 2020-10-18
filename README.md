## energyStore 
This GitHub repo is for the Boston University Senior Design team, EnergyStore. 
The goal of EnergyStore is to create an energy microgrid for small communities centered around a communal smart battery.

### Functionality
#### Host (Battery Unit):
* NETWORKING
    * Maintain remote connection home unit
* MEASURING
    * Measure power delivered to homes
    * Measure power recieved from homes
    * Measure battery temperature and charge to be used in battery ML measure
* MODELING
    * Run ML model to predict charging and discharging efficieny of battery
    * Run ML to forward project cost of maingrid power
    * Maintain persistent measure of average cost of energy stored in battery
* ACTIONS
    * Cross compare the two ML models to charge battery in most cost efficient way
    * Send instructions to home unit for switching grid connections to use cheapest energy

#### Client (Home Unit):
* NETWORKING
    * Maintain remote connection to Battey Unit (incase of no connection, use maingrid power)
* MEASURING
    * Verify state of switch between maingrid and microgid - share with Battery Unit
* ACTIONS
    * Drive switching between maingrid power and microgrid power 

