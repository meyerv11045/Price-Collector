## Price Collector 
Collects price data from Walmart using an API. 

### Requirements:
This script utilizes the requests library for making HTTP requests and the dotenv library for reading environment variables from a .env file
 `pip3 install requests,python-dotenv`

### Running the Program
The main functionality is in the `get_prices.py` script. The additional scripts are used to explore/analyze the data at various stages.

To collect prices run: `python3 get_prices.py` in the terminal.

When prompted, enter the relative path to the input and output files (Note: there is a folder for input files & output files respectively in the data folder) 
    
Ex: `./data/input/file_name.csv`
