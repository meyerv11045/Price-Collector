# 6/11/2020

import requests
from time import time
from get_prices import get_prod_info

def get_status(item):
    """ Return the HTTP response status code for the call to the walmart API

    Args:
        item (int or str): Walmart product id 

    Returns:
        int: HTTP status code
    """
    url = f'https://grocery.walmart.com/v3/api/products/{item}?itemFields=all&storeId=2250'
    return requests.get(url).status_code

def get_404_responses(input_file):
    """ Print the number of HTTP codes that are not ok
        When calling the API on product ids read from a txt file

    Args:
        input_file (str): path to the file to be read
    """
    start = time()
    fails = 0
    total = 0
    with open(input_file,"r") as f:
        lines = f.readlines()
        total = len(lines)
        for line in lines:
            if get_status(line.strip()) != 200:
                fails += 1
    end = time()

    print(f'{fails} out of {total} API calls had HTTP errors')
    print(f'Elapsed Time: {end - start} seconds')

def get_prices(input_file,output_file):
    """ 1) Reads a txt file of walmart product ids
        2) Calls Walmart API and parses response for price
        3) Writes the product id & the price to a new txt file

    Args:
        input_file (str): path to the txt file to be read
        output_file (str): path to the txt file to be written to
    """
    with open(input_file,'r') as read, open(output_file,'w') as write:
        lines = read.readlines()
        for line in lines:
            item = line.strip()
            resp = get_prod_info(item)
            try:
                store = resp["store"]
                try:
                    if not store["isInStock"]:
                        write.write(f'{item}: Out of Stock')
                    else:
                        price = store["price"]
                    try:
                        listPrice = price["list"]
                        write.write(f'{item}: ${listPrice}\n')
                    except KeyError:
                        write.write(f'{item}: KeyError with list attribute\n')        
                except KeyError:
                     write.write(f'{item}: KeyError with price attribute\n')
            except KeyError:
                write.write(f'{item}: Item does not exist in DB\n')


