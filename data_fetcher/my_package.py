
import requests
import os
import xml.etree.ElementTree
import json
import logging
import sys
import os.path
import prettytable
import requests_cache
import httplib

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

        if response.status_code != httplib.OK:
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

        if code != httplib.OK:
            print("There was a problem with the status code: {}".format(code))
            return

        project_data = request.json()

        for metagenome in project_data["metagenomes"]:
            metagenome_name = metagenome[0]
            if self.metagenome_must_be_processed(metagenome_name):
                address = download_metagenome_api_call.format(metagenome_name)
                request = requests.get(address)

                if code == httplib.OK:
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
        metagenome_file_call = "http://api.metagenomics.anl.gov/download/{}"

        project = self.name

        address = project_api_call.format(project)

        request = requests.get(address)
        code = request.status_code

        metadata_directory = project + "_metagenome_metadata"

        if not os.path.exists(metadata_directory):
            os.makedirs(metadata_directory)

        if code != httplib.OK:
            raise Exception("Error in HTTP return code.")

        project_data = request.json()

        for metagenome in project_data["metagenomes"]:
            metagenome_name = metagenome[0]
            address = download_metagenome_api_call.format(metagenome_name)
            request = requests.get(address)

            code = request.status_code

            logging.debug("Fetching {} at {}".format(metagenome_name, address))
            
            if code != httplib.OK:
                raise Exception("Error in HTTP return code !")

            json_data = request.json()
            
            data = json_data
                    
            output = open(os.path.join(metadata_directory, metagenome_name + ".json"), "w+")
            output.write(json.dumps(data))
            output.close()

            # also fetch the download information
            address = metagenome_file_call.format(metagenome_name)
            request = requests.get(address)

            code = request.status_code

            logging.debug("Fetching file info {} at {}".format(metagenome_name, address))

            if code != httplib.OK:
                raise Exception("Invalid code for file info")

            data = request.json()

            output = open(os.path.join(metadata_directory, metagenome_name + "-download.json"), "w+")
            output.write(json.dumps(data))
            output.close()
    
    def run_command(self):
        command = Command(sys.argv)
        command.run()

class MgRastMetagenome:
    """
    A wrapper around a MG-RAST metagenome
    """
    def __init__(self, name):
        self._cache_directory = "input_cache"

        self._uploaded_files = []

        download_metagenome_api_call = "http://api.metagenomics.anl.gov/metagenome/{}"
        metagenome_file_call = "http://api.metagenomics.anl.gov/download/{}"

        request = requests.get(download_metagenome_api_call.format(name))

        if request.status_code == httplib.OK:
            json_data = request.json()
            self.id = json_data["id"]
            self.sequencing_run = json_data["name"]
        else:
            raise Exception("invalide status code.")

    def get_identifier(self):
        return self.id

    def get_sequencing_run(self):
        return self.sequencing_run

    def get_uploaded_files(self):

        self.fetch_uploaded_files()
        return self._uploaded_files

    def download(self):
        self.fetch_uploaded_files()

        items = self.get_uploaded_files()

        for item in items:
            print(str(item))

    def fetch_uploaded_files(self):
        download_metagenome_api_call = "http://api.metagenomics.anl.gov/download/{}"
        address = download_metagenome_api_call.format(self.id)
#logging.debug("Downloading from {}".format(address))

        request = requests.get(address)
        if request.status_code != httplib.OK:
            raise Exception("invalid code..")

        json_data = request.json()

        items = json_data["data"]

        for item in items:
            stage = item["stage_name"]

            if stage == "upload":
                file_id = item["file_id"]

                file_name = "{}.{}.upload.fastq".format(self.id, file_id)
            
                self._uploaded_files.append([file_name, address + "file={}".format(file_id)])

    def delete_file_from_cache(self):
        return -1

    def are_files_available_in_cache(self):
        items = self.get_uploaded_files()

        for item in items:
            file_name = item[0]
            cache_file_path = os.path.join(self._cache_directory, "/", file_name)

            the_file_exists = os.path.isfile(cache_file_path)

            if not the_file_exists:
                return False

        return True 

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

class EbiSraSample:
    def __init__(self, name):
        self.name = name
        self.site = "?"
        self.input_data_in_cache = False
        self._metagenomes = {}

        self._check_data()

    def get_site(self):
        return self.site

    def get_name(self):
        return self.name

    def get_state(self):
        return self.input_data_in_cache

    def synchronize(self):
        self._check_data()

    def get_mgrast_metagenomes(self):
        return self._metagenomes

    def _check_data(self):
        # TODO this has a linear time complexity.
        # to do better than this, we probably want to use redis or mongodb..
        # anyway..
        with open("metagenome_paths.txt") as f:
            for line in f:
                tokens = line.split()
                sample = tokens[5]

                if sample == self.name:
                    metagenome = tokens[1]
                    run = tokens[3]

                    self._metagenomes[metagenome] = run
                    metagenome = MgRastMetagenome(metagenome)

                    available = metagenome.are_files_available_in_cache()

                    if not available:
                        self.input_data_in_cache = False
                        return

    def download(self):
        metagenomes = self.get_mgrast_metagenomes()
        for item in metagenomes:
            metagenome = MgRastMetagenome(item)
            logging.debug("download sample {}, metagenome {}".format(self.get_name(), item))
            metagenome.download()

        self.input_data_in_cache = True
 
class Command:
    def __init__(self, arguments):
        self.arguments = arguments

        # Use a HTTP cache for responses.
        requests_cache.install_cache('demo_cache')

    def run(self):
        arguments = self.arguments
        if len(arguments) == 1:
            print("Please provide a sub-command:")
            print("list-samples")
            print("show-sample")
            print("download-sample-data")
            print("list-probes")
            print("start-download-worker")
            print("start-analysis-worker")
            return

        command = arguments[1]

#print("command= {}".format(command))

        if command == "list-samples":
            self.list_samples()

        elif command == "show-sample":
            self.show_sample()
        elif command == "download-sample-data":
            self.download_sample()

    def download_sample(self):
        if len(sys.argv) != 3:
            print("show-sample: needs a sample name!")
            return

        sample_name = sys.argv[2]

        sample = EbiSraSample(sample_name)
        sample.download()

    def show_sample(self):
        if len(sys.argv) != 3:
            print("show-sample: needs a sample name!")
            return

        sample_name = sys.argv[2]

        sample = EbiSraSample(sample_name)

        print("Name: {}".format(sample_name))
        print("Site: {}".format(sample.get_site()))
        print("input_data: {}".format(sample.get_state()))

        print("MG-RAST metagenomes (SRA runs)")

        metagenomes = sample.get_mgrast_metagenomes()
        for item in metagenomes:
            print("- {} ({})".format(item, metagenomes[item]))
            metagenome = MgRastMetagenome(item)
            items = metagenome.get_uploaded_files()

            for item in items:
                print("  +++ {}".format(item[0]))

    def list_samples(self):
#print("sample   site    runs_in_cache")

        samples = {}

        with open("metagenome_paths.txt") as f:
            for line in f:
                tokens = line.split()
            
        # Path: mgm4472521.3 -> SRR060413 -> SRS011269
                sample = tokens[5]

                samples[sample] = 99
        
        samples = samples.keys()
        samples = sorted(samples)

        table = prettytable.PrettyTable(["sample", "site", "input_data", "probe_counts"])
        for sample in samples:
            sampleObject = EbiSraSample(sample)

            site = sampleObject.get_site()
            state = sampleObject.get_state()

            table.add_row([sample, site, state, "-"])

        print(table)
