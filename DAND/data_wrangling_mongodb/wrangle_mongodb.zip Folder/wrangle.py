from pymongo import MongoClient
from pymongo import IndexModel, ASCENDING, DESCENDING
import process_osm
import process_postcode
import fix_postcode
import fix_street
import fix_suburb_city
import analysis 

def get_db(): 
#    client = MongoClient("mongodb://udacity:data_wrangler@cluster0-shard-00-00-v2n7o.mongodb.net:27017,cluster0-shard-00-01-v2n7o.mongodb.net:27017,cluster0-shard-00-02-v2n7o.mongodb.net:27017/admin?ssl=true&replicaSet=Cluster0-shard-0&authSource=admin")
    client = MongoClient("mongodb://redhatsrv:27017")
    db = client.OSM
    return db

def insert_data(infile, db, col):
    if col == "sydney":
        data = process_osm.process_map(infile)
        db.sydney.insert_many(data)
        index_0 = IndexModel([("id", DESCENDING)], name="index_0")
        index_1 = IndexModel([("address.street", ASCENDING)], name="index_1")
        index_2 = IndexModel([("address.postcode", ASCENDING)], name="index_2")
        index_3 = IndexModel([("address.city", ASCENDING),("address.suburb", ASCENDING)], name="index_3")
        index_4 = IndexModel([("address.suburb", ASCENDING),("address.city", ASCENDING)], name="index_4")
        db.sydney.create_indexes([index_0, index_1, index_2, index_3, index_4])
    elif col == "postcode":
        data = process_postcode.csv_reader(infile)
        db.postcodes.insert_many(data)
        index_5 = IndexModel([("suburb", ASCENDING)], name="index_0")
        index_6 = IndexModel([("postcode", ASCENDING)], name="index_1")
        db.postcodes.create_indexes([index_5, index_6])


if __name__ == "__main__":
    OSM_db = get_db()
# Loading the Sydney OSM data into a collection
    print "Loading Sydney OSM data into the Sydney collection"
    insert_data('sydney_australia.osm', OSM_db, "sydney")
    print "Completed loading OSM data"
# Loading the postcodes csv file into the postcodes collection
    print "Loading all Australian postcodes into the postcodes collection"
    insert_data("AUS.csv", OSM_db, "postcode")
    print "Completed loading postcode data"
# Fixing Postcode Data
    print "************ Fixing address.postcode field ************"
    postcode_pipeline = fix_postcode.postcode_query()
    fix_postcode.process_doc(OSM_db, postcode_pipeline)
# Fixing Street information
    print "************ Fixing address.street field ************"
    street_pipeline = fix_street.street_query()
    fix_street.process_doc(OSM_db, street_pipeline)
# Fixing Suburb and city information
    print "************ Fixing address.suburb, address.city field ************"
    fix_suburb_city.fix_scenario04(OSM_db)
    query01 = fix_suburb_city.city_query01()
    query03 = fix_suburb_city.city_query03()
    fix_suburb_city.fix_scenario01(OSM_db, query01)
    fix_suburb_city.fix_scenario03(OSM_db, query03)


"""
    while True:
        print "Would you like to fix or analyse the data:"
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
"""



