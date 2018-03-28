import csv

def parse_csv_into_dict(csv_string):
    reader = csv.DictReader(csv_string)
    parsed_output = []
    for line in reader:
        parsed_output.append(line)
    return parsed_output


def process_csv_file(file_path):
    with open(file_path, 'rb') as opened_csvfile:
        reader = csv.DictReader(opened_csvfile)
        csv_output = []
        for line in reader:
            csv_output.append(line)
        return csv_output
