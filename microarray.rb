
require_relative 'feature'

require 'csv'

class Microarray
    def initialize
        @features = []
    end

    def load_from_file file
        CSV.foreach(file, {:col_sep => "\t"}) do |row|

            next if row.size == 0
            next if row[0] == 'Feature'
            next if row[0] == 'Feature #'

            #puts row

            feature = Feature.new row[1], row[2], row[3], row[4]

            @features.push feature
        end
    end

    def feature_count
        @features.size
    end
end
