#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Dictionary operations for configkit.
Provides functions for merging dictionaries and loading files into dictionaries.
"""

import os
import yaml
from typing import Dict

# Import from other modules (avoid circular imports)
# Note: tcl_interp imports are done at function level to avoid circular dependency


def merge_dict(dict1: Dict, dict2: Dict) -> Dict:
    """
    Recursively merge two dictionaries. If there are conflicts, values from dict2 will override dict1.
    For lists, values are appended rather than replaced.

    Args:
        dict1: First dictionary
        dict2: Second dictionary to merge into dict1

    Returns:
        Merged dictionary
    """
    result = dict1.copy()

    for key, value in dict2.items():
        if key in result:
            if isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dictionaries
                result[key] = merge_dict(result[key], value)
            elif isinstance(result[key], list) and isinstance(value, list):
                # For lists, append items from dict2 to dict1
                result[key] = result[key] + value
            else:
                # For other types, dict2 values override dict1
                result[key] = value
        else:
            # Key doesn't exist in dict1, just add it
            result[key] = value

    return result


def yamlfiles2dict(*yaml_files: str, expand_variables: bool = True) -> Dict:
    """
    Convert one or more YAML files to a merged dictionary.
    Supports variable references like $var or ${var} in YAML values.

    Args:
        *yaml_files: One or more paths to YAML files
        expand_variables: Whether to expand variable references (e.g., $a, ${a}) in YAML values.
                         If True, variables defined earlier in the same file or in previous files
                         will be expanded. Default is True.

    Returns:
        Dictionary containing merged content from all YAML files

    Raises:
        FileNotFoundError: If any of the YAML files doesn't exist
        yaml.YAMLError: If there's an error parsing any YAML file
    """
    result = {}

    for yaml_file in yaml_files:
        if not os.path.exists(yaml_file):
            raise FileNotFoundError(f"YAML file not found: {yaml_file}")

        with open(yaml_file, 'r', encoding='utf-8') as f:
            yaml_dict = yaml.safe_load(f)
            if yaml_dict:  # Handle empty YAML files
                # If variable expansion is enabled, convert to Tcl interpreter first
                # to leverage Tcl's variable substitution mechanism
                if expand_variables:
                    from .tcl_interp import dict2tclinterp, tclinterp2dict, expand_variable_references
                    
                    # Convert current result to Tcl interpreter
                    interp = dict2tclinterp(result)
                    
                    # Add new YAML content to interpreter
                    new_interp = dict2tclinterp(yaml_dict, interp=interp)
                    
                    # Expand variable references
                    expand_variable_references(new_interp)
                    
                    # Convert back to dictionary
                    result = tclinterp2dict(new_interp)
                else:
                    # No variable expansion, just merge
                    result = merge_dict(result, yaml_dict)

    return result


def files2dict(*input_files: str, mode: str = "auto", skip_errors: bool = False) -> Dict:
    """
    Convert a mixed list of YAML and Tcl files to a single Python dictionary.
    Files are processed in order and merged into a single dictionary.

    Args:
        *input_files: One or more paths to YAML or Tcl files
        mode: Conversion mode for Tcl values ("auto", "str", or "list")
        skip_errors: Whether to skip files that cause errors (True) or raise exceptions (False)

    Returns:
        Dictionary containing merged content from all input files

    Raises:
        FileNotFoundError: If any of the input files doesn't exist and skip_errors is False
        ValueError: If no input files are provided
        Exception: Various exceptions from file processing if skip_errors is False
    """
    if not input_files:
        raise ValueError("At least one input file must be provided")

    # Initialize an empty result dictionary
    result_dict = {}

    # Process each input file and merge into the result dictionary
    for input_file in input_files:
        try:
            if not os.path.exists(input_file):
                if skip_errors:
                    continue
                else:
                    raise FileNotFoundError(f"Input file not found: {input_file}")

            # Determine file type based on extension
            file_ext = os.path.splitext(input_file)[1].lower()

            # Process based on file type
            if file_ext in ('.yaml', '.yml'):
                # Handle YAML file
                with open(input_file, 'r', encoding='utf-8') as yf:
                    yaml_dict = yaml.safe_load(yf)

                if yaml_dict:  # Skip empty YAML files
                    result_dict = merge_dict(result_dict, yaml_dict)

            elif file_ext in ('.tcl', '.tk'):
                # Handle Tcl file
                # Import here to avoid circular dependency
                from .tcl_interp import tclfiles2tclinterp, tclinterp2dict
                
                # Load the Tcl file into an interpreter
                interp = tclfiles2tclinterp(input_file)

                # Convert to dictionary
                tcl_dict = tclinterp2dict(interp, mode=mode)

                # Merge with result
                result_dict = merge_dict(result_dict, tcl_dict)
        except Exception as e:
            if not skip_errors:
                raise

    return result_dict

