This is the project deliverable for the module “Data Wrangling with MongoDB”. It’s all about loading data from a data source into a MongoDB database and then cleaning it. For this project, an XML extract of an area in Open Street Maps was taken and it was loaded into MongoDB and then cleaned.
I chose Sydney, Australia as the location. The reason being that this is where I live and am very familiar with the places. This makes it easier for me to validate the data in the OSM file. As a result, I didn’t have to refer to any external information. The only exception are the suburbs and their corresponding postcodes. That information was obtained from the geonames website and the URL is located in the PDF report. This postcode information was converted into a MongoDB collection called postcodes and sits in the same OSM database as the Sydney collection.

The Sydney OSM file was downloaded from Mapzen. The website URL is https://mapzen.com/data/metro-extracts/metro/sydney_australia/ and the area of Sydney covered is coloured in pink. This particular extract is the Sydney metropolitan area and its surrounding suburbs.

This file is to describe the contents of the zip file. The files that are in the zip file are the following:
* Wrangling OpenStreetMap Data_v2.pdf -> The Report of findings was done for this project.
* process_postcode.py -> Converts the postcodes CSV file into a data dictionary format for inserting into the database.
* process_osm.py -> converts OSM xml file to data dictionary format for inserting into the database.
* analysis.py -> Analyse the data held in the Sydney collection in the mongodb database OSM and it focuses on the address field
* wrangle.py -> This file is to be run first in order to insert the data into the database. To wrangle the data it calls all the other files to fix the data.
* fix_postcode.py
* fix_street.py
* fix_suburb_city.py
* sydney_australia.osm.bz2 -> Compressed file of the raw OSM xml for Sydney, Australia.
* AUS.csv -> CSV file of australian suburbs and their postcodes.
* AU.zip -> raw text file of Australian suburbs and postcodes that was massaged into CSV format later.

All the Python files with the exception of postcode_json.py and json_create.py connect to the MongoDB database in the cloud using the account “udacity”. The account along with the password is stored in the python file along with the connection string. This information could be used to view the data using the MongoDB Compass client or any other client.

