#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import re
import pprint
from collections import defaultdict
import sys
import codecs

"""
This program fixes the street types that exist in the collection. 
"""

# Regular expression to extract the street types
street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE)

# List of valid Street types
valid_type = ['Arcade','Esplanade','Close', 'Court', 'Place','East','Promenade','Place','Circuit','Boulevard','Road', 'Parade','Esplanade','Close', 'Avenue',
                'Highway','Crescent','Drive', 'Freeway','Boulevarde', 'Lane', 'Street', 'Terrace','Way', 'West']

# Dictionary mapping of abbreviated street types to their correct format
type_fix = {'Rd': 'Road',
            'street': 'Street',
            'Pl': 'Place',
            'Promanade': 'Promenade',
            'Ave': 'Avenue',
            'Roads': 'Road',
            'St.': 'Street',
            'Street)': 'Street',
            'St': 'Street',
            'Streets': 'Street',
            'Streett': 'Street',
            'Bouvelard': 'Boulevarde',
            'st': 'Street',
            'Av': 'Avenue'}


def get_db():
    from pymongo import MongoClient
    client = MongoClient("mongodb://udacity:data_wrangler@cluster0-shard-00-00-v2n7o.mongodb.net:27017,cluster0-shard-00-01-v2n7o.mongodb.net:27017,cluster0-shard-00-02-v2n7o.mongodb.net:27017/admin?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin")
#    client = MongoClient("mongodb://redhatsrv:27017")
    db = client.OSM
    return db

# MongoDB query
def street_query():
    pipeline = [{"$match": {"address.street": {"$exists": "true"}}},
                {"$project": {"_id": 0, "street_type": "$address.street", "id": 1}}]

    return pipeline

# Fixing street types
def fix_street(db, id_data, st):
    st_type = type_fix[st]

    for i in id_data:
        docs = db.sydney.find({"id": i})
        for d in docs:
            street_name = d["address"]["street"]
            fixed_st = street_type_re.sub(st_type, street_name)
            db.sydney.update_many({"id": i}, {"$set": {"address.street": fixed_st}})

# updates records identified as being hard to fix programmatically "assembly": {"$in": ["Germany", "United Kingdom", "Japan"]}
def review_update(db, id_data):
#    for id in id_data:
     db.sydney.update_many({"id": {"$in": id_data}}, {"$push": {"to_review": "address_street"}})

def street_id(db, pipeline):
    street_type_id = defaultdict(list)
    street_type = {}
    for doc in db.sydney.aggregate(pipeline):
        m = street_type_re.search(doc["street_type"]).group()
        street_type_id[m].append(doc["id"])

    return street_type_id

# Function below is to process through all street names and fix those which can be fixed and flag those that need to be reviewed.
def process_doc(db, pipeline):
    street_rec = street_id(db, pipeline)

    for t in street_rec:
        if t in valid_type:
            continue
        elif t in type_fix:
            ids = street_rec[t]
            fix_street(db, ids, t)
            print "Street Type {0} changed to {1} - Records updated: {2}".format(t, type_fix[t], len(ids))
        else:
            id_toreview = street_rec[t]
            review_update(db, id_toreview)
            print "Street type " + t + " is incomplete and needs to be reviewed - ids to be reviewed:", id_toreview

if __name__ == "__main__":
    db = get_db()
    st_type_query = street_query()
    data = process_doc(db, st_type_query)
