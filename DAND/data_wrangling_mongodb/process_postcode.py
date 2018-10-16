#!/usr/bin/env python
# -*- coding: utf-8 -*-
import pprint
import codecs
import json
import csv
from collections import defaultdict

"""
This file converts the CSV file for postcodes into a JSON format that can be imported into the postcodes collection.
"""

#Function below reads in the CSV file
def csv_reader(file_in):
    data = []
    with open(file_in, "rb") as f:
        reader = csv.DictReader(f)
        for line in reader:
            data.append(line)

    return data

#Using the CSV file, the function below creates the JSON formatted file
def json_create(data, file_name = "postcode"):
    # You do not need to change this file
    file_out = "{0}.json".format(file_name)
    with codecs.open(file_out, "w", "utf-8") as fo:
        for rec in data:
            if rec:
                fo.write(json.dumps(rec, ensure_ascii=False) + "\n")
    return data

if __name__ == "__main__":
    postcode_data = csv_reader("AUS.csv")
    json_create(postcode_data)
