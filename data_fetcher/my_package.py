
import time
import requests
import os
import redis
import xml.etree.ElementTree
import json
import logging
import sys
import os.path
import prettytable
import requests_cache
import httplib
import subprocess
import procfs
import multiprocessing

import xmltodict

working_directory="/mnt/worker"

alignment_directory = "alignments"

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

        cache = InputDataDownloader()
        for item in items:
            file_name = item[0]
            address = item[1]
            file_size = item[2]["file_size"]
            cache.download(file_name, address, file_size)

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

                self._uploaded_files.append([file_name, address + "?file={}".format(file_id), item])

    def delete_file_from_cache(self):
        return -1

    def are_files_available_in_cache(self):
        items = self.get_uploaded_files()
        cache = InputDataDownloader()

        for item in items:
            file_name = item[0]

            the_file_exists = cache.is_entry_in_cache(file_name, item[2]["file_size"])

            if not the_file_exists:
                return False

        return True

    def is_aligned(self):
        return self._is_aligned_redis()

    def _is_aligned_vfs(self):

        items = self.get_uploaded_files()
        cache = InputDataDownloader()

        for item in items:
            file_name = item[0]
            if not cache.is_aligned(file_name):
                return False

        return True

    def _is_aligned_redis(self):

        items = self.get_uploaded_files()
        warehouse = Warehouse.get_singleton()

        for item in items:
            file_name = item[0]
            if not warehouse.is_aligned(file_name):
                return False

        return True

    def align(self):

        items = self.get_uploaded_files()

        # get token from warehouse
        warehouse = Warehouse.get_singleton()

        if not os.path.isdir(alignment_directory):
            os.mkdir(alignment_directory)

        for item in items:
            file_name = item[0]

            logging.debug("Aligning data file {}".format(file_name))

            with open("{}/{}.json".format(alignment_directory, file_name), "w") as out:
                process = subprocess.Popen(["./microarray_tools/amr_search.rb",
                                "input_data_cache/{}".format(file_name)], stdout = out, stderr= subprocess.PIPE)

                stdout, stderr = process.communicate()

            warehouse.push_alignment(file_name)

    def purge(self):

        items = self.get_uploaded_files()

        cache = InputDataDownloader()
        for item in items:
            file_name = item[0]

            cache.delete_cache_entry(file_name)

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

        self._get_body_site()

    @staticmethod
    def get_samples(self):
        return []

    def _get_body_site(self):
        endpoint = "http://www.ebi.ac.uk/ena/data/view/{}&display=xml".format(self.get_name())

        request = requests.get(endpoint)

        if request.status_code != httplib.OK:
            raise Exception("Invalid code")

        content = request.text

        dictionnary = xmltodict.parse(content)

        items = dictionnary["ROOT"]["SAMPLE"]["SAMPLE_ATTRIBUTES"]["SAMPLE_ATTRIBUTE"]

        for item in items:
            tag = item["TAG"]
            value = item["VALUE"]

            if tag == "body site":
                self.site = value
                break

    def get_site(self):
        return self.site

    def get_name(self):
        return self.name

    def get_state(self):
        self._check_data()
        return self.input_data_in_cache

    def synchronize(self):
        self._check_data()

    def get_mgrast_metagenomes(self):
        return self._metagenomes

    def _check_data(self):
        # TODO this has a linear time complexity.
        # to do better than this, we probably want to use redis or mongodb..
        # anyway..

        self.input_data_in_cache = True

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

    def download(self):

        warehouse = Warehouse.get_singleton()

        # lock the sample before downloading.
        # alignment is a dependency anyway.
        if not warehouse.lock(self.get_name()):
            logging.debug("can not lock {}, skipping".format(self.get_name()))
            return

        logging.debug("download sample {}".format(self.get_name()))

        metagenomes = self.get_mgrast_metagenomes()
        for item in metagenomes:
            metagenome = MgRastMetagenome(item)
