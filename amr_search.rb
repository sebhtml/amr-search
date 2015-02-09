#!/usr/bin/env ruby

require 'csv'

# Dependencies:
#
# ruby (tested with Ruby 2.2.0)
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

purge_files = false
query=ARGV[0]

database="/bigdata/seb/amr-search/ARDM_v2_and_v3.fasta"

#fastq2fasta.pl $query > $query.fasta

fasta_query = query + ".fasta"

unless File.exists? fasta_query
    #STDERR.puts "Running #{command}"
    command = "time cat #{query} | seqtk seq -A - > #{fasta_query}"
    success = Kernel.system(command)

    unless success
        STDERR.puts "Failed to convert file, do you have seqtk in your path ?"
        exit
    end
end


output = query + ".csv"

unless File.exists? output
    Kernel.system("
    vsearch \
    --minseqlength 24 \
    --usearch_global #{fasta_query} \
    --db #{database} \
    --id 0.90 \
    --target_cov 0.90 \
    --blast6out #{output} \
    --maxaccepts 4 \
    ")
end

#STDERR.puts("Output: #{query}.csv")

i = 0

content = File.read(output)
csv = CSV.parse(content, {:headers => false, :col_sep => "\t"})

probe_hits = Hash.new

csv.each do |row|
    #STDERR.puts i.to_s + " ---> " + row.size.to_s + " " + row.to_s
    #STDERR.puts "Found a probe hit: " + row[1]

    probe_name = row[1]

    if probe_hits[probe_name].nil?
        probe_hits[probe_name] = 0
    end

    probe_hits[probe_name] += 1

    i += 1
end

sorted_probes = probe_hits.to_a.sort { |x, y| y[1] <=> x[1] }

sorted_probes.each do |pair|
    probe_name = pair[0]
    read_count = pair[1]

    puts read_count.to_s + " " + probe_name
end

if purge_files
    Kernel.system("rm #{fasta_query}")
end

