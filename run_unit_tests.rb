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

    def foo
        assert_equal(1, 2)
    end

    def teardown

    end
end

suite = Test::Unit::TestSuite.new "Test 1"
suite << MyTestCase.new("load_microarray_v2")
suite << MyTestCase.new("load_microarray_v3")

Test::Unit::UI::Console::TestRunner.run(suite)
