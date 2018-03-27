import csv

def process_csv(csvfile):
    # import ipdb; ipdb.set_trace()
    with open(csvfile.filename, 'rb') as opened_csvfile:
        # reader = csv.reader(opened_csvfile, delimiter=' ', quotechar='|')
        reader = csv.DictReader(opened_csvfile)
        csv_output = []
        for line in reader:
            csv_output.append(line)
        return csv_output
