#!/usr/bin/env python

import requests
import urllib
import sys

class MetagenomeProject:
    def __init__(self, name):
        self.name = name
        self.positive_filter_list = None
        self.negative_filter_list = None
        self.selected_stage = None

    def download(self):

        project_api_call = "http://api.metagenomics.anl.gov/project/{}?verbosity=full"
        download_metagenome_api_call = "http://api.metagenomics.anl.gov/download/{}"

        project = self.name

        address = project_api_call.format(project)

        request = requests.get(address)
        code = request.status_code

        if code != 200:
            print("There was a problem with the status code: {}".format(code))
            return

        project_data = request.json()

        for metagenome in project_data["metagenomes"]:
            metagenome_name = metagenome[0]
            if self.metagenome_must_be_processed(metagenome_name):
                address = download_metagenome_api_call.format(metagenome_name)
                request = requests.get(address)

                if code == 200:
                    json_data = request.json()
                    data = json_data["data"]
                    
                    for stage in data:
                        stage_name = stage["stage_name"]
                        url = stage["url"]
                        file_name = stage["file_name"]

                        if self.use_stage_name(stage_name):
                            print("curl {} > {}".format(url, file_name))
    
    def use_stage_name(self, stage_name):
        if self.selected_stage != None:
            if stage_name != self.selected_stage:
                return False

        return True

    def metagenome_must_be_processed(self, metagenome):
        if self.positive_filter_list != None:
            if metagenome not in self.positive_filter_list:
                return False

        if self.negative_filter_list != None:
            if metagenome in self.negative_filter_list:
                return False

        return True

    def add_positive_filter_list(self, sample_list_file):
        self.positive_filter_list = {}

        with open(sample_list_file) as f:
            for line in f:
                sample_name = line.strip()
                self.positive_filter_list[sample_name] = True

    def set_stage(self, stage_name):
        self.selected_stage = stage_name

def main():

    # check Python version
    if sys.version_info < (2.7):
        print("This software needs at l=east Python 2.7.")
        sys.exit()

    name = "mgp385"
    project = MetagenomeProject(name)

    file_with_sample_list = "samples-with-fna-format.txt"

    project.add_positive_filter_list(file_with_sample_list)
    project.set_stage("upload")
    project.download()

    arguments = sys.argv
    

if __name__ == '__main__':
    main()
