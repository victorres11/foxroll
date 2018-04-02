import analytics
import logging
import datetime
from pytz import timezone

# logger setup
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

FOXROLL_SEGMENT_WRITE_KEY = "TRHR0eTFmnb6cdNcQD2GeTW6ds5k6MMO"
FOXROLL_EVENT_NAME = 'FoxRoll Updated User'

def on_error(error, items):
    print("An error occurred:", error)

analytics.on_error = on_error
analytics.debug = True

def event_api_call(client, user_id, timestamp):
    """Track foxroll updated user event."""
    logger.info("Event API Call for user: {}".format(user_id))
    client.track(user_id, FOXROLL_EVENT_NAME, {
    'date_updated': timestamp
    })

def identify_api_call(client, user_id_header, row_data):
    """Identify traits of user call."""
    user_id = row_data.pop(user_id_header)
    logger.info("Identify API Call for user: {}".format(user_id))
    client.identify(user_id, row_data)
    row_data[user_id_header] = user_id

def segment_api_call(segment_write_key, user_id_header, csv_output):
    """Make segment api calls for each row of csv data."""
    logger.info("Instantiating new client with write_key: {}".format(segment_write_key))
    segment_client = analytics.Client(write_key=segment_write_key, debug=True, on_error=on_error, send=True, max_queue_size=100000)

    # Create datetime object.
    now_utc = datetime.datetime.now()
    now_pacific_tz = now_utc.replace(tzinfo=timezone("US/Pacific"))

    logger.info("Initiating batch of api calls...")
    for row_data in csv_output:
        identify_api_call(segment_client, user_id_header, row_data)
        event_api_call(segment_client, row_data[user_id_header], now_pacific_tz)

    logger.info("Flush is being attempted...")
    segment_client.flush()
    logger.info("API batch complete!")
    return True
