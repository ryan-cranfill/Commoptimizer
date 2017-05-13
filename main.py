import click
import os
import pathlib
import pytz
import logging
import pickle
from datetime import datetime

from commoptimizer.scraper.api import get_trains
from commoptimizer.settings import get_cta_api_key

CTA_API_KEY = get_cta_api_key()

DATA_DIR = os.path.expanduser('~/commoptimizer_data')
DATA_PATH = pathlib.Path(DATA_DIR).absolute()

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def make_data_dir_if_not_exists(data_path):
    if not data_path.is_dir():
        logger.log(logging.WARN, f'Making data directory: {data_path}')
        data_path.mkdir()


# TODO: Add train line name to pickle name
def make_today_file_path():
    today = datetime.today().astimezone(pytz.timezone('US/Central'))
    today_path = f"commopt_{today.strftime('%y_%m_%d')}.pkl"

    return today_path


def make_now():
    now = datetime.now(tz=pytz.timezone('US/Central'))

    return now, now.strftime('%H:%M:%S')


def write_pickle_if_not_exists(pickle_path, data_dict):
    if pickle_path.exists():
        logger.log(logging.INFO, f'Appending to current pickle: {str(pickle_path)}')
        with open(str(pickle_path), 'rb') as f:
            current_data = pickle.load(f)

        all_data = current_data + [data_dict]
        with open(str(pickle_path), 'wb') as f:
            pickle.dump(all_data, f, pickle.HIGHEST_PROTOCOL)
        logger.log(logging.INFO, f'Data appended')

    else:
        logger.log(logging.INFO, f'Creating new pickle: {str(pickle_path)}')

        with open(str(pickle_path), 'wb') as f:
            pickle.dump([data_dict], f, pickle.HIGHEST_PROTOCOL)
        logger.log(logging.INFO, f'Data written')


@click.command()
def run():
    """Scrape the train tracker and append the data into today's pickle"""
    make_data_dir_if_not_exists(DATA_PATH)
    trains, all_train_stops = get_trains(CTA_API_KEY)
    now, now_string = make_now()
    data_dict = {
        'trains': trains,
        'stops': all_train_stops,
        'time': now_string,
        'datetime': now
    }

    today_string = make_today_file_path()
    pickle_path = DATA_PATH / today_string

    write_pickle_if_not_exists(pickle_path, data_dict)


if __name__ == '__main__':
    run()

