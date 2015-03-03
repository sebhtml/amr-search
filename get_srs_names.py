#!/usr/bin/env python

import os
import json
import my_package
from os import listdir

xml_directory = "xml_files"

json_directory = "mgp385_metagenome_metadata"

for file in os.listdir(json_directory):
    with open(os.path.join(json_directory, file)) as f:
        content = f.read()
        tree = json.loads(content)
        srr_number = tree["name"]

        probe = my_package.SRAFetcher(srr_number, xml_directory)
        probe.download_xml()

        break
