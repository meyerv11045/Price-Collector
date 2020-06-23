import csv
import re
import requests

class WalmartCore:
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
        """ Takes a Walmart product id and returns the url
            for that product after calling the API

        Args:
            item_id (str or int): walmart product id

        Returns:
            str: The grocery.walmart url to the product
        """
        resp = self.get_product(item_id,field='basic')
        try:
            url = resp["basic"]["productUrl"]
            return f'https://grocery.walmart.com{url}'
        except KeyError:
            return 'No URL'

class WalmartPrices(WalmartCore):
    def __init__(self, input_file_name, output_file_name):
        super().__init__(input_file_name, output_file_name)

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

class WalmartGlutenFree(WalmartCore):
    def __init__(self, input_file_name, output_file_name):
        super().__init__(input_file_name, output_file_name)
        self.gluten_ingredients =  ['barley', 'breading', "brewer's yeast", 'bulgur', 'durum', 'farro', 'faro', 'spelt', 'dinkel', 'graham flour', 'hydrolyzed wheat protein', 'kamut', 'malt', 'malt extract', 'malt syrup', 'malt flavoring', 'malt vinegar', 'malted milk', 'matzo', 'matzo meal', 'modified wheat starch', 'oatmeal', 'oat bran', 'oat flour', 'whole oats', 'rye flour', 'seitan', 'semolina', 'triticale', 'wheat bran', 'wheat flour', 'wheat germ', 'wheat starch', 'atta', 'einkorn', 'emmer', 'farina', 'fu']

    def is_gluten_free(self,response):
        """ Parses the JSON response from the Walmart API 
            to determine if the product is gluten free

        Args:
            response (dict): product info JSON response from Walmart API 

        Returns:
            boolean: True for GF, False for Contains Gluten
        """
        if type(response) == str: 
            return response #Handles HTTP error strings
        try:
            detailed = response['detailed']
            try:
                #Look at product description first to see if GF
                description = detailed['description']
                if re.search('[gG]luten [fF]ree',description) != None:
                    return True
                #Use more indepth ingredient method to see if GF
                else:
                    ingredients = detailed['ingredients']
                    return self.check_ingredients(ingredients)
            except KeyError: 
                return 'NA'
        except KeyError:
            return 'NA'

    def check_ingredients(self,prod_ingredients):
        """ Takes a string of ingredients and uses regex to determine
            if there are any gluten ingredients in the product

        Args:
            prod_ingredients (str): String of ingredients for a product 

        Returns:
            boolean: Returns True for GF ingredients, False for ingredients w/ gluten
        """
        for ingredient in self.gluten_ingredients:
            if re.search(ingredient,prod_ingredients,re.IGNORECASE) != None:
                return False
        return True 

    def label_GF_products(self):
        """ Takes a csv file of walmart product ids and labels them as GF 
            or not, writing the results to a new file

        Raises:
            SystemExit: If Walmart resets/ends the connection because of too many consecutive
                        API calls from one IP address, the script terminates
        """
        with open(self.input_file_name,'r') as read, open(self.output_file_name,'w') as write:
            csv_reader, csv_writer = csv.reader(read),csv.writer(write)

            #Skip & Write Headers
            next(csv_reader)
            csv_writer.writerow(['Product Id','Gluten Free'])

            for val,line in enumerate(csv_reader):
                item = line[0]
                try:
                    response = self.get_product(item,field='detailed')
                    gf = self.is_gluten_free(response)
                    print(f'{val+1} | {item}: {gf}')
                    csv_writer.writerow([item,gf])
                except ConnectionResetError as e:
                    print(f'Ended on item # {val + 1} | ID: {item}')
                    raise SystemExit(e)

if __name__ == '__main__':
    mode = input('Enter GF for to flag products as gluten free or P to collect prices: ')
    input_file = input('Enter path to walmart input file: ')
    output_file = input('Enter path to walmart output file: ')
    if mode == 'P':
        walmart_prices = WalmartPrices(input_file,output_file)
        walmart_prices.collect_prices()
    elif mode == 'GF':
        walmart_gf = WalmartGlutenFree(input_file,output_file)
        walmart_gf.label_GF_products()
    else:
        print('No mode (GF or P) entered')