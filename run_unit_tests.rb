#!/usr/bin/env ruby

require "test/unit"

require 'test/unit/ui/console/testrunner'

require_relative 'microarray'

class MyTestCase < Test::Unit::TestCase

    def setup

    end

    def load_microarray_v2
        microarray = Microarray.new
        microarray.load_from_file "Microarray/ARDMv2.csv"

        assert_equal 2240, microarray.feature_count
    end

    def load_microarray_v3
        microarray = Microarray.new
        microarray.load_from_file "Microarray/ARDMv3-delta.csv"

        assert_equal 2240, microarray.feature_count
    end

    def load_microarray_v2_v3

        microarray = Microarray.new
        microarray.load_from_file "Microarray/ARDMv2.csv"
        microarray.load_from_file "Microarray/ARDMv3-delta.csv"

        assert_equal 2 * 2240, microarray.feature_count
    end

    def foo
        assert_equal(1, 2)
    end

    def get_genes
        tests = [
                    ["M55547:2314-3138blaOXA-9825_17_51", "blaOXA-9"],
                    ["X02588:331-1113ant(9)-Ia783_261_299", "ant(9)-Ia"],
                    ["AF189721:274-1149blaCTX-M-8876_577_611", "blaCTX-M-8"]
                ]
        tests.each do |probe_name, gene_name|
            feature = Feature.new 1, 1, probe_name, "ATCG"
            assert_equal gene_name, feature.gene
        end

    end

    def teardown

    end
end

suite = Test::Unit::TestSuite.new "Test 1"
suite << MyTestCase.new("load_microarray_v2")
suite << MyTestCase.new("load_microarray_v3")
suite << MyTestCase.new("load_microarray_v2_v3")
suite << MyTestCase.new("get_genes")

Test::Unit::UI::Console::TestRunner.run(suite)
