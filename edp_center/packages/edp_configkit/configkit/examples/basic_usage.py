#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Basic usage examples for configkit.
"""

import os
import sys
import tempfile

# Add the parent directory to the path so we can import configkit
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from configkit import (
    dict2tclinterp,
    tclinterp2dict,
    tclinterp2tclfile,
    tclfiles2tclinterp
)

def example_dict_to_tcl():
    """Example of converting a Python dictionary to Tcl and back."""
    print("=== Example: Python Dict -> Tcl -> Python Dict ===")
    
    # Create a test dictionary
    test_dict = {
        "app": {
            "name": "TestApp",
            "version": 1.0,
            "settings": {
                "debug": True,
                "timeout": 30
            },
            "features": ["login", "dashboard", "reports"]
        }
    }
    
    print(f"Original dict: {test_dict}")
    
    # Convert to Tcl interpreter
    interp = dict2tclinterp(test_dict)
    
    # Access some values in Tcl
    app_name = interp.eval("set app(name)")
    app_version = interp.eval("set app(version)")
    debug_setting = interp.eval("set app(settings,debug)")
    features = interp.eval("set app(features)")
    
    print("\nValues in Tcl:")
    print(f"  app(name) = {app_name}")
    print(f"  app(version) = {app_version}")
    print(f"  app(settings,debug) = {debug_setting}")
    print(f"  app(features) = {features}")
    
    # Convert back to Python dictionary
    result_dict = tclinterp2dict(interp)
    print(f"\nRound-trip dict: {result_dict}")
    
    print("\nDone!")

def example_tcl_file():
    """Example of saving and loading Tcl files."""
    print("\n=== Example: Tcl File Operations ===")
    
    # Create a test dictionary
    test_dict = {
        "server": {
            "host": "localhost",
            "port": 8080,
            "ssl": True
        },
        "database": {
            "url": "postgres://user:pass@localhost/db",
            "pool_size": 10
        },
        "logging": {
            "level": "INFO",
            "file": "/var/log/app.log"
        }
    }
    
    # Convert to Tcl interpreter
    interp = dict2tclinterp(test_dict)
    
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix='.tcl', delete=False) as temp:
        temp_path = temp.name
    
    # Save to Tcl file
    tclinterp2tclfile(interp, temp_path)
    print(f"Saved Tcl file to: {temp_path}")
    
    # Read the file content
    with open(temp_path, "r") as f:
        print("\nContent of Tcl file:")
        print(f.read())
    
    # Load the file into a new interpreter
    new_interp = tclfiles2tclinterp(temp_path)
    print("\nSuccessfully loaded Tcl file into a new interpreter")
    
    # Convert back to Python dictionary
    result_dict = tclinterp2dict(new_interp)
    print(f"\nDictionary from Tcl file: {result_dict}")
    
    # Clean up
    os.remove(temp_path)
    print(f"\nRemoved temporary file: {temp_path}")
    
    print("\nDone!")

def example_mode_parameter():
    """Example of using the mode parameter with tclinterp2dict."""
    print("\n=== Example: Mode Parameter ===")
    
    # Create a Tcl interpreter with ambiguous values
    from tkinter import Tcl
    interp = Tcl()
    interp.eval("set numbers {1 2 3 4 5}")
    interp.eval("set words {apple banana cherry}")
    interp.eval("set sentence {This is a sentence with spaces}")
    
    # Convert with different modes
    print("\nWith mode='auto':")
    auto_dict = tclinterp2dict(interp, mode="auto")
    print(f"  numbers: {auto_dict['numbers']} (type: {type(auto_dict['numbers']).__name__})")
    print(f"  words: {auto_dict['words']} (type: {type(auto_dict['words']).__name__})")
    print(f"  sentence: {auto_dict['sentence']} (type: {type(auto_dict['sentence']).__name__})")
    
    print("\nWith mode='str':")
    str_dict = tclinterp2dict(interp, mode="str")
    print(f"  numbers: {str_dict['numbers']} (type: {type(str_dict['numbers']).__name__})")
    print(f"  words: {str_dict['words']} (type: {type(str_dict['words']).__name__})")
    print(f"  sentence: {str_dict['sentence']} (type: {type(str_dict['sentence']).__name__})")
    
    print("\nWith mode='list':")
    list_dict = tclinterp2dict(interp, mode="list")
    print(f"  numbers: {list_dict['numbers']} (type: {type(list_dict['numbers']).__name__})")
    print(f"  words: {list_dict['words']} (type: {type(list_dict['words']).__name__})")
    print(f"  sentence: {list_dict['sentence']} (type: {type(list_dict['sentence']).__name__})")
    
    print("\nDone!")

if __name__ == "__main__":
    example_dict_to_tcl()
    example_tcl_file()
    example_mode_parameter()
