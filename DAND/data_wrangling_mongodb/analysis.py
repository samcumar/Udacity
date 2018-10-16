#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import re
import pprint
from collections import defaultdict

"""
This program just analyses the data that has been imported into the Sydney collection of the MongoDB database OSM.
This program analyses the following components of the address field:
* address.postcode
* address.streetname
* address.suburb
* address.city
"""

# A list of postcode regular expressions to deal with the different scenarios of data found in the address.postcode field
postcode_re = re.compile(r"^\D+\s+|\s+\D+$", re.IGNORECASE)
postcode2_re = re.compile(r"^\D+|\D+$", re.IGNORECASE)
postcode_dig_re = re.compile(r"\d+", re.IGNORECASE)
postcode_gd_re = re.compile(r"^\d{4}$", re.IGNORECASE)
postcode_let_re = re.compile(r"^(\s*[a-zA-Z]+\s*)+$", re.IGNORECASE)

# Regular expression for extracting street types from the address.street field
street_type_re = re.compile(r'\S+\.?$', re.IGNORECASE)

# regular expression for dealing with the address.city and address.suburb fields
sydney_re = re.compile(r"(sydney)", re.IGNORECASE)
ne_sydney_re = re.compile(r"^((?!sydney).)*$", re.IGNORECASE)

# A list of valid street types
valid_type = ['Arcade','Esplanade','Close','Court','Place','East','Promenade','Place','Circuit','Boulevard','Road', 'Parade','Esplanade','Close', 'Avenue',
                'Highway','Crescent','Drive', 'Freeway','Boulevarde', 'Lane', 'Street', 'Terrace','Way']

# A dictionary mapping of abbreviated street types to their appropriate names.
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
#    client = MongoClient("mongodb://udacity:data_wrangler@cluster0-shard-00-00-v2n7o.mongodb.net:27017,cluster0-shard-00-01-v2n7o.mongodb.net:27017,cluster0-shard-00-02-v2n7o.mongodb.net:27017/admin?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin")
    client = MongoClient("mongodb://redhatsrv:27017")
    db = client.OSM
    return db

# This section is all the mongoDB queries for extracting postcode, street name, suburb and city information from the collection
def postcode_query01(postcode_regex):
    pipeline = [{"$match": {"address":{"$exists": "true"},"address.postcode": {"$regex": postcode_regex}}},
                {"$group": {"_id": {"postcode": "$address.postcode"}, "count":{"$sum": 1}}},
                {"$sort": {"postcode": 1}}
                ]
    return pipeline

def street_query():
    pipeline = [{"$match": {"address.street": {"$exists": "true"}}},
                {"$project": {"_id": 0, "street_type": "$address.street"}}]


    return pipeline

def city_query01():
    pipeline = [{"$match":{"$and": [{"address.city": "Sydney"}, {"address.suburb":{"$exists": True}}]}},
                {"$group": {"_id": {"city": "$address.city", "suburb": "$address.suburb", "postcode": "$address.postcode"}, "count": {"$sum": 1}}},
                {"$sort": {"suburb": 1}}
                ]

    return pipeline

def city_query02():
    pipeline = [{"$match":{"$and": [{"address.city": {"$regex": sydney_re}}, {"address.postcode": {"$exists": True}}, {"address.suburb":{"$exists": False}}]}},
                {"$group": {"_id": {"city": "$address.city", "suburb": "$address.suburb", "postcode": "$address.postcode"}, "count": {"$sum": 1}}},
                {"$sort": {"suburb": 1}}
                ]

    return pipeline


def city_query04():
    pipeline = [{"$match":{"$and": [{"address.city": {"$exists": False}}, {"address.suburb":{"$exists": True}}]}},
                {"$group": {"_id": {"city": "$address.city", "suburb": "$address.suburb", "postcode": "$address.postcode"}, "count": {"$sum": 1}}},
                {"$sort": {"suburb": 1}}
                ]

    return pipeline

def city_query03():
    pipeline = [{"$match": {"$and": [{"address.city": {"$regex": ne_sydney_re}}, {"address.suburb": {"$exists": False}}]}},
                {"$group": {"_id": {"city": "$address.city", "suburb": "$address.suburb", "postcode": "$address.postcode"}, "count": {"$sum": 1}}},
                {"$sort": {"suburb": 1}}
                ]

    return pipeline

def city_query05():
    pipeline = [{"$match":{"$and": [{"address.suburb": {"$exists": True}}, {"address.city": {"$regex": ne_sydney_re}}]}},
                {"$group": {"_id": {"city": "$address.city", "suburb": "$address.suburb", "postcode": "$address.postcode"}, "count": {"$sum": 1}}},
                {"$sort": {"suburb": 1}}
                ]

    return pipeline


