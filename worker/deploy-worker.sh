#!/bin/bash

# Ubuntu 14.04

./data_fetcher/analysis_engine.py download-samples-in-process &
./data_fetcher/analysis_engine.py align-samples-in-process &
./data_fetcher/analysis_engine.py purge-in-process &
