This project aims to search for antimicrobial resistance (AMR) genes in
the Human Microbiome Project public data using probes from the
ARDM (Antimicrobial Resistance Determinant Microarray).

Molecular Characterization of Multidrug Resistant Hospital Isolates Using the Antimicrobial Resistance Determinant Microarray
http://journals.plos.org/plosone/article?id=10.1371/journal.pone.0069507

The microarray probe data is not available publicly.


data_fetcher
============

Goal: download data for HMP samples.

Needs Python >= 2.7

To set up the virtual environment:

    virtualenv ardm-virtualenv
    source ardm-virtualenv/bin/activate
    pip install -r data_fetcher/requirements.txt

The MG-RAST Metagenome project used here is mgp385.


microarray_tools
================

Goal: run vsearch and analyze its output

Using Ruby 2.2.0

To run tests, run ./run_unit_tests.rb.