# The functions below analyse the postcode information.
def postcode_print(postcode_regex):
    pc_query = postcode_query01(postcode_regex)
    total_count = 0
    for doc in db.sydney.aggregate(pc_query):
        if doc["_id"]["postcode"] is None:
            continue
        elif (postcode_let_re.search(doc["_id"]["postcode"])):
            continue
        elif (int(postcode_dig_re.search(doc["_id"]["postcode"]).group()) >= 2000) and (int(postcode_dig_re.search(doc["_id"]["postcode"]).group()) <= 2999):
            print "Postcode: '{0}' - Record Count: {1}".format(doc["_id"]["postcode"], doc["count"])
            total_count = total_count + int(doc["count"])
    print "Total record count: {0}".format(total_count)

def postcode_review(postcode_regex):
    pc_query = postcode_query01(postcode_regex)
    for doc in db.sydney.aggregate(pc_query):
        if doc["_id"]["postcode"] is None:
            continue
        elif (postcode_let_re.search(doc["_id"]["postcode"])):
            print "Postcode: '{0}' - Record Count: {1}".format(doc["_id"]["postcode"], doc["count"])
        elif (int(postcode_dig_re.search(doc["_id"]["postcode"]).group()) < 2000) or (int(postcode_dig_re.search(doc["_id"]["postcode"]).group()) > 2999):
            print "Postcode: '{0}' - Record Count: {1}".format(doc["_id"]["postcode"], doc["count"])

def postcode_analyse(db):
    print "Total number of records in Sydney collection:", db.sydney.count()

    postcode_rec = db.sydney.find({"address.postcode": {"$exists": "true"}})

    print "Total Number of records that have a postcode field:", postcode_rec.count()
    print "\n"

    print "Scenario 01: Following are counts of records with valid NSW postcodes:"
    postcode_print(postcode_gd_re)
    print "\n"

    print "Scenario 02: Following are record counts of postcodes mixed with alphanumeric characters:"
    postcode_print(postcode_re)
    print "\n"

    print "Scenario 03: Following are record counts of postcodes which aren't valid and therefore require a review of the address field:"
    postcode_review(postcode_dig_re)
    postcode_review(postcode_let_re)

# Functions below analyse the street types
def build_streettype(db, pipeline):
    street_typeid = defaultdict(list)
    street_type = {}
    count = 0
    for doc in db.sydney.aggregate(pipeline):
        m = street_type_re.search(doc["street_type"]).group()
        count +=1
        if m not in street_type:
            street_type[m] = 1
        else:
            street_type[m] += 1

    return street_type, count

def street_analyse(db):
    street_type_clause = street_query()
    street_rec, rec_count = build_streettype(db, street_type_clause)

    good_street_type = {}
    review_street_type = {}
    fixable_street_type = {}

    for t in street_rec:
        if t in valid_type:
            good_street_type[t] = street_rec[t]
        elif t in type_fix:
            fixable_street_type[t] = street_rec[t]
        else:
            review_street_type[t] = street_rec[t]

    print "Total number of records in Sydney collection:", db.sydney.count()
    print "Records with a street address: {0}".format(rec_count)

    print "Street Types that are considered complete in the database:"
    pprint.pprint(good_street_type)
    print "\n"

    print "Street types that are abbreviated and can be fixed:"
    pprint.pprint(fixable_street_type)
    print "\n"

    print "Street types that aren't valid at all and requires a review of the address field:"
    pprint.pprint(review_street_type)
    print "\n"

def suburb_print(db, query):
    count = 0
    for doc in db.sydney.aggregate(query):
        count = count + doc["count"]
        print doc

    print "Total Record count: {0}".format(count)
    print "\n"

# Functions below analyse both suburb and city data
def suburb_city_analyse(db):
    scenario01 = city_query01()
    scenario02 = city_query02()
    scenario03 = city_query03()
    scenario04 = city_query04()
    scenario05 = city_query05()

    print "****Total number of records in Sydney collection:", db.sydney.count()

    print "**** Scenario 01: Has city value of 'Sydney' and a value for suburb ********"
    suburb_print(db, scenario01)

    print "**** Scenario 02: Has Sydney as part of the value of city and has a postcode but no suburb ********"
    suburb_print(db, scenario02)

    print "****** Scenario 03: Has city whose value is not 'Sydney' and suburb field does not exist ******"
    suburb_print(db, scenario03)

    print "****** Scenario 04: The city field doesn't exist and holds a value for the suburb ******"
    suburb_print(db, scenario04)

    print "****** Scenario 05: The value of the field city doesn't contain the value of 'Sydney' and has a value for the suburb field ******"
    suburb_print(db, scenario05)

# Function below executes the analysis program
if __name__ == "__main__":
    db = get_db()
    while True:
        print "What type of address field data would you like to analyse:"
        print "1: Analyse Postcodes"
        print "2: Analyse Street Types"
        print "3: Analyse Suburb and City data"
        print "0: Exit this program"
        analyse = int(raw_input("Enter 1, 2, 3 or 0(Exit Program):"))
        if analyse == 1:
            postcode_analyse(db)
        elif analyse == 2:
            street_analyse(db)
        elif analyse == 3:
            suburb_city_analyse(db)
        elif analyse == 0:
            print "Exiting Program"
            exit()
        else:
            print "You pressed the wrong key!"
