import analytics
import logging

logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def on_error(error, items):
    print("An error occurred:", error)

analytics.on_error = on_error
analytics.debug = True

# [{'action': 'identify',
#   'anonymousId': '7D897FDB-7DCE-4B76-AB6A-177F11441901',
#   'timestamp': '2016-06-22T00:00:00.000Z',
#   'traits.email': 'c.silveri@e-motion.tv+',
#   'traits.first_name': 'Corrado',
#   'traits.joined_via': 'organic',
#   'traits.last_name': 'Silveri',
#   'userId': '1ac44fe1-183d-4219-9f13-d9ebecd0bfef'},

def segment_api_call(segment_write_key, csv_output):
    logger.info("Instantiating new client with write_key: {}".format(segment_write_key))
    segment_client = analytics.Client(segment_write_key, debug=True, on_error=on_error, send=True, max_queue_size=100000)

    for call_data in csv_output:
        # call_api
        logger.info("Initiating batch...")
        segment_client.identify(call_data['userId'], {
        'email': call_data['traits.email'],
        'first_name': call_data['traits.first_name'],
        'last_name': call_data['traits.last_name'],
        'joined_via': call_data['traits.joined_via']
    })
