#!/usr/bin/env ruby

require_relative 'microarray'

if ARGV.size != 1
    puts "A microarray.csv file must be provided"
    exit
end

file = ARGV.first

a = Microarray.new
a.load_from_file file

a.print_genes
