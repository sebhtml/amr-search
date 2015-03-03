
import requests
import os
import xml.etree.ElementTree
import json
import logging

import xmltodict

class SRAFetcher:
    """
    This class is useful for downloading XML files for objects identified by SRA identifier.
    """
    def __init__(self, identifier, xml_directory):
        self.identifier = identifier
        self.xml_directory = xml_directory

    def download_xml(self):
        address = "http://www.ebi.ac.uk/ena/data/view/{}&display=xml&download=xml&filename={}.xml"

        address = address.format(self.identifier, self.identifier)
        response = requests.get(address)

        if response.status_code != 200:
            raise Exception("incorrect HTTP status code..")

        if not os.path.exists(self.xml_directory):
            os.makedirs(self.xml_directory)

        with open(os.path.join(self.xml_directory, self.identifier + ".xml"), "w+") as f:
            f.write(response.text)


class MetagenomeProject:
    """
    This class is used to download information from the MG-RAST API.

    # see http://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1004008
    """

    def __init__(self, name):
        logging.basicConfig(level=logging.DEBUG)
        self.name = name
        self.positive_filter_list = None
        self.negative_filter_list = None
        self.selected_stage = None

        # check Python version
        if sys.version_info < (2.7):
            print("This software needs at l=east Python 2.7.")
            sys.exit()

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

    def download_metagenome_metadata(self):

        # see http://journals.plos.org/ploscompbiol/article?id=10.1371/journal.pcbi.1004008

        project_api_call = "http://api.metagenomics.anl.gov/project/{}?verbosity=full"
        download_metagenome_api_call = "http://api.metagenomics.anl.gov/metagenome/{}"

        project = self.name

        address = project_api_call.format(project)

        request = requests.get(address)
        code = request.status_code

        metadata_directory = project + "_metagenome_metadata"

        if not os.path.exists(metadata_directory):
            os.makedirs(metadata_directory)

        if code != 200:
            raise Exception("Error in HTTP return code.")

        project_data = request.json()

        for metagenome in project_data["metagenomes"]:
            metagenome_name = metagenome[0]
            address = download_metagenome_api_call.format(metagenome_name)
            request = requests.get(address)

            code = requests.status_code

            logging.debug("Fetching {} at {}".format(metagenome_name, address))
            
            if code != 200:
                raise Exception("Error in HTTP return code !")

            json_data = request.json()
            
            data = json_data
                    
            output = open(os.path.join(metadata_directory, metagenome_name + ".json"), "w+")
            output.write(json.dumps(data))
            output.close()


class MgRastMetagenome:
    """
    A wrapper around a MG-RAST metagenome
    """
    def __init__(self, json_file):
        with open(json_file) as f:
            json_data = json.loads(f.read())
            self.id = json_data["id"]
            self.sequencing_run = json_data["name"]

    def get_identifier(self):
        return self.id

    def get_sequencing_run(self):
        return self.sequencing_run


class EbiSraRun:
    """
    A class to read XML run files from EBI SRA.
    """
    def __init__(self, file):
        with open(file) as f:
            content = f.read()
            data = xmltodict.parse(content)
            
            identifier = data["ROOT"]["RUN"]["IDENTIFIERS"]["PRIMARY_ID"]

            self.identifier = identifier
            sample = -1

            logging.debug("file: {} run: {} sample: {}".format(file, identifier, sample))

            links = data["ROOT"]["RUN"]["RUN_LINKS"]["RUN_LINK"]

            #print(links)

            for link in links:

                #print(link)

                database = link["XREF_LINK"]["DB"]
                database_identifier = link["XREF_LINK"]["ID"]

                logging.debug("db {} id {}".format(database, database_identifier))

                if database == "ENA-SAMPLE":
                    self.sample = database_identifier

    def get_identifier(self):
        return self.identifier

    def get_sample_name(self):
        return self.sample
