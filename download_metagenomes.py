#!/usr/bin/env python

import my_package

import requests
import urllib
import sys
import os
import logging
import json

project_name = "mgp385"

def download_data():

    name = project_name
    project = my_package.MetagenomeProject(name)

    file_with_sample_list = "samples-with-fna-format.txt"

    project.add_positive_filter_list(file_with_sample_list)
    project.set_stage("upload")
    project.download()

    arguments = sys.argv
    
def download_metadata():
    name = project_name
    project = my_package.MetagenomeProject(name)
    project.download_metagenome_metadata()
   
def main():
    download_metadata()

if __name__ == '__main__':
    main()
