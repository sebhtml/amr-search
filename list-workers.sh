#!/bin/bash

pdsh -w ^workers.txt 'uname -a'|dshbak -c
