
class Feature

    attr_accessor :feature_number, :probe_number, :probe_name, :probe_sequence

    def initialize feature_number, probe_number, probe_name, probe_sequence
        @feature_number = feature_number
        @probe_number = probe_number
        @probe_name = probe_name
        @probe_sequence = probe_sequence.upcase
    end
end
