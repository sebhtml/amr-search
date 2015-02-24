#!/usr/bin/env ruby

require 'csv'

files = ["ARDMv2.csv", "ARDMv3-delta.csv"]

probes = []

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

        puts ">" + version + "-" + row[0] + "-" + row[1] + "-" + row[2]
        puts row[3].upcase
    end
end

