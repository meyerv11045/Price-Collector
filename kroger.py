#Vikram Meyer 6/15/2020
import csv
from os import getenv
from base64 import b64encode
from time import time

#pip3 install python-dotenv,requests
from dotenv import load_dotenv 
import requests 

class KrogerPriceCollector:
    def __init__(self,input_file_name,output_file_name):
        self.input_file_name = input_file_name
        self.output_file_name = output_file_name
        self.credentials = ''
        self.api_base = 'https://api-ce.kroger.com'
        self.access_token = ''
        self.location_id = '01400929' # 1 W Corry St, Cincinnati, OH 45219
    
    @staticmethod
    def url_to_uuid(input_name,output_name):
        """ Takes an csv input file of Kroger urls and writes the kroger
            product ids to a new csv file

        Args:
            input_name (str): Path to the input csv file
            output_name (str): Path to the output csv file
        """
        with open(input_name,'r') as f1, open(output_name,'w') as f2:
            csv_reader, csv_writer = csv.reader(f1), csv.writer(f2)
            next(csv_reader)
            csv_writer.writerow(['Product Id'])
            for line in csv_reader:
                clean = line[0].strip()
                product_id = clean.split('/')[5]

                csv_writer.writerow([product_id])
    
    def get_credentials(self):
        """ Loads the client id and client secret from the .env
            file and creates the credentials specified in the kroger
            api documentation using base64 encoding

        Raises:
            EnvironmentError:   CLIENT_ID or CLIENT_SECRET were not
                                set in the .env file
        """
        
        load_dotenv()
        
        client_id = getenv('CLIENT_ID')
        client_secret = getenv('CLIENT_SECRET')
        
        if client_id == None:
            raise EnvironmentError('Set CLIENT_ID in .env file')
        if client_secret == None:
            raise EnvironmentError('Set CLIENT_SECRET in .env file')
        
        print('Client ID and Secret retrieved from .env file')

        #Base64 Encoding client_id:client_secret to create credentials specified in Kroger API Docs
        combo = f'{client_id}:{client_secret}'.encode('utf-8')
        self.credentials = b64encode(combo).decode('utf-8')
        
        print('Credentials Created')
    
    def get_access_token(self):
        """ Calls the Kroger authentication API using the credentials
            property and sets the access token property as the api return value
        """
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
            'Authorization': f'Basic {self.credentials}'
        }
        payload = 'grant_type=client_credentials&scope=product.compact'
        r = requests.post(f'{self.api_base}/v1/connect/oauth2/token',headers=headers,data=payload) 
        r.raise_for_status()
        self.access_token = r.json()['access_token']
        print('Access Token Received')

    def get_product(self,item_id):
        """ Calls the kroger API for the specified product
            and returns the response as a dict 

        Args:
            item_id (str): The 13 digit Kroger product id (leading 0s are only retained in string form)

        Returns:
            dict: JSON response from API or empty dict signifying an empty response
        """
        url = f'{self.api_base}/v1/products/{item_id}?filter.locationId={self.location_id}'

        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }
        r = requests.get(url,headers=headers)
        
        #Checks for invalid/expired access token
        if r.status_code == 401:
            self.get_access_token()
            return self.get_product(item_id)
        
        if int(r.headers['content-length']) > 0:
            return r.json()
        else:
            return {}

    def find_price(self,response):
        """ Parses through the dictionary response
            and returns the price if available

        Args:
            response (dict): The JSON response from the Kroger API call for the product

        Returns:
            str: The price or parsing error message
        """
        try:
            items = response['data']['items'][0]
            try: 
                price =items['price']['regular']
                return price
            except KeyError:
                return 'No price'
        except KeyError: 
            return 'DNE'

    def collect_prices(self):
        """ Collects kroger prices for csv list of ids 
            specified under input_file property and writes the 
            prices to a new csv file under the path specified in the
            output_file property
        """
        with open(self.input_file_name,'r') as read, open(self.output_file_name,'w') as write:
            csv_reader, csv_writer = csv.reader(read),csv.writer(write)
            
            #Skip & Write Headers
            next(csv_reader)
            csv_writer.writerow(['Product Id','Price'])

            for val,line in enumerate(csv_reader):
                item = line[0]
                response = self.get_product(item)
                price = self.find_price(response)
                print(f'{val+1} | {item}: ${price}')
                csv_writer.writerow([item,price])

    def run(self):
        """ Calls authentication functions in proper order
            and then collects prices
        """
        start = time()
        self.get_credentials()
        self.get_access_token()
        self.collect_prices()
        end = time()
        print(f'Finished collecting Kroger prices in {end-start //60} minutes')

if __name__ == '__main__':
    #Preprocess the urls into uuids
    #KrogerPriceCollector.url_to_uuid('kroger_urls.csv','kroger_ids.csv')
    
    #Collect prices for the kroger uuids
    input_file = input('Enter path to kroger input file: ')
    output_file = input('Enter path to kroger output file: ')
    kroger = KrogerPriceCollector(input_file,output_file)
    kroger.run()