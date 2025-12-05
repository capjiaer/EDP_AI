# Test Import Util File
# This file is used to test if #import in hooks can be processed correctly

puts "========== Test Import Util: Starting =========="

# Some test functions
proc test_import_function {} {
    puts "This is a function from test_import.tcl"
    return "test_import_success"
}

proc test_get_value {} {
    return "test_value_from_import"
}

puts "========== Test Import Util: Loaded =========="

