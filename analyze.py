import csv

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

def parse_output(self,input_file,output_file):
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
