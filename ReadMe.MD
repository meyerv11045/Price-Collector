## Price Collector 
Collects price data from Walmart and Kroger using their APIs. 

### Setting up the Environment
1. Clone or download this repository
2. Create a `config.ini` file and add the following details from your reigstered Kroger App:
``` 
[KrogerApi]
client_id = insertHere
client_seceet = insertHere
```
3. Install the necessary requirements with pip (see below)

### Requirements:
`requests`: used to make HTTP requests to the APIs

Install the requirments with: `pip install requests` 

### Collecting the Prices
The core functionality for collecting Kroger and Walmart prices as well as other data is stored within `kroger.py` and `walmart.py` respectively. 

After running `python walmart.py` or `python kroger.py`, you will be prompted to enter the name/path to the input and output csv files. If the files are located in the same directory as the python scripts, all that needs to be specified is the name, otherwise specify the directory too (e.g. `./data/input.csv`). The scripts will create the output file at the specified location w/ the specified name.