#logging.debug("download sample {}, metagenome {}".format(self.get_name(), item))
            metagenome.download()

        self.input_data_in_cache = True

    def align(self):

        if self.is_aligned():
            logging.debug("{} is already aligned".format(self.get_name()))
            return

        if not self.get_state():
            logging.debug("{} is not available locally".format(self.get_name()))
            return

        logging.debug("OK. aligning {}".format(self.get_name()))

        metagenomes = self.get_mgrast_metagenomes()
        for item in metagenomes:
            metagenome = MgRastMetagenome(item)
            metagenome.align()

    def is_aligned(self):
        metagenomes = self.get_mgrast_metagenomes()
        for item in metagenomes:
            metagenome = MgRastMetagenome(item)
            if not metagenome.is_aligned():
                return False

        return True

    def has_summary(self):
        return False

    def purge_input_data(self):

        logging.debug("Purging sample input data for {}".format(self.get_name()))

        metagenomes = self.get_mgrast_metagenomes()
        for item in metagenomes:
            metagenome = MgRastMetagenome(item)
            metagenome.purge()

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
            print("purge            delete input data for samples that have alignments")
            print("show-sample")
            print("align-sample")
            print("align-samples")
            print("download-sample")
            print("download-samples")
            print("align-samples-in-process    -      align samples in a separate process")
            print("download-samples-in-process    -      download samples in a separate process")
            print("purge-in-process         -      purge samples in a separate process")
            print("drop-caches          -   drop file system cache (pagecache, dentries, inodes)")
            print("run-daemon       -  download, align, and purge in parallel")

            return

        command = arguments[1]

#print("command= {}".format(command))

        if command == "list-samples":
            self.list_samples()

        elif command == "drop-caches":
            self.drop_caches()

        elif command == "show-sample":
            self.show_sample()

        elif command == "download-sample":
            self.download_sample()

        elif command == "download-samples":
            self.download_samples()

        elif command == "download-samples-in-process":
            self.download_samples_in_process()

        elif command == "run-daemon":
            self.run_daemon()

        elif command == "align-sample":
            self.align_sample()

        elif command == "purge":
            self.purge()

        elif command == "purge-in-process":
            self.purge_in_process()

        elif command == "align-samples":
            self.align_samples()

        elif command == "align-samples-in-process":
            self.align_samples_in_process()

    def purge_in_process(self):
        while True:
            try:
                self.purge()
            except Exception as e:
                print(str(e))
            time.sleep(5)

    def align_samples_in_process(self):
        while True:
            try:
                self.align_samples()
            except Exception as e:
                print(str(e))
            time.sleep(5)

    def download_samples_in_process(self):
        while True:
            try:
                self.download_samples()
            except Exception as e:
                print(str(e))
            time.sleep(5)

    def drop_caches(self):
        fs = FileSystem("/")
        fs.drop_caches()

    def run_daemon(self):
        download_process = multiprocessing.Process(target=self.download_samples_in_process)
        download_process.start()

        # avoid the sqlite error: OperationalError: database is locked
        time.sleep(5)

        align_process = multiprocessing.Process(target=self.align_samples_in_process)
        align_process.start()

        purge_process = multiprocessing.Process(target=self.purge_in_process)
        purge_process.start()

        download_process.join()
        align_process.join()
        purge_process.join()

    def purge(self):
        samples = self.get_samples()

        for sample in samples:
            sample = EbiSraSample(sample)
            if sample.is_aligned():
                if sample.get_state():
                    sample.purge_input_data()

    def align_sample(self):
        if len(sys.argv) != 3:
            print("show-sample: needs a sample name!")
            return

        sample_name = sys.argv[2]

        sample = EbiSraSample(sample_name)
        sample.align()

    def _not_enough_free_space(self):
        mount_point = working_directory
        vfs = FileSystem(mount_point)

        free_bytes = vfs.get_free_byte_count()

        # 50 GiB
        minimum = 50 * 1024 * 1024 * 1024

        return free_bytes < minimum

    def download_samples(self):

        samples = self.get_samples()

        for sample_name in samples:

            if self._not_enough_free_space():
                logging.debug("not enough free space...")
                return

            sample = EbiSraSample(sample_name)

            # only download those that are not aligned
            if not sample.is_aligned():
                sample.download()

    def download_sample(self):
        if len(sys.argv) != 3:
            print("show-sample: needs a sample name!")
            return

        sample_name = sys.argv[2]

        sample = EbiSraSample(sample_name)
        sample.download()

    def show_sample(self):
        cache = InputDataDownloader()
        if len(sys.argv) != 3:
            print("show-sample: needs a sample name!")
            return

        sample_name = sys.argv[2]

        sample = EbiSraSample(sample_name)

        print("Name: {}".format(sample_name))
        print("Site: {}".format(sample.get_site()))
        print("input_data_available: {}".format(sample.get_state()))
        print("is_aligned: {}".format(sample.is_aligned()))

        print("MG-RAST metagenomes (SRA runs)")

        metagenomes = sample.get_mgrast_metagenomes()
        for item in metagenomes:
            print("- {} ({})".format(item, metagenomes[item]))
            metagenome = MgRastMetagenome(item)
            items = metagenome.get_uploaded_files()

            for item in items:
                file_name = item[0]
                expected_file_size = item[2]["file_size"]
                state = cache.is_entry_in_cache(file_name, expected_file_size)
                size = expected_file_size
                md5_key = "file_md5"
                md5sum = item[2][md5_key]

                aligned = cache.is_aligned(file_name)
                print("  - {} (available: {}, aligned: {}, md5: {}, size: {})".format(file_name, state,
                                        aligned, md5sum, size))

