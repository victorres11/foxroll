import analytics


# SEGMENT_WRITE_KEY = "TRHR0eTFmnb6cdNcQD2GeTW6ds5k6MMO"
# analytics.write_key = SEGMENT_WRITE_KEY
analytics.debug = True

def on_error(error, items):
    print("An error occurred:", error)

analytics.on_error = on_error

def dummy_call():
    analytics.identify('019mr8mf4r', {
    'email': 'john@example.com',
    'name': 'John Smith',
    'friends': 30
})


# [{'action': 'identify',
#   'anonymousId': '7D897FDB-7DCE-4B76-AB6A-177F11441901',
#   'timestamp': '2016-06-22T00:00:00.000Z',
#   'traits.email': 'c.silveri@e-motion.tv+',
#   'traits.first_name': 'Corrado',
#   'traits.joined_via': 'organic',
#   'traits.last_name': 'Silveri',
#   'userId': '1ac44fe1-183d-4219-9f13-d9ebecd0bfef'},

def segment_api_call(segment_write_key, csv_output):
    print "Segment write key = {}".format(segment_write_key)
    analytics.write_key = segment_write_key
    # import ipdb; ipdb.set_trace()

    for call_data in csv_output:
        # call_api
        analytics.identify(call_data['userId'], {
        'email': call_data['traits.email'],
        'first_name': call_data['traits.first_name'],
        'last_name': call_data['traits.last_name'],
        'joined_via': call_data['traits.joined_via']
    })
