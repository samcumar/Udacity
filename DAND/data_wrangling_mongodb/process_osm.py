#!/usr/bin/env python
# -*- coding: utf-8 -*-
import xml.etree.cElementTree as ET
import pprint
import re
import codecs
import json
from collections import defaultdict
"""
The aim of this program is to convert the OSM xml file into each record of a format
like below:

{
"id": "2406124091",
"type: "node",
"visible":"true",
"created": {
          "version":"2",
          "changeset":"17206049",
          "timestamp":"2013-08-03T16:43:42Z",
          "user":"linuxUser16",
          "uid":"1219059"
        },
"pos": [41.9757030, -87.6921867],
"address": {
          "housenumber": "5157",
          "postcode": "60625",
          "street": "North Lincoln Ave"
        },
"amenity": "restaurant",
"cuisine": "mexican",
"name": "La Cabana De Don Luis",
"phone": "1 (773)-271-5176"
}

"""


lower = re.compile(r'^([a-z]|_)*$')
lower_colon = re.compile(r'^([a-z]|_)*:([a-z]|_)*$')
problemchars = re.compile(r'[=\+/&<>;\'"\?%#$@\,\. \t\r\n]')
last_word = re.compile(r'([a-z]|_)+$')
first_word = re.compile(r'^([a-z]|_)*')

CREATED = [ "version", "changeset", "timestamp", "user", "uid"]

#Function below is to process each element under the way, node and relation tags
def shape_element(element):
    #Picked up the node defaultdict idea from this URL https://stackoverflow.com/questions/33080869/python-how-to-create-a-dict-of-dict-of-list-with-defaultdict.
    node = defaultdict(defaultdict(list).copy)
    created = {}
    address = {}
    node_refs = []
    members = []
    lower_list = set()

    node["tag_type"] = element.tag
    for a in ["id", "visible"]:
        try:
            node[a] = element.attrib[a]
        except KeyError:
            node[a] = None

    for i in CREATED:
        created[i] = element.attrib[i]
    node["created"] = created
    if element.tag == "node":
        try:
            pos = [float(element.attrib["lat"]), float(element.attrib["lon"])]
        except ValueError:
            pos = None
        node["pos"] = pos
    elif element.tag == "way":
        node_refs = []
        for nd in element.iter("nd"):
            node_refs.append(nd.attrib["ref"])
        node["node_refs"] = node_refs
    else:
        members = []
        for member in element.iter("member"):
            members.append(member.attrib)
        node["member"] = members
    lower_list = lower_tags(element)

    for tag in element.iter("tag"):
        if (lower.search(tag.attrib["k"])):
            node[lower.search(tag.attrib["k"]).group()] = tag.attrib["v"]
        elif (first_word.search(tag.attrib["k"]).group() == "addr") and (lower_colon.search(tag.attrib["k"])):
            address[last_word.search(tag.attrib["k"]).group()] = tag.attrib["v"]
            node["address"] = address
        elif (lower_colon.search(tag.attrib["k"])):
            if (first_word.search(tag.attrib["k"]).group() in lower_list):
                node_key = first_word.search(tag.attrib["k"]).group() + "-details"
                node[node_key][last_word.search(tag.attrib["k"]).group()] = tag.attrib["v"]
            else:
                node_key = first_word.search(tag.attrib["k"]).group()
                node[node_key][last_word.search(tag.attrib["k"]).group()] = tag.attrib["v"]


    return node

def lower_tags(elem):
    lower_set = set()

    for tag in elem.iter("tag"):
        if lower.search(tag.attrib["k"]):
            lower_set.add(lower.search(tag.attrib["k"]).group())

    return lower_set


# The function below has been taken from previous Udacity exercises in order to process large XML files
def get_element(osm_file, tags=('node', 'way', 'relation')):
    """Yield element if it is the right type of tag"""

    context = ET.iterparse(osm_file, events=('start', 'end'))
    _, root = next(context)
    for event, elem in context:
        if event == 'end' and elem.tag in tags:
            yield elem
            root.clear()

#Function below outputs the data into a JSON formatted file
def process_map(file_in):
    # You do not need to change this file
    file_out = "{0}.json".format(file_in)
    data = []
    with codecs.open(file_out, "w", "utf-8") as fo:
        for element in get_element(file_in):
            el = shape_element(element)
            if el:
                data.append(el)
#                fo.write(json.dumps(el, ensure_ascii=False) + "\n")

    return data    

if __name__ == "__main__":
    data = process_map('sydney_australia.osm')

