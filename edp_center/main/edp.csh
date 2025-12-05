#!/bin/tcsh
# 
# EDP Main wrapper script for csh/tcsh users
# The real script is in the same directory as the linked shell script
# ref: edp_center/main/cli.py

# Find the directory where this script is located
set srcdir=`readlink -e $0 | xargs dirname`
set srcfile=${srcdir}/edp.py

# Execute file
# Default py path: use environment variable or system python3
# Users can set EDP_PYTHON_PATH environment variable to use specific Python interpreter
# Example: setenv EDP_PYTHON_PATH /usrhome/chenanping/tools/python3.9.16/bin/python3.9

if ( $?EDP_PYTHON_PATH ) then
    # Use user-specified Python path
    set python_path=$EDP_PYTHON_PATH
else
    # Try common Python paths
    if ( -f /usr/bin/python3 ) then
        set python_path=/usr/bin/python3
    else if ( -f /usr/local/bin/python3 ) then
        set python_path=/usr/local/bin/python3
    else
        set python_path=python3
    endif
endif

# Execute the Python script
${python_path} ${srcfile} $*

