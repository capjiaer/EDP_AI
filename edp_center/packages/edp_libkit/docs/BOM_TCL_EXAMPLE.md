# BOM TCL Example

## Overview
Bill of Materials (BOM) TCL scripts define the complete set of library files needed for a design flow.

## Example Structure
```tcl
# Library Configuration
set LIBRARY(gds_file) "/path/to/library.gds"
set LIBRARY(lef_file) "/path/to/library.lef"
set LIBRARY(lib_file) "/path/to/library.lib"

# Timing Libraries
set LIBRARY(ccs_lvf) "/path/to/ccs_lvf.db"
set LIBRARY(ccs_power) "/path/to/ccs_power.db"

# Physical Libraries
set LIBRARY(milkyway) "/path/to/milkyway_lib"
set LIBRARY(ndm) "/path/to/ndm_lib"
```

## Usage
Source this TCL file in your EDA tool to set up all library paths consistently.