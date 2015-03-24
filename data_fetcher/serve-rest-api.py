#!/usr/bin/env python

import my_package
import pymongo
import json
from flask import request
from flask import abort
from flask.ext.cors import CORS

from flask import Flask

app = Flask(__name__)
cors = CORS(app)

app.debug = True
app.debug = False

database = my_package.Database()

sample_collection = database.get_sample_collection()

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
    item["hits"] = document["hits"]
    item["total_number_of_sequences"] = document["total_number_of_sequences"]
    item["number_of_matched_sequences"] = document["number_of_matched_sequences"]

    return json.dumps(item)

if __name__ == '__main__':
    #samples()
    app.run(host='0.0.0.0')
