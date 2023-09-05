import collections
import pickle

import mysql.connector
from absl import app
from absl import flags
from absl import logging
import configparser

from pv.disambiguation.core import AssigneeMention, AssigneeNameMention
import pv.disambiguation.util.db as pvdb

import os

def build_granted(config):
    # | uuid | patent_id | assignee_id | rawlocation_id | type | name_first | name_last | organization | sequence |
    cnx = pvdb.granted_table(config)
    cursor = cnx.cursor()
    query = 'SELECT {cols} FROM {table}'.format(
        cols=config['ETC']['sql_cols'], 
        table=config['ETC']['table']
    )
    cursor.execute(query)

    tot_cols = [i.strip() for i in config['ETC']['sql_cols'].split(',')]
    location_cols = None
    if 'locations'in config['ETC']:
        location_cols = [i.strip() for i in config['ETC']['locations'].split(',')]
        loc2tot_indices = [tot_cols.index(i) for i in location_cols]
    # 'uuid, patent_id, orgname, city_name, state_name, country_code, postal_code, address'
    disambiguated_index = tot_cols.index(config['ETC']['disambiguated_col'])
    feature_map = collections.defaultdict(list)

    for idx, rec in enumerate(cursor):
        uuid, patent_id = rec[0], rec[1]
        orgname = rec[disambiguated_index]
        location = [rec[ind] for ind in loc2tot_indices]
        am = AssigneeMention(uuid, patent_id, None, None, None, None, orgname, '0', location_id=location)
        feature_map[am.name_features()[0]].append(am)
        logging.log_every_n(logging.INFO, 'Processed %s granted records - %s features', 10000, idx, len(feature_map))
    return feature_map


def main(argv):
    logging.info('Building assignee mentions')

    config = configparser.ConfigParser()
    config.read(['config/database_config.ini', 'config/database_tables.ini',
                 'config/consolidated_config_adhoc.ini'])
    feats = build_granted(config)
    logging.info('finished loading mentions %s', len(feats))
    # name_mentions = set(feats[0].keys()).union(set(feats[1].keys()))
    name_mentions = set(feats[0].keys())
    logging.info('number of name mentions %s', len(name_mentions))
    from tqdm import tqdm
    records = dict()
    from collections import defaultdict
    canopies = defaultdict(set)
    for nm in tqdm(name_mentions, 'name_mentions'):
        anm = AssigneeNameMention.from_assignee_mentions(nm, feats[nm])
        for c in anm.canopies:
            canopies[c].add(anm.uuid)
        records[anm.uuid] = anm
    os.makedirs(config['BASE_PATH']['assignee'])
    with open(config['BASE_PATH']['assignee'] + 'assignee.%s.pkl' % 'records', 'wb') as fout:
        pickle.dump(records, fout)
    with open(config['BASE_PATH']['assignee'] + 'assignee.%s.pkl' % 'canopies', 'wb') as fout:
        pickle.dump(canopies, fout)


if __name__ == "__main__":
    app.run(main)
