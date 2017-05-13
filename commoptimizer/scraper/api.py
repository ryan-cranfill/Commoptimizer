import requests
import json
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

LOCATION_ENDPOINT = 'http://lapi.transitchicago.com/api/1.0/ttpositions.aspx'
FOLLOW_ENDPOINT = 'http://lapi.transitchicago.com/api/1.0/ttfollow.aspx'


class TrainAPI(object):
    """Helper object to make querying the CTA API nicer"""
    def __init__(self, api_key):
        self.api_key = api_key

    def get_train_locations(self, line='brn'):
        """Get all trains along a line"""
        # TODO: Build in retry/error handling logic
        return requests.get(LOCATION_ENDPOINT, params={'key': self.api_key,
                                                       'rt': line,
                                                       'outputType': 'JSON'})

    def get_follow_train(self, run_number):
        """Get estimated arrival times for a given train number"""
        # TODO: Build in retry/error handling logic
        return requests.get(FOLLOW_ENDPOINT, params={'key': self.api_key,
                                                     'runnumber': run_number,
                                                     'outputType': 'JSON'})


class Train(object):
    # TODO: Update this with all the actual properties
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def get_trains(api_key, line='brn'):
    """Ping the CTA API and get info on all trains for a given line"""
    train_api = TrainAPI(api_key)
    logger.log(logging.INFO, 'Getting train info...')
    response = train_api.get_train_locations(line=line)
    content = json.loads(response.content)
    trains = content.get('ctatt', {}).get('route', {})[0].get('train')

    all_train_stops = {}

    if trains:
        for train_dict in trains[-1:]:
            train = Train(**train_dict)

            response = train_api.get_follow_train(train.rn)
            content = json.loads(response.content)
            # TODO: Check for errors
            stops = content.get('ctatt', {}).get('eta')
            if stops:
                all_train_stops[train.rn] = stops
            else:
                logger.log(logging.ERROR, 'could not get stops, lol')
                raise ValueError
    else:
        logger.log(logging.ERROR, 'could not get trains, lol')
        raise ValueError

    logger.log(logging.INFO, 'Train data successfully got')
    return trains, all_train_stops
