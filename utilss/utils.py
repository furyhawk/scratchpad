import os.path
from pathlib import Path
from collections import OrderedDict
from functools import wraps

import csv
import json
import compress_json

from .configuration import settings
from .logger import logging

ASSETS_DIR = settings.assets_dir
SERVER = settings.server


def trace(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        print(f'{func.__name__}({args!r}, {kwargs!r}) -> {result!r}')
        return result
    return wrapper


def to_str(bytes_or_str):
    if isinstance(bytes_or_str, bytes):
        value = bytes_or_str.decode('utf-8')
    else:
        value = bytes_or_str
    return value


def read_csv(data_path):
    with open(data_path, mode='r') as csv_file:
        csv_reader = csv.reader(csv_file)

        data_list = []
        line_count = 0
        for row in csv_reader:
            line_count += 1
            data_list.append(row)
        print(f'Processed {line_count} lines.')
    return data_list


def read_json(fname):
    fname = Path(fname)
    with fname.open('rt') as handle:
        return json.load(handle, object_hook=OrderedDict)


def write_json(content, fname):
    fname = Path(fname)
    with fname.open('wt') as handle:
        json.dump(content, handle, indent=4, sort_keys=False)


def get_data_filename(filename='json_data'):
    return os.path.join(ASSETS_DIR, filename+".json.gz")


def write_asset_json(data, filename='json_data', update=False):
    json_asset = get_data_filename(filename)
    try:
        if update:  # Extend json file on update mode
            old_data = read_asset_json(filename)
            data.extend(old_data)

        compress_json.dump(data, json_asset)

    except FileNotFoundError:
        logging.warning(f"{filename} not found.")


def read_asset_json(filename='json_data'):
    json_asset = get_data_filename(filename)
    try:
        return compress_json.load(json_asset)
    except Exception as e:
        logging.error(e)
        return []


def load_matches(df, server=SERVER):
    matches_asset = []
    for _, summoner in df.iterrows():
        match_asset = read_asset_json(
            filename='matches_detail' + '_' + server + '_'+summoner['name'])
        if match_asset:
            matches_asset.extend(match_asset)

    return matches_asset


def read_collection_db(collection, select={}):
    try:
        return collection.find({}, select)
    except Exception as e:
        logging.error(e)
        return []


def load_matches_db(collection, select={}):
    matches_asset = []
    match_asset = read_collection_db(collection=collection, select=select)
    if match_asset:
        matches_asset.extend(match_asset)

    return matches_asset


def find_collection_db(collection, key, value, select={}):
    ''' { "info.participants.puuid": value, 'game_version': {'$regex': LATEST_RELEASE} } '''
    try:
        return list(collection.find({key: value}, select))
    except Exception as e:
        logging.error(e)
        return []


def find_matches_db(collection, puuid, select={}):
    matches_asset = []
    match_asset = find_collection_db(
        collection, 'info.participants.puuid', puuid, select)
    if match_asset:
        matches_asset.extend(match_asset)

    return matches_asset


def load_league_matches_db(collection, summoners_df, select={}):
    matches_asset = []
    for _, summoner in summoners_df.iterrows():
        match_asset = find_matches_db(collection, summoner['puuid'], select)

        if match_asset:
            matches_asset.extend(match_asset)

    return matches_asset


def write_collection_db(data, collection, update=False):
    try:
        if update:  # Extend collection on update mode
            old_data = read_collection_db(collection)
            data.extend(old_data)

        collection.drop()
        collection.insert_many(data, ordered=False)
    except Exception as e:
        logging.error(e)


def insert_collection_db(data, collection):
    try:
        collection.insert_many(data, ordered=False)
    except Exception as e:
        logging.error(e)


def load_summoners(df, server=SERVER):
    matches_asset = []
    for _, summoner in df.iterrows():
        match_asset = read_asset_json(
            filename='matches_detail' + '_' + server + '_'+summoner['name'])
        if match_asset != None:
            matches_asset.extend(match_asset)

    return matches_asset
