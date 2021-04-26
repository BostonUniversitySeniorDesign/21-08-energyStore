### How to Run:
This simulation uses a virtul enviroment to store all the packages to better manage between different people:
- Install the most recent version of python (https://www.python.org/downloads/) along with pip 
- Install the venv package `pip install venv`
- To enter the virtual enviroment type the following:
    `source simulation-env/bin/activate`
- Once in the environment, install the required packages:       `python -m pip install -r requirements.txt`
- To leave the virtual environment at any point, type           `deactivate`



### References



Household energy usage is sourced from here:
https://machinelearningmastery.com/how-to-load-and-explore-household-electricity-usage-data/

Solar data is sourced from here:
https://nsrdb.nrel.gov/about/u-s-data.html
|Source|Location ID|City|State|Country|Latitude|Longitude|Time Zone|Elevation|LocalTimeZone|
|:-----|:----------|:---|:----|:------|:-------|:--------|:--------|:--------|:------------|
|NSRDB |89062      |N/A |N/A  |N/A    |34.61   |-118.54  |0        |807      |-8|

GHI is units wh/m2 in solar csv
