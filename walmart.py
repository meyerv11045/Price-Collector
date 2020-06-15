import requests
import csv
from time import time

class WalmartPriceCollector:
    def __init__(self,input_file_name,output_file_name):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.storeId = 2250 #4000 Red Bank Rd, Cincinnati, OH

    def get_product(self,item_id,field='store'):
        """ Calls Walmart internal API for specified product and returns the info as a dictionary

            Args:
                prod_id (string or int): Walmart product/item id to be searched for
                field (str, optional):  Specifies what fields are returned from API call 
                                        (basic, detailed, nutritionFacts, store, all). Defaults to 'store'.

            Returns:
                dict: A dictionary following the json structure of the response (or a str when errors occur)
        """
        url = url = f'https://grocery.walmart.com/v3/api/products/{item_id}?itemFields={field}&storeId={self.storeId}'
        r = requests.get(url)
        if r.status_code == 404:
            return 'Product Not Found'     
        elif r.status_code > 404:
            return 'HTTP Error Occured'
        else:
            return r.json()  

    def get_url(self,item_id):
        resp = self.get_product(item_id,field='basic')
        try:
            url = resp["basic"]["productUrl"]
            return f'https://grocery.walmart.com{url}'
        except KeyError:
            return 'No URL'

    def find_price(self,response,item):
        """ Parses through the json dictionary to find the price of the item
            Uses error handling to deal with different response bodies and keys

            Args:
                response (dict or str): JSON response (or string error msg) from the API call
            Returns:
                list: The first element is the price, the second element is the product's url if it is out of stock 
        """
        if type(response) == str: 
            return response #Handles HTTP error strings
        try:
            store = response['store']
            price = store['price']
            try:
                try:
                    listPrice = price['list']
                    return [str(listPrice),None]
                except KeyError:
                    displayPrice = price['displayPrice']
                    return [str(displayPrice),None]
            except KeyError:
                url = self.get_url(item)
                if not store['isInStock']:
                    return ['Out of Stock',url]
                else: 
                    return ['FIND',url]
        except KeyError:
            return 'DNE'
    
    def collect_prices(self):
        """ Loads the input data, collects the prices from the walmart API, 
            and writes the results to a new csv file 

            Raises:
                SystemExit: If Walmart resets/ends the connection because of too many consecutive
                            API calls from one IP address, the script terminates
        """    
        
        with open(self.input_file_name,'r') as read, open(self.output_file_name,'w') as write:
            csv_reader, csv_writer = csv.reader(read),csv.writer(write)
            
            #Skip & Write Headers
            next(csv_reader)
            csv_writer.writerow(['Product Id','Price'])

            for val,line in enumerate(csv_reader):
                item = line[0]
                try:
                    response = self.get_product(item)
                    price = self.find_price(response,item)
                    print(f'{val+1} | {item}: ${price[0]}')
                    csv_writer.writerow([item,price[0],price[1]])
                except ConnectionResetError as e:
                    print(f'Ended on item # {val + 1} | ID: {item}')
                    raise SystemExit(e)

    def run(self):
        start = time()
        self.collect_prices()
        end = time()
        print(f'Finished collecting Walmart prices in {end-start // 60} minutes')

if __name__ == '__main__':
    input_file = input('Enter path to walmart input file: ')
    output_file = input('Enter path to walmart output file: ')
    walmart = WalmartPriceCollector(input_file,output_file)
    walmart.run()
    