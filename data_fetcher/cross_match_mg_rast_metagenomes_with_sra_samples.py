#!/usr/bin/env python

import my_package
import os
import json
import logging

mg_rast_metagenomes = {}
sra_runs = {}

mg_rast_directory = "mgp385_metagenome_metadata"
sra_run_directory = "xml_files"

#logging.basicConfig(level=logging.DEBUG)

for metagenome in os.listdir(mg_rast_directory):
    file = os.path.join(mg_rast_directory, metagenome)
    metagenome = my_package.MgRastMetagenome(file)

    identifier = metagenome.get_identifier()
    mg_rast_metagenomes[identifier] = metagenome


for run in os.listdir(sra_run_directory):
    file = os.path.join(sra_run_directory, run)
    run = my_package.EbiSraRun(file)

    identifier = run.get_identifier()
    sra_runs[identifier] = run

for metagenome_name in mg_rast_metagenomes:
    metagenome = mg_rast_metagenomes[metagenome_name]
    run = sra_runs[metagenome.get_sequencing_run()]
    run_name = run.get_identifier()
    sample_name = run.get_sample_name()

    print("Path: {} -> {} -> {}".format(metagenome_name, run_name, sample_name))
