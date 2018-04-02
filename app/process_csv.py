import csv

def parse_csv_into_dict(csv_string, limit=None):
    reader = csv.DictReader(csv_string)
    parsed_output = []
    for line in reader:
        parsed_output.append(line)

        if limit and len(parsed_output) > limit:
            return parsed_output

    return parsed_output


def process_csv_file(file_path, limit=None):
    with open(file_path, 'rb') as opened_csvfile:
        reader = csv.DictReader(opened_csvfile)
        csv_output = []

        for line in reader:
            csv_output.append(line)

            if limit and len(csv_output) > limit:
                return csv_output

        return csv_output
