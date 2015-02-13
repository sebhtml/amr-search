#!/usr/bin/env python

import sys
import os

if len(sys.argv) != 3:
    print("Usage: " + sys.argv[0] + " fasta_file name_file")
    sys.exit()

fasta_file = sys.argv[1]
name_file = sys.argv[2]

#print(name_file)

names = {}

with open(name_file) as f:
    for line in f:
        names[line.strip()] = True

keep = False

with open(fasta_file) as f:
    for line in f:
        if line[0] == '>':
            name = line.replace('>', '').strip()
            if name in names:
                print(line.strip())
                keep = True
        elif keep:
            print(line.strip())
            keep = False
