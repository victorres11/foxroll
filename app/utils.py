from process_csv import parse_csv_into_dict
from api import segment_api_call
import os
import csv
from s3_access import read_s3_file
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


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


def redis_worker_wrapper(segment_write_key, bucket_to_use, user_id_header, parse_csv_func, shard_filename):
    """
    This is the combination of functions we want to outsource to the worker.

    1. Read the contents of the shard that's in S3
    2. Parse that csv string into a usable dictionary
    3. Make segment API calls

    Arguments:
        `segment_write_key`: The write key which dictates what segment instance the data will be written to.
        `user_id_header`: The headers for the csv document.
        `parse_csv_func`: The type of parsing function we will use, outputs a dict.
        `shard_filename`: The filename for the shard.
    """
    logger.info("Reading s3 File...")
    s3_file_contents = read_s3_file(bucket_to_use, shard_filename)

    logger.info("Parsing s3_file contents...")
    parsed_csv = parse_csv_func(s3_file_contents)

    logger.info("Calling segment api with parsed csv contents...")
    segment_api_call(segment_write_key, user_id_header, parsed_csv)
