# 6/11/2020

import csv
import requests
from time import time

def load_products(file_name):
    """ Returns an list of strings loaded from an input csv file

    Args:
        file_name (string): name of the csv file to be loaded

    Returns:
        [list]: A list of product id strings
    """
    with open(file_name,'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader) #Skips over header    
        products = []
        for line in csv_reader:
            products.append(line[0])
        return products

def get_prod_info(prod_id,field='store',storeId=2250):
    """ Calls Walmart internal API for specified product and returns the info as a dictionary

    Args:
        prod_id (string or int): Walmart product/item id to be searched for
        field (str, optional):  Specifies what fields are returned from API call 
                                (basic, detailed, nutritionFacts, store, all). Defaults to 'store'.
        storeId (int, optional): Specifies the Walmart location for items to be searched at. 
                                 Defaults to 2250 (4000 Red Bank Rd, Cincinnati, OH).

    Returns:
        [dict]: A dictionary following the json structure of the response
    """
    url = f'https://grocery.walmart.com/v3/api/products/{prod_id}?itemFields={field}&storeId={storeId}'
    r = requests.get(url)
    if r.status_code == 404:
        return 'Product Not Found'     
    elif r.status_code > 404:
        return 'HTTP Error Occured'
    else:
        return r.json()   

def parse_response(response):
    """ Parses through the json dictionary to find the price of the item
        Uses error handling to deal with different response bodies and keys

    Args:
        response (dict or str)): [description]

    Returns:
        [str]: A price or an error message
    """
    
    if type(response) == str: 
        return response #Handles HTTP error strings
    try:
        store = response['store']
        price = store['price']
        try:
            try:
                listPrice = price['list']
                return str(listPrice)
            except KeyError:
                displayPrice = price['displayPrice']
                return str(displayPrice)
        except KeyError:
            #Future version can call for basic field to get the url
            #Then a scraper can find the price on the website
            if not store['isInStock']:
                return 'Out of Stock'
            else: 
                return 'FIND'
    except KeyError:
        return 'DNE'

def write_to_csv(file_name,rows):
    """ Writes the product id and its price to a new csv file

    Args:
        file_name (string): name of the file to be written to
        column1 (list): list of product ids
        column2 (list): list of prices
    """
    with open(file_name,'w') as csv_file:
        csv_writer = csv.writer(csv_file)
        csv_writer.writerow(['Product Id','Price'])
        for row in rows:
            csv_writer.writerow(row)

def main(input_file_name,output_file_name):
    """ Loads the input data, collects the prices from the walmart API, 
        and writes the results to a new csv file 

    Args:
        input_file_name (str): path to the input csv file
        output_file_name (str): path to the output csv file

    Raises:
        SystemExit: If Walmart resets/ends the connection because of too many consecutive
                    API calls from one IP address, the script terminates
    """
    start = time()
    product_ids = load_products(input_file_name)
    rows = []
    
    for val, item in enumerate(product_ids):
        try:
            response = get_prod_info(item)
            price = parse_response(response)
            rows.append([item,price])
            print(f'{val}| {item}: ${price}')
        except ConnectionResetError as e:
            print(f'Ended on item # {val + 1} | ID: {item}')
            raise SystemExit(e)
    
    write_to_csv(output_file_name,rows)
    end = time()
    print(f'Finished {len(rows)} items in {end-start // 60} minutes')

if __name__ == '__main__':
    input_file = input("Enter the path to the input file: ")
    output_file = input("Enter the path to the output file: ")

    main(input_file,output_file)