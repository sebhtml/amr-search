
class Feature

    attr_accessor :feature_number, :probe_number, :probe_name, :probe_sequence

    def initialize feature_number, probe_number, probe_name, probe_sequence
        @feature_number = feature_number
        @probe_number = probe_number
        @probe_name = probe_name
        @probe_sequence = probe_sequence.upcase
        @gene_name = "NULL"
        # puts "name= #{@probe_name}"

        parse_gene
    end

    def parse_gene

        if detect_gene_with_pipe
        elsif detect_gene_with_parenthesis
        elsif detect_gene_with_number
        end

        @gene_name
    end

    def gene
        @gene_name
    end

    private

    def is_numeric? character
        character =~ /[[:digit:]]/
    end

    # parse this:
    # AB074437|17-754|blaIMP-11 family|647-682
    def detect_gene_with_pipe

        if probe_name.include? '|'
            @gene_name = probe_name.split('|')[2]
            return true
        end

        false
    end

    # parse this:
    # AB071145:1-1143mac(A)1143_808_842
    def detect_gene_with_parenthesis

        if @probe_name.count(":") != 1
            return false
        elsif @probe_name.count("-") != 1
            return false
        end

        token = @probe_name.split(":")[1]

        token = token.split("-")[1]
        i = 0
        while i < token.length and is_numeric? token[i]
            i += 1
        end

        token = token[i..token.length - 1]
=begin
=end
        if token.include? ')'
            token = token.split(')')[0] + ')'
            @gene_name = token
# @gene_name = "PARENTHESIS " + @gene_name

            return true
        end

        false
    end

    # parse this:
    # AF012101:562-1749vceA1188_701_735
    def detect_gene_with_number
        if @probe_name.count(":") != 1
            return false
        elsif @probe_name.count("-") != 1
            return false
        end

        token = @probe_name.split(":")[1]

        token = token.split("-")[1]
        i = 0
        while i < token.length and is_numeric? token[i]
            i += 1
        end

        token = token[i..token.length - 1]

        if token.count('_') != 2
            return false
        end

        token = token.split("_")[0]

        last = token.length - 1
        while last >= 0 and is_numeric? token[last]
            last -= 1
        end

        token = token[0..last]
        @gene_name = token

        true
    end
end
