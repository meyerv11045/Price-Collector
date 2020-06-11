# 6/11/2020

import csv
import requests
from get_prices import load_products,get_prod_info, write_to_csv

def get_stats(input_file):
    """ Takes a csv file with product_id and price and prints how
        many products are Out of Stock and how many were Not Found

    Args:
        input_file (str): path to the csv file to be read/analyzed
    """
    with open(input_file,'r') as csv_file:
        csv_reader = csv.reader(csv_file)
        next(csv_reader) #Skips over header    
        not_found = 0
        out_of_stock = 0
        total = 0
        for line in csv_reader:
            total += 1
            if line[1] == 'Product Not Found': not_found += 1
            elif line[1] == 'Out of Stock': out_of_stock += 1
        print(f'Out of Stock: {out_of_stock} of {total}')
        print(f'Product Not Found: {not_found} of {total}')

def parse_output(input_file,output_file):
    """ Takes a csv file with product_id and price and writes to a new file the product ids
        of those that were Out of Stock and had no price returned in the API call

    Args:
        input_file (str): path to the input csv file
        output_file (str): path to the output csv file 
    """
    
    with open(input_file,'r') as reader, open(output_file,'w') as writer:
        csv_reader, csv_writer = csv.reader(reader), csv.writer(writer)
        next(csv_reader)
        csv_writer.writerow(['Product Id'])
        for line in csv_reader:
            if line[1] == 'Out of Stock':
                csv_writer.writerow([line[0]])

def get_url(input_file,output_file):
    """ Takes the csv file of product ids that were Out of Stock and calls Walmart API
        to get the product's url so the price can be web/manually scraped if it exists

    Args:
        input_file (str): path to csv file of Out of Stock product ids
        output_file (str): path to new csv file of Out of Stock product ids and their urls
    """
    products = load_products(input_file)
    rows = []
    for item in products:
        resp = get_prod_info(item,field='basic')
        try:
            url = resp["basic"]["productUrl"]
            rows.append([item,url])
        except KeyError:
            rows.append([item,'No URL'])
    write_to_csv(output_file,rows)

if __name__ == '__main__':    
   IN = input('Enter the path to the input file of Out of Stock product ids: ')
   OUT = input('Enter the path to the output file for urls: ')
   get_url(IN,OUT)