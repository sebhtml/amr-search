#!/usr/bin/env python

import my_package
import pymongo
import json
from flask import request
from flask import abort

from flask import Flask
app = Flask(__name__)

app.debug = True

mongodb_address = "10.1.28.53"

mongo_connection = pymongo.MongoClient(mongodb_address, 27017)

database_name = "ardm-database"
sample_collection_name = "samples"
sample_collection = mongo_connection[database_name][sample_collection_name]

@app.route('/context')
def context():
    return str(request.url_root)

@app.route('/samples')
def samples():
    response = {}
    my_list = []
    cursor = sample_collection.find({})

    for document in cursor:
        item = {}
        identifier = document["_id"]
        item["id"] = identifier
        item["link"] = request.url_root + "samples/{}".format(identifier)

        my_list.append(item)

    response["samples"] = my_list

    return json.dumps(response)

@app.route('/samples/<sample_id>')
def sample(sample_id):
    
    cursor = sample_collection.find({"_id": sample_id})

    if cursor.count() != 1:
        abort(404)

    document = cursor.next()

    item = {}
    identifier = document["_id"]
    item["id"] = identifier
    item["link"] = request.url_root + "samples/{}".format(identifier)
    item["hits"] = {}

    return json.dumps(item)

if __name__ == '__main__':
    #samples()
    app.run(host='0.0.0.0')
