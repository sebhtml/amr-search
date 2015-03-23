#!/usr/bin/env python

import pymongo
import redis
import json

# this code is not used.

class Loader:
    def __init__(self, redis_address, mongodb_address):
        self._redis_address = redis_address
        self._mongodb_address = mongodb_address
    def load(self):
        return 0
    def _load(self):

        redis_connection = redis.StrictRedis(host=self._redis_address, port=6379, db=0)

        mongo_connection = pymongo.MongoClient(self._mongodb_address, 27017)

        sample_collection = mongo_connection["ardm-database"]["samples"]
        alignment_collection = mongo_connection["ardm-database"]["alignments"]

        for sample in sample_collection.find():

            sample_id = sample["_id"]
            metagenomes = sample["metagenomes"]
            
            if "hits" not in sample:
                sample["hits"] = {}
                sample_collection.save(sample)

            for metagenome in metagenomes:

                aligned = False

                # mgm4472777.3.050.1.upload.fastq
                key = "{}.050.1.upload.fastq".format(metagenome)
                cursor = alignment_collection.find({"_id": key})

                aligned = cursor.count() > 0
                print("{} -> {} (Aligned= {})".format(sample_id, metagenome, aligned))
    


    def _import_redis_json(self):
        for key in redis_connection.keys():
            if key.find("alignments") >= 0:
                print("key= {}".format(key))

                content = redis_connection.get(key)
                json_object = json.loads(content)

                #print("KEY " + key)
                #print("CONTENT " + content)
                print(json_object)

                # alignments,mgm4473256.3.050.1.upload.fastq.json#
                fastq_file_name = key.replace("alignments,", "").replace(".json", "")

                print("fastq " + fastq_file_name)

                json_object["_id"] = fastq_file_name

                document = json_object

                # clean the document...

                self.replace_dots(document)

                print("new document !")
                print(document)

                alignment_collection.insert(document)


    def _populate_samples(self):
        #alignment_collection.remove({})
        samples = {}


        metagenome_to_sample = {}

        with open('../metagenome_paths.txt') as f:
            for line in f:
                tokens = line.split()
                metagenome = tokens[1]
                sample = tokens[5]

                metagenome_to_sample[metagenome] = sample

                print("{} -> {}".format(metagenome, sample))

                cursor = sample_collection.find({"_id": sample})

                print("COUNT {}".format(str(cursor.count())))

                if cursor.count() == 0:
                    document = {"_id": sample, "metagenomes": []}
                    sample_collection.insert(document)
                
                sample_collection.update({"_id": sample}, {"$push": {"metagenomes": metagenome}})

        for key in redis_connection.keys():
            if key.find("alignments") >= 0:
                print("key= {}".format(key))

        document = {}


    def replace_dots(self, document):
        for key in document.keys():
            value = document[key]
            if key.find(".") >= 0:
                new_key = key.replace(".", "_dot_")

                # add new key without the dot symbol (".")
                document[new_key] = value

                # remove old key that has a a dot (".")
                del document[key]

            # recursive call
            if isinstance(value, dict):
                self.replace_dots(value)


        print("AFTER")
        print(document)



def main():
    redis_address = "10.1.28.25"
    mongodb_address = "10.1.28.53"

    loader = Loader(redis_address, mongodb_address)

    loader.load()

if __name__ == "__main__":
	main()


