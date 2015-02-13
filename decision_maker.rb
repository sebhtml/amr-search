
require 'csv'

class DecisionMaker
    def initialize
        @feature_counts = {}
        @probes = {}
    end

    def load_alignment_data file
        CSV.foreach(file) do |row|
            feature_name = row[1]
        end
    end

    def load_microarray_probe_data file
        CSV.foreach(file) do |row|
            puts row
        end
    end
end
