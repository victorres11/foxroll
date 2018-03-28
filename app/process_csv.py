import csv

def process_csv(file_path):
    with open(file_path, 'rb') as opened_csvfile:
        parse_csv_into_dict(opened_csvfile)

def parse_csv_into_dict(csv_string):
    reader = csv.DictReader(csv_string)
    parsed_output = []
    for line in reader:
        parsed_output.append(line)
    return parsed_output