#print("sample   site    runs_in_cache")

    def get_samples(self):
        samples = {}

        with open("metagenome_paths.txt") as f:
            for line in f:
                tokens = line.split()

        # Path: mgm4472521.3 -> SRR060413 -> SRS011269
                sample = tokens[5]

                samples[sample] = 99

        samples = samples.keys()
        samples = sorted(samples)

        return samples

    def list_samples(self):

        aligned_count = 0
        total = 0

        samples = self.get_samples()
        table = prettytable.PrettyTable(["sample", "site", "input_data_available", "aligned", "Summary"])
        for sample in samples:
            sample_object = EbiSraSample(sample)

            site = sample_object.get_site()
            state = sample_object.get_state()
            aligned = sample_object.is_aligned()
            has_summary = sample_object.has_summary()

            table.add_row([sample, site, state, aligned, has_summary])

            if aligned:
                aligned_count += 1

            total += 1

        print(table)

        print("Total count: {}".format(total))
        print("Aligned count: " + str(aligned_count))

    def align_samples(self):

        samples = self.get_samples()
        for sample in samples:
            sample_object = EbiSraSample(sample)
            sample_object.align()

class InputDataDownloader:
    def __init__(self):
        self._directory = "input_data_cache"

    def download(self, name, address, file_size):

        if self.is_entry_in_cache(name, file_size):
            return

        logging.debug("Download {} to {}".format(address, name))
        if not os.path.isdir(self._directory):
            os.mkdir(self._directory)

        with open(os.path.join(self._directory, name), "w") as out:
            process = subprocess.Popen(["curl", address], stdout = out, stderr= subprocess.PIPE)
            stdout, stderr = process.communicate()

    def delete_cache_entry(self, name):
        if os.path.isfile(os.path.join(self._directory, name)):
            os.remove(os.path.join(self._directory, name))

    def is_entry_in_cache(self, name, file_size):
        path = os.path.join(self._directory, name)
        if not os.path.isfile(path):
            return False

        actual_file_size = os.path.getsize(path)

        return actual_file_size == file_size

    def is_aligned(self, name):
        path = "{}/{}.json".format(alignment_directory, name)
        if not os.path.isfile(path):
            return False
        if os.path.getsize(path) == 0:
            return False

        return True

class FileSystem:
    def __init__(self, path):
        self._path = path

    def get_free_byte_count(self):
        data = os.statvfs(self._path)
        block_size = data.f_bsize
        free_block_count = data.f_bavail

# >>> import os
# >>> os.statvfs("/space2")
# posix.statvfs_result(f_bsize=4096, f_frsize=4096, f_blocks=6527485956, f_bfree=390162322, f_bavail=62478226, f_files=409600000, f_ffree=404034293, f_favail=404034293, f_flag=4096, f_namemax=255)

        byte_count = free_block_count * block_size

        return byte_count

    def drop_caches(self):
        proc = procfs.Proc()

        self._update('/proc/sys/vm/drop_caches', '3\n')
        self._update('/proc/sys/vm/drop_caches', '0\n')

    def _update(self, path, content):
        return

# all the redis logic is in here
class Warehouse:
    def __init__(self, redis_address):
        self._redis = redis.StrictRedis(host=redis_address, port=6379, db=0)

        self._redis.setnx('schema_version', '1')

    @staticmethod
    def get_singleton():
        address = '10.1.28.25'
        return Warehouse(address)

    def is_aligned(self, file_name):
        redis_key = self._get_key(file_name)
        return self._redis.exists(redis_key)

    def lock(self, name):
        return self._redis.setnx(",".join(["lock", name]), True)

    def _get_key(self, file_name):
        return ",".join(["alignments", file_name + ".json"])

    def push_alignment(self, file_name):
        # check if the file is here locally...
        path = os.path.join("alignments", file_name + ".json")
        redis_key = self._get_key(file_name)

        if not self._redis.exists(redis_key):
            if os.path.isfile(path) and os.path.getsize(path) > 0:
                logging.debug("Warehouse check SUCCESS {} is in VFS, push to redis with key {}".format(path, redis_key))
                self._redis.setnx(redis_key, open(path).read())


