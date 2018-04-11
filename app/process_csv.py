import csv

def parse_csv_into_dict(csv_string, limit=None):
    """
    Parse strings into a list of dictionaries, where the key is the header and
    value is the corresponding value.

    We'll automatically convert strings into integers.

    [{'userId': 'foo-123', 'count_cool_cucumber': 4, first_order_date': '2017-05-30T20:37:46.000Z'},]
    """
    reader = csv.DictReader(csv_string)
    parsed_output = []
    for line in reader:
        parsed_output.append(line)

        if limit and len(parsed_output) > limit:
            return parsed_output

        # This is a naive check (and mutation) to see if the string value can be
        # safely converted to an integer or float.
        for key, value in line.iteritems():
            if value and value.isdigit():
                line[key] = int(value)
            elif value and is_float(value):
                line[key] = float(value)

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

def is_float(input_string):
    """
    Check if number should be converted into a float. Decimals *and* integers
    will return true.

    Returns a boolean.
    """
    try:
        float(input_string)
        return True
    except ValueError:
        return False
