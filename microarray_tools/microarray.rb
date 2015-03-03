
require_relative 'feature'

require 'csv'

class Microarray
    def initialize
        @features = []
    end

    def load_from_file file
        @file = file

        version = "v2"

        if file.include? "v3"
            version = "v3"
        end

        @version = "v3"

        CSV.foreach(file, {:col_sep => "\t"}) do |row|

            next if row.size == 0
            next if row[0] == 'Feature'
            next if row[0] == 'Feature #'

            # puts row.to_s

            feature = Feature.new row[0], row[1], row[2], row[3]

            @features.push feature
        end

        @features.each do |feature|
            @genes = {}
            gene = feature.gene

            if not @genes.has_key? gene
                @genes[gene] = Hash.new
            end
            @genes[gene][get_key(feature)] = 0
        end
    end

    def feature_count
        @features.size
    end

    def print_genes

        @features.each do |feature|
            probe_name = feature.probe_name
            gene = feature.gene

            puts probe_name + " ---> " + gene
        end
    end

    def print_keys

    end

    private

    def get_key feature
        @version + feature.feature_number + "-" + feature.probe_number + "-" + feature.probe_name
    end
end
