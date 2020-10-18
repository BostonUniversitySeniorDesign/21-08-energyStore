# energyStore #
The GitHub repo for the team energyStore


Functionality
Host (Battery Unit):
markup: * M
* Maintain remote connection home unit
* Send instructions to home unit for switching grid connections

* Measure power delivered to homes
* Measure power recieved from homes
* Measure battery temperature and charge to be used in battery ML measure

* Run ML model to predict charging and discharging efficieny of battery
* Run ML to forward project cost of maingrid power


Client (Home Unit):
* Maintain remote connection to Battey Unit (incase of no connection, use maingrid power)
* Drive switching between maingrid power and microgrid power 
* verify state of switch between maingrid and microgid - share with Battery Unit




