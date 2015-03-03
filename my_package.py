
import requests
import os

class SRAFetcher:
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
