#!/bin/bash

cd /mnt

sudo apt-get update -y
sudo apt-get install -y ruby make gcc python-pip zlib1g-dev git

sudo pip install virtualenv

virtualenv ardm-virtualenv
source ardm-virtualenv/bin/activate

git clone https://github.com/sebhtml/amr-search.git
cd amr-search
ln -s ~/ardm-assets
pip install -r data_fetcher/requirements.txt

# vsearch/1.1.1
wget https://github.com/torognes/vsearch/releases/download/v1.1.1/vsearch-1.1.1-linux-x86_64
chmod +x vsearch-1.1.1-linux-x86_64
sudo cp vsearch-1.1.1-linux-x86_64 /usr/local/bin/vsearch

# seqtk (no version)
git clone https://github.com/lh3/seqtk.git
cd seqtk
make
sudo cp seqtk /usr/local/bin

