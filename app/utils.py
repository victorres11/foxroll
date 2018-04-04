from process_csv import parse_csv_into_dict
from api import segment_api_call
import os
import csv


def shard_csv(filehandler, delimiter=',', row_limit=200000,
    output_name_template='output_%s.csv', output_path='.', keep_headers=True):
    """
    Splits a CSV file into multiple pieces.

    A quick bastardization of the Python CSV library.
    Arguments:
        `row_limit`: The number of rows you want in each output file. 10,000 by default.
        `output_name_template`: A %s-style template for the numbered output files.
        `output_path`: Where to stick the output files.
        `keep_headers`: Whether or not to print the headers in each output file.
    Example usage:

        >> from toolbox import csv_splitter;
        >> csv_splitter.split(open('/home/ben/input.csv', 'r'));

    """

    reader = csv.reader(filehandler, delimiter=delimiter)
    current_piece = 1
    current_out_path = os.path.join(
         output_path,
         output_name_template  % current_piece
    )
    current_out_writer = csv.writer(open(current_out_path, 'w'), delimiter=delimiter)
    current_limit = row_limit

    output_paths = []
    output_paths.append(current_out_path)

    if keep_headers:
        headers = reader.next()
        current_out_writer.writerow(headers)
    for i, row in enumerate(reader):
        if i + 1 > current_limit:
            current_piece += 1
            current_limit = row_limit * current_piece
            current_out_path = os.path.join(
               output_path,
               output_name_template  % current_piece
            )
            current_out_writer = csv.writer(open(current_out_path, 'w'), delimiter=delimiter)
            output_paths.append(current_out_path)
            if keep_headers:
                current_out_writer.writerow(headers)
        current_out_writer.writerow(row)

    return output_paths


def parse_csv_and_call_segment(segment_write_key, user_id_header, parse_csv_func, parse_csv_arg):
    """Wrapper function to combine the csv parsing and segmetn api calls together.
    Redis seems to require the function that is added to the queue to be imported and
    not written directly in the main moduel"""



    parsed_csv = parse_csv_func(parse_csv_arg)
    print "{} - {}".format(segment_write_key, user_id_header)
    segment_api_call(segment_write_key, user_id_header, parsed_csv)
