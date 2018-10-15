#!/usr/bin/env python
# -*- coding: utf-8 -*-

import io
import re
import pprint

"""
This program fixes the majority of the postcode data if not all. 
"""

# Regular expressions to identify the different types of data in the postcodes field
postcode_re = re.compile(r"^\D+\s+|\s+\D+$", re.IGNORECASE)
postcode2_re = re.compile(r"^\D+|\D+$", re.IGNORECASE)
postcode_digit = re.compile(r"\d+", re.IGNORECASE)
postcode_letters = re.compile(r"^(\s*[a-zA-Z]+\s*)+$", re.IGNORECASE)

def get_db():
    from pymongo import MongoClient
    client = MongoClient("mongodb://udacity:data_wrangler@cluster0-shard-00-00-v2n7o.mongodb.net:27017,cluster0-shard-00-01-v2n7o.mongodb.net:27017,cluster0-shard-00-02-v2n7o.mongodb.net:27017/admin?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin")
#    client = MongoClient("mongodb://redhatsrv:27017")
    db = client.OSM
    return db

# MongoDB query to find all the postcodes in the collection
def postcode_query():
    pipeline = [{"$match": {"address.postcode":{"$exists": True}}},
                {"$group": {"_id": {"postcode": "$address.postcode"}, "count":{"$sum": 1}, "id_list": {"$push": "$id"}}},
                {"$sort": {"postcode": 1}}]
    return pipeline

# Function that processes the postcode field
def process_doc(db, pipeline):
    for doc in db.sydney.aggregate(pipeline):
        if doc["_id"]["postcode"] is None:
            continue
        elif (postcode_letters.search(doc["_id"]["postcode"])):
            pc = doc["_id"]["postcode"]
            result = db.sydney.update_many({"address.postcode": pc}, {"$push": {"to_review": "address_postcode"}})
            print "Postcode: {0} - Invalid postcode as it is just characters. ids to be reviewed: {1}".format(pc, doc["id_list"])
        elif (int(postcode_digit.search(doc["_id"]["postcode"]).group()) < 2000) or (int(postcode_digit.search(doc["_id"]["postcode"]).group()) > 2999):
            # This is to capture any postcodes that weren't in the correct range
            pc = doc["_id"]["postcode"]
            result = db.sydney.update_many({"address.postcode": pc}, {"$push": {"to_review": "address_postcode"}})
            print "Postcode: {0} - Invalid postcode as it is in the wrong range of postcodes. Records to be reviewed: {1}".format(pc, doc["id_list"])
        elif postcode_re.search(doc["_id"]["postcode"]):
            pc_orig = doc["_id"]["postcode"]
            pc = postcode_re.sub("", pc_orig).strip()
            result = db.sydney.update_many({"address.postcode": pc_orig}, {"$set": {"address.postcode": pc}})
            print "Postcode: {0} has been modified to {1} - Records updated: {2}".format(pc_orig, pc, result.modified_count)

if __name__ == "__main__":
    db = get_db()
    postcode_pipeline = postcode_query()
    process_doc(db, postcode_pipeline)
