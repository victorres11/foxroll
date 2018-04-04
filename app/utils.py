from process_csv import parse_csv_into_dict
from api import segment_api_call

def parse_csv_and_call_segment(segment_write_key, user_id_header, parce_csv_func, parse_csv_arg):
    """Wrapper function to combine the csv parsing and segmetn api calls together.
    Redis seems to require the function that is added to the queue to be imported and
    not written directly in the main moduel"""
    parsed_csv = parce_csv_func(parse_csv_arg)
    print "{} - {}".format(segment_write_key, user_id_header)
    segment_api_call(segment_write_key, user_id_header, parsed_csv)
