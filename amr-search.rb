#!/usr/bin/env ruby

# Dependencies:
#
# ruby
# bash
# coreutils
# seqtk
# vsearch

# Search DNA sequencing reads against
# ARDB v2 and v3 microarray probe sequences
# To do so, use vsearch with these options:
# --minseqlength 24 to avoid discarding probes,
# --target_cov 0.90 to cover a good percentage of probes
# --id 0.90 to allow some mismatches
# --maxaccepts 4 (the same probe is present in at most 4 features)

if ARGV.size != 1
    puts "Missing argument, please provide a fastq file"
    exit
end

query=ARGV[0]

database="/bigdata/seb/amr-search/ARDM_v2_and_v3.fasta"

#fastq2fasta.pl $query > $query.fasta

command = "time cat #{query} | seqtk seq -A - > #{query}.fasta"

#STDERR.puts "Running #{command}"
success = Kernel.system(command)

unless success
    STDERR.puts "Failed to convert file, do you have seqtk in your path ?"
    exit
end

Kernel.system("
vsearch \
    --minseqlength 24 \
    --usearch_global #{query}.fasta \
    --db #{database} \
    --id 0.90 \
    --target_cov 0.90 \
    --blast6out #{query}.csv \
    --maxaccepts 4 \
    ")


#Kernel.system("rm #{query}.fasta")

STDERR.puts("Output: #{query}.csv")
