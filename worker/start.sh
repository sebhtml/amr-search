#!/bin/bash

cd /mnt/worker

source ardm-virtualenv/bin/activate

cd amr-search

nohup data_fetcher/analysis_engine.py run-daemon &> log &
