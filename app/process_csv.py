import csv

def parse_csv_into_dict(csv_string, limit=None):
    reader = csv.DictReader(csv_string)
    parsed_output = []
    for line in reader:
        parsed_output.append(line)

        if limit and len(parsed_output) > limit:
            return parsed_output

    return parsed_output


def process_csv_file(filepath, limit=None):
    with open(filepath, 'rb') as opened_csvfile:
        reader = csv.DictReader(opened_csvfile)
        csv_output = []

        for line in reader:
            csv_output.append(line)

            if limit and len(csv_output) > limit:
                return csv_output

        return csv_output

def count_rows(filepath):
    """Count number of rows present in a csvfile."""
    with open(filepath, 'rb') as opened_csvfile:
        csv_file = csv.reader(opened_csvfile)
        row_count = sum(1 for row in csv_file)

    return row_count
