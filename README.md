## energyStore 
This GitHub repo is for the Boston University Senior Design team, EnergyStore. 
The goal of EnergyStore is to create an energy microgrid for small communities centered around a communal smart battery.

### Functionality
#### Host (Battery Unit):
* NETWORKING
    * Maintain remote connection home unit
    * Send instructions to home unit for switching grid connections
* MEASURING
    * Measure power delivered to homes
    * Measure power recieved from homes
    * Measure battery temperature and charge to be used in battery ML measure
* MODELING
    * Run ML model to predict charging and discharging efficieny of battery
    * Run ML to forward project cost of maingrid power

#### Client (Home Unit):
* NETWORKING
    * Maintain remote connection to Battey Unit (incase of no connection, use maingrid power)
* MEASURING
    * verify state of switch between maingrid and microgid - share with Battery Unit
* ACTIONS
    * Drive switching between maingrid power and microgrid power 

