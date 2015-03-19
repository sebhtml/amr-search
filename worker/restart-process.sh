#!/bin/bash

cd /mnt/worker/
source ardm-virtualenv/bin/activate
killall python
cd amr-search/
./data_fetcher/analysis_engine.py run-daemon &> log-$(date +%Y-%m-%d-%H-%M-%S) &
