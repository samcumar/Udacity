#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import re
import pprint
from collections import defaultdict

"""
This program fixes both the data in the city and suburb fields that exist in the collection. As part of the process, it fixes any postcode issues that are left over 
from running the fix_postcode.py program but not all.
"""

sydney_re = re.compile(r"(sydney)", re.IGNORECASE)
ne_sydney_re = re.compile(r"^((?!sydney).)*$", re.IGNORECASE)

def get_db():
    from pymongo import MongoClient
    client = MongoClient("mongodb://udacity:data_wrangler@cluster0-shard-00-00-v2n7o.mongodb.net:27017,cluster0-shard-00-01-v2n7o.mongodb.net:27017,cluster0-shard-00-02-v2n7o.mongodb.net:27017/admin?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin")
#    client = MongoClient("mongodb://redhatsrv:27017")
    db = client.OSM
    return db


def city_query01():
    pipeline = [{"$match":{"$and": [{"address.city": "Sydney"}, {"address.suburb":{"$exists": True}}]}},
                {"$group": {"_id": {"city": "$address.city", "suburb": "$address.suburb", "postcode": "$address.postcode"}, "count": {"$sum": 1}, "id_list": {"$push": "$id"}}},
                {"$sort": {"suburb": 1}}
                ]

    return pipeline

def city_query03():
    pipeline = [{"$match": {"$and": [{"address.city": {"$regex": ne_sydney_re}}, {"address.suburb": {"$exists": False}}]}},
                {"$group": {"_id": {"city": "$address.city", "suburb": "$address.suburb", "postcode": "$address.postcode"}, "count": {"$sum": 1}, "id_list": {"$push": "$id"}}},
                {"$sort": {"suburb": 1}}
                ]

    return pipeline

def fix_scenario01(db, pipeline):
    print "**** Scenario 01: Has city value of 'Sydney' and a value for suburb ********"
    print "Fixing Records now ....."
    
    for doc in db.sydney.aggregate(pipeline):
        suburb = doc["_id"]["suburb"]
        sb, pc = find_postcode(db, suburb)
        if ((sb is None) and (pc is None)):
            result = db.sydney.update_many({"$and": [{"address.city": "Sydney"}, {"address.suburb": suburb}]}, {"$push": {"to_review": "address_city_suburb"}})
            print "Scenario 01: {0} is an invalid suburb - ids to be reviewed: {1}".format(suburb, doc["id_list"])
        else:
            result = db.sydney.update_many({"$and": [{"address.city": "Sydney"}, {"address.suburb": suburb}]}, {"$set": {"address.suburb": sb, "address.postcode": pc}})
            print "Scenario 01: {1} records have been updated for the suburb {0} and city of Sydney".format(suburb, result.modified_count)
    
    print "\n"


def fix_scenario03(db, pipeline):
    print "****** Scenario 03: Has city whose value is not 'Sydney' and suburb field does not exist ******"
    print "Fixing Records now ....."

    for doc in db.sydney.aggregate(pipeline):
        city = doc["_id"]["city"]
        sb, pc = find_postcode(db, city)
    
        if ((sb is None) and (pc is None)):
            result = db.sydney.update_many({"$and": [{"address.city": city}, {"address.suburb": {"$exists": False}}]}, {"$push": {"to_review": "address_city_suburb"}})
            print "Scenario 03: {0} is an invalid name for a suburb - ids to be reviewed: {1}".format(city, doc["id_list"])
        else:
            result = db.sydney.update_many({"$and": [{"address.city": city}, {"address.suburb": {"$exists": False}}]}, {"$set": {"address.city": "Sydney", "address.suburb": sb, "address.postcode": pc}})
            print "Scenario 03: {1} records have been updated for the suburb {0} and city of Sydney".format(sb, result.modified_count)
    
    print "\n"

def fix_scenario04(db):
    print "****** Scenario 04: The city field doesn't exist and holds a value for the suburb ******"
    print "Fixing Records now ....."
    
    result = db.sydney.update_many({"$and": [{"address.city": {"$exists": False}}, {"address.suburb":{"$exists": True}}]}, {"$set": {"address.city": "Sydney"}})
    
    print "Scenario 04: {0} records have been updated with the value of Sydney for the city field".format(result.modified_count)
    print "\n"


def find_postcode(db, suburb):
    postcode_rec = db.postcodes.find_one({"$and": [{"suburb": re.compile(suburb, re.IGNORECASE)}, {"postcode": {"$gte": "2000"}}, {"postcode": {"$lte": "2999"}}]})
    if postcode_rec is None:
        return None, None
    else:
        return postcode_rec["suburb"], postcode_rec["postcode"]

def find_suburb(db, postcode):
    postcode_rec = db.postcodes.find_one({"postcode": postcode})
    return postcode_rec["suburb"], postcode_rec["postcode"]

if __name__ == "__main__":
    db = get_db()
    fix_scenario04(db)
    query01 = city_query01()
    query03 = city_query03()
    fix_scenario01(db, query01)
    fix_scenario03(db, query03)
