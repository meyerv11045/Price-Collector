## Data Collector 
Collects price and other product data from Walmart and Kroger using their APIs. 

### Setting up the Environment
1. Clone or download this repository
2. Create a `config.ini` file and add the following details from your reigstered Kroger App:
``` 
[KrogerApi]
client_id = insertHere
client_seceet = insertHere
```
3. Install the requests for making HTTP calls to the APIs with: `pip install requests` 

### Kroger API
- Price collection
- Other data can be collected by creating subclasses of `KrogerCore`

### Walmart API
- Price collection
- Gluten Free product collection
- Nutrition fact collection
- Other data can be collected by creating subclasses of `WalmartCore`

### Collecting Data from the APIs
The core functionality for collecting Kroger and Walmart prices as well as other data is stored within `kroger.py` and `walmart.py` respectively. 

After running `python walmart.py` or `python kroger.py`, you will be prompted to enter the name/path to the input and output csv files. If the files are located in the same directory as the python scripts, all that needs to be specified is the name, otherwise specify the directory too (e.g. `./data/input.csv`). The scripts will create the output file at the specified location w/ the specified name.

### Other Scripts
`mixed.py` is used to collect product information for a csv file with a mix of Kroger product ids and Walmart product ids

`analyze.py` is used to get statistics on how many prices were found for kroger and walmart by analyzing the output csv files