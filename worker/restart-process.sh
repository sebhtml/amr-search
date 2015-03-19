#!/bin/bash

cd /mnt/worker/
source ardm-virtualenv/bin/activate
killall python
cd amr-search/
git pull origin master
./data_fetcher/analysis_engine.py run-daemon &> log-$(date +%Y-%m-%d-%H-%M-%S) &
