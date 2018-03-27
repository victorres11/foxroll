import csv

def process_csv(file_path):
    with open(file_path, 'rb') as opened_csvfile:
        reader = csv.DictReader(opened_csvfile)
        csv_output = []
        for line in reader:
            csv_output.append(line)
        return csv_output
