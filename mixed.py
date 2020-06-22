from kroger import KrogerPriceCollector
from walmart import WalmartPriceCollector
import csv

#Setup/Initialization
input_file = input('Enter Path to Input File: ')
output_file = input('Enter Path to Output File: ')

krg = KrogerPriceCollector('','')
krg.get_credentials()
krg.get_access_token()

wmt = WalmartPriceCollector('','')

def check(line):
    if line == 'NA':
        return 'NA'
    elif len(line) == 13:
        return krg.find_price(krg.get_product(line))
    else:
        return wmt.find_price(wmt.get_product(line),line)[0]

with open(input_file,'r') as f,open(output_file,'w') as f2:
    csv_reader,csv_writer = csv.reader(f),csv.writer(f2)
    next(csv_reader)
    csv_writer.writerow(['Product Id','Price'])
    for line in csv_reader:
        item = line[0]
        price = check(item)
        print(f'{item}: ${price}')
        csv_writer.writerow([item,price])


