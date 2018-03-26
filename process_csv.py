import csv

def process_csv(csvfile):
    print "UPDATED"
    with open(csvfile.filename, 'rb') as opened_csvfile:
        # reader = csv.reader(opened_csvfile, delimiter=' ', quotechar='|')
        reader = csv.DictReader(opened_csvfile)
        csv_output = []
        for line in reader:
            print "loop in csv reader"
            print line
            csv_output.append(line)
        return csv_output
