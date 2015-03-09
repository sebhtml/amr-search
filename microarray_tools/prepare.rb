#!/usr/bin/env ruby

require 'csv'

files = ["ARDMv2.csv", "ARDMv3-delta.csv"]

probes = {}

files.each do |file|
    #puts "Opening #{file}"

    version = "v2"

    if file == "ARDMv3-delta.csv"
        version = "v3"
    end

    # using :col_sep => "\t" hangs...
    CSV.foreach(file) do |row|
        row = row.first.split "\t"

        if row[0] == "Feature #"
            next
        end

        feature_number = row[0]
        probe_number = row[1]
        probe_name = row[2]

        #puts ">" + version + "-" + feature_number + "-" + probe_number + "-" + probe_name

        if probes.has_key? probe_name
            next
        end

        puts ">" + probe_name
        puts row[3].upcase
        probes[probe_name] = 1
    end
end

