#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Transformation functions for configkit.
Provides functionality to convert between Python dictionaries, YAML files, and Tcl interpreters.
"""

import os
import yaml
from tkinter import Tcl
from typing import Dict, List, Any, Union, Optional


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


def yamlfiles2dict(*yaml_files: str) -> Dict:
    """
    Convert one or more YAML files to a merged dictionary.

    Args:
        *yaml_files: One or more paths to YAML files

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
                result = merge_dict(result, yaml_dict)

    return result


def value_format_py2tcl(value: Any) -> str:
    """
    Convert Python value to Tcl format.

    Args:
        value: Python value to convert

    Returns:
        String representation of the value in Tcl format
    """
    if value is None:
        return '""'
    elif isinstance(value, bool):
        return "1" if value else "0"
    elif isinstance(value, (int, float)):
        return str(value)
    elif isinstance(value, list):
        # Convert list to Tcl list format: [list elem1 elem2 ...]
        elements = [value_format_py2tcl(item) for item in value]
        return f"[list {' '.join(elements)}]"
    elif isinstance(value, dict):
        # For dictionaries, we'll use Tcl's dict create command
        items = []
        for k, v in value.items():
            items.append(f"{value_format_py2tcl(k)} {value_format_py2tcl(v)}")
        return f"[dict create {' '.join(items)}]"
    else:
        # For strings, escape any special characters
        value_str = str(value)
        # If the string contains spaces or special characters, we need to handle it properly
        if any(c in value_str for c in ' \t\n\r{}[]$"\\'):
            # Use braces for complex strings to preserve literal meaning
            return f"{{{value_str}}}"
        return value_str


def detect_tcl_list(tcl_value: str, var_name: str = "") -> bool:
    """
    Detect if a Tcl string value should be interpreted as a list.

    This function checks if a string value from Tcl should be converted to a Python list.
    It looks for patterns like space-separated numbers that likely represent a list.

    Args:
        tcl_value: Tcl value as a string
        var_name: Optional variable name for context-aware detection

    Returns:
        True if the value should be interpreted as a list, False otherwise
    """
    # If it's explicitly a Tcl list, it's already handled elsewhere
    if tcl_value.startswith("[list ") and tcl_value.endswith("]"):
        return False

    # If it's enclosed in braces, it's a complex string, not a list
    if tcl_value.startswith("{") and tcl_value.endswith("}"):
        return False

    # If it doesn't contain spaces, it's not a list
    if " " not in tcl_value:
        return False

    # Variable name hints - if the name suggests it's a list
    list_hint_names = ["list", "array", "items", "elements", "values"]
    is_likely_list_by_name = var_name and any(hint in var_name.lower() for hint in list_hint_names)

    # Split by spaces
    items = tcl_value.split()

    # If all items are numbers, it's likely a list of numbers
    all_numbers = True
    for item in items:
        try:
            float(item)
        except ValueError:
            all_numbers = False
            break

    if all_numbers and len(items) > 1:
        return True

    # Be more conservative with non-numeric items
    # Only consider it a list if the variable name suggests it's a list
    # or if it has a very specific pattern
    if is_likely_list_by_name and len(items) > 1:
        return True

    return False


def value_format_tcl2py(tcl_value: str) -> Any:
    """
    Convert Tcl value to Python format.

    Args:
        tcl_value: Tcl value as a string

    Returns:
        Python representation of the Tcl value
    """
    # Use Tcl interpreter to evaluate and convert the value
    interp = Tcl()

    # Handle empty string
    if not tcl_value or tcl_value == '""':
        return None

    # Try to interpret as a number
    try:
        if '.' in tcl_value:
            return float(tcl_value)
        else:
            return int(tcl_value)
    except ValueError:
        pass

    # Handle boolean values
    if tcl_value == "1" or tcl_value.lower() == "true":
        return True
    elif tcl_value == "0" or tcl_value.lower() == "false":
        return False

    # Handle explicit Tcl lists
    if tcl_value.startswith("[list ") and tcl_value.endswith("]"):
        list_content = tcl_value[6:-1].strip()
        if not list_content:
            return []

        # Use Tcl to properly parse the list
        result = interp.eval(f"return {tcl_value}")
        # Convert the result to a Python list
        return [value_format_tcl2py(item) for item in interp.splitlist(result)]

    # Check if the string value should be interpreted as a list
    if detect_tcl_list(tcl_value):
        # Split the string and convert each item
        items = interp.splitlist(tcl_value)
        return [value_format_tcl2py(item) for item in items]

    # Handle dictionaries
    if tcl_value.startswith("[dict create ") and tcl_value.endswith("]"):
        dict_content = tcl_value[12:-1].strip()
        if not dict_content:
            return {}

        try:
            # Use Tcl to properly parse the dictionary
            result = interp.eval(f"return {tcl_value}")
            # Convert the result to a Python dict
            result_dict = {}
            items = interp.splitlist(result)
            for i in range(0, len(items), 2):
                if i+1 < len(items):
                    key = items[i]
                    value = items[i+1]

                    # Handle nested dictionaries
                    if value.startswith("[dict create ") and value.endswith("]"):
                        py_key = value_format_tcl2py(key)
                        py_value = value_format_tcl2py(value)
                        result_dict[py_key] = py_value
                    else:
                        py_key = value_format_tcl2py(key)
                        py_value = value_format_tcl2py(value)
                        result_dict[py_key] = py_value
            return result_dict
        except Exception:
            # If there's an error parsing the dict, return as string
            return tcl_value

    # For other values, return as string
    return tcl_value


def dict2tclinterp(data: Dict, interp: Optional[Tcl] = None) -> Tcl:
    """
    Convert a Python dictionary to Tcl variables in a Tcl interpreter.
    Also records type information for proper conversion back to Python.

    Args:
        data: Dictionary to convert
        interp: Optional Tcl interpreter to use. If None, a new one will be created.

    Returns:
        Tcl interpreter with variables set
    """
    if interp is None:
        interp = Tcl()

    # Initialize a special array to store type information
    interp.eval("array set __configkit_types__ {}")

    def _set_tcl_var(name: str, value: Any, parent_keys: List[str] = None):
        if parent_keys is None:
            parent_keys = []

        if isinstance(value, dict):
            for k, v in value.items():
                new_keys = parent_keys + [k]
                _set_tcl_var(name, v, new_keys)
        else:
            tcl_value = value_format_py2tcl(value)

            # Record type information
            type_key = name
            if parent_keys:
                type_key = f"{name}({','.join(parent_keys)})"

            # Store the Python type
            if isinstance(value, list):
                interp.eval(f"set __configkit_types__({type_key}) list")
            elif isinstance(value, bool):
                interp.eval(f"set __configkit_types__({type_key}) bool")
            elif value is None:
                interp.eval(f"set __configkit_types__({type_key}) none")
            elif isinstance(value, (int, float)):
                interp.eval(f"set __configkit_types__({type_key}) number")
            else:
                interp.eval(f"set __configkit_types__({type_key}) string")

            if not parent_keys:
                # Simple variable
                interp.eval(f"set {name} {tcl_value}")
            else:
                # Array variable with keys joined by commas
                array_indices = ','.join(parent_keys)
                interp.eval(f"set {name}({array_indices}) {tcl_value}")

    for key, value in data.items():
        _set_tcl_var(key, value)

    return interp


def tclinterp2tclfile(interp: Tcl, output_file: str) -> None:
    """
    Export all variables and arrays from a Tcl interpreter to a Tcl file.
    Also exports type information for proper conversion back to Python.

    Args:
        interp: Tcl interpreter containing variables
        output_file: Path to the output Tcl file

    Returns:
        None
    """
    # Get all global variables
    all_vars = interp.eval("info vars").split()

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Generated by configkit\n\n")

        # First, check if we have type information
        has_type_info = "__configkit_types__" in all_vars and interp.eval("array exists __configkit_types__") == "1"

        # Process regular variables
        for var in all_vars:
            # Skip special Tcl variables and system variables
            if (var.startswith("tcl_") or var.startswith("auto_") or
                var in ["errorInfo", "errorCode", "env", "argv0", "_tkinter_skip_tk_init"]):
                continue

            # Skip our internal type information array (we'll handle it separately)
            if var == "__configkit_types__":
                continue

            # Check if it's an array
            is_array = interp.eval(f"array exists {var}")

            if is_array == "1":
                # Get all array indices
                try:
                    indices = interp.eval(f"array names {var}").split()

                    for idx in indices:
                        try:
                            value = interp.eval(f"set {var}({idx})")
                            # Properly quote the value to ensure it's valid Tcl
                            if ' ' in value or any(c in value for c in '{}[]$"\\'):
                                f.write(f"set {var}({idx}) {{{value}}}\n")
                            else:
                                f.write(f"set {var}({idx}) {value}\n")
                        except Exception:
                            # Skip indices that can't be accessed
                            continue
                except Exception:
                    # Skip arrays that can't be accessed
                    continue
            else:
                # Simple variable
                try:
                    value = interp.eval(f"set {var}")
                    # Properly quote the value to ensure it's valid Tcl
                    if ' ' in value or any(c in value for c in '{}[]$"\\'):
                        f.write(f"set {var} {{{value}}}\n")
                    else:
                        f.write(f"set {var} {value}\n")
                except Exception:
                    # Skip variables that can't be accessed
                    continue

        # Now export type information if available
        if has_type_info:
            f.write("\n# Type information for configkit\n")
            f.write("array set __configkit_types__ {}\n")

            try:
                type_indices = interp.eval("array names __configkit_types__").split()

                for idx in type_indices:
                    try:
                        type_value = interp.eval(f"set __configkit_types__({idx})")
                        # Properly quote both the index and value
                        if ' ' in idx or any(c in idx for c in '{}[]$"\\'):
                            quoted_idx = f"{{{idx}}}"
                        else:
                            quoted_idx = idx

                        f.write(f"set __configkit_types__({quoted_idx}) {type_value}\n")
                    except Exception:
                        continue
            except Exception:
                # If we can't access type information, just skip it
                pass


def files2tclfile(*input_files: str, output_file: str, add_source_comments: bool = True) -> None:
    """
    Convert a mixed list of YAML and Tcl files to a single Tcl file.
    Files are processed in order, with each file's content written sequentially to the output file.

    Args:
        *input_files: One or more paths to YAML or Tcl files
        output_file: Path to the output Tcl file
        add_source_comments: Whether to add comments indicating the source file for each section

    Returns:
        None

    Raises:
        FileNotFoundError: If any of the input files doesn't exist
        ValueError: If no input files are provided
    """
    if not input_files:
        raise ValueError("At least one input file must be provided")

    # Open the output file for writing
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Generated by configkit\n\n")

        # Process each input file sequentially
        for input_file in input_files:
            if not os.path.exists(input_file):
                raise FileNotFoundError(f"Input file not found: {input_file}")

            # Get the absolute path of the file
            abs_path = os.path.abspath(input_file)

            # Determine file type based on extension
            file_ext = os.path.splitext(input_file)[1].lower()

            # Add a comment indicating the source file
            if add_source_comments:
                f.write(f"\n# From {abs_path}\n")

            # Process based on file type
            if file_ext in ('.yaml', '.yml'):
                # Handle YAML file
                with open(input_file, 'r', encoding='utf-8') as yf:
                    yaml_dict = yaml.safe_load(yf)

                if not yaml_dict:  # Handle empty YAML files
                    f.write("# (Empty file - no variables defined)\n")
                    continue

                # Convert dictionary to Tcl interpreter
                interp = dict2tclinterp(yaml_dict)

                # Write all variables from this file
                _write_tcl_vars_to_file(interp, f)

            elif file_ext in ('.tcl', '.tk'):
                # Handle Tcl file
                # Create a new interpreter
                interp = Tcl()

                try:
                    # Source the Tcl file
                    interp.eval(f"source {{{input_file}}}")

                    # Write all variables from this interpreter
                    _write_tcl_vars_to_file(interp, f)

                except Exception as e:
                    f.write(f"# Error loading Tcl file: {str(e)}\n")
            else:
                # Unknown file type
                f.write(f"# Skipping file with unknown extension: {file_ext}\n")


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


def files2yamlfile(*input_files: str, output_file: str, mode: str = "auto") -> None:
    """
    Convert a mixed list of YAML and Tcl files to a single YAML file.
    Files are processed in order and merged into a single dictionary.

    Args:
        *input_files: One or more paths to YAML or Tcl files
        output_file: Path to the output YAML file
        mode: Conversion mode for Tcl values ("auto", "str", or "list")

    Returns:
        None

    Raises:
        FileNotFoundError: If any of the input files doesn't exist
        ValueError: If no input files are provided
    """
    # Convert files to dictionary
    result_dict = files2dict(*input_files, mode=mode)

    # Write the result dictionary to the output YAML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Generated by configkit\n")
        yaml.dump(result_dict, f, default_flow_style=False, sort_keys=False)


# Helper function to write Tcl variables to a file
def _write_tcl_vars_to_file(interp: Tcl, file) -> None:
    """Write all variables from a Tcl interpreter to a file."""
    # Get all global variables
    all_vars = interp.eval("info vars").split()

    # Process regular variables
    for var in all_vars:
        # Skip special Tcl variables and system variables
        if (var.startswith("tcl_") or var.startswith("auto_") or
            var in ["errorInfo", "errorCode", "env", "argv0", "_tkinter_skip_tk_init", "__configkit_types__"]):
            continue

        # Check if it's an array
        is_array = interp.eval(f"array exists {var}")

        if is_array == "1":
            # Get all array indices
            try:
                indices = interp.eval(f"array names {var}").split()

                for idx in indices:
                    try:
                        value = interp.eval(f"set {var}({idx})")
                        # Properly quote the value to ensure it's valid Tcl
                        if ' ' in value or any(c in value for c in '{}[]$"\\'):
                            file.write(f"set {var}({idx}) {{{value}}}\n")
                        else:
                            file.write(f"set {var}({idx}) {value}\n")
                    except Exception:
                        # Skip indices that can't be accessed
                        continue
            except Exception:
                # Skip arrays that can't be accessed
                continue
        else:
            # Simple variable
            try:
                value = interp.eval(f"set {var}")

                # Properly quote the value to ensure it's valid Tcl
                if ' ' in value or any(c in value for c in '{}[]$"\\'):
                    file.write(f"set {var} {{{value}}}\n")
                else:
                    file.write(f"set {var} {value}\n")
            except Exception:
                # Skip variables that can't be accessed
                continue

    # Export type information
    if "__configkit_types__" in all_vars and interp.eval("array exists __configkit_types__") == "1":
        file.write("\n# Type information for configkit\n")
        file.write("array set __configkit_types__ {}\n")

        try:
            type_indices = interp.eval("array names __configkit_types__").split()

            for idx in type_indices:
                try:
                    type_value = interp.eval(f"set __configkit_types__({idx})")
                    # Properly quote both the index and value
                    if ' ' in idx or any(c in idx for c in '{}[]$"\\'):
                        quoted_idx = f"{{{idx}}}"
                    else:
                        quoted_idx = idx

                    file.write(f"set __configkit_types__({quoted_idx}) {type_value}\n")
                except Exception:
                    continue
        except Exception:
            # If we can't access type information, just skip it
            pass


def tclfiles2tclinterp(*tcl_files: str, interp: Optional[Tcl] = None) -> Tcl:
    """
    Load multiple Tcl files into a Tcl interpreter.

    Args:
        *tcl_files: One or more paths to Tcl files
        interp: Optional Tcl interpreter to use. If None, a new one will be created.

    Returns:
        Tcl interpreter with loaded variables

    Raises:
        FileNotFoundError: If any of the Tcl files doesn't exist
    """
    if interp is None:
        interp = Tcl()

    for tcl_file in tcl_files:
        if not os.path.exists(tcl_file):
            raise FileNotFoundError(f"Tcl file not found: {tcl_file}")

        # Use source command to load the file
        interp.eval(f"source {{{tcl_file}}}")

    return interp


def tclinterp2dict(interp: Tcl, mode: str = "auto") -> Dict:
    """
    Convert all variables and arrays from a Tcl interpreter to a Python dictionary.
    Uses type information if available to correctly convert values.

    Args:
        interp: Tcl interpreter containing variables
        mode: Conversion mode for space-separated values without type information:
              - "auto": Use type information if available, otherwise make best guess
              - "str": Always treat space-separated values as strings
              - "list": Always convert space-separated values to lists

    Returns:
        Dictionary representation of Tcl variables
    """
    result = {}

    # Get all global variables
    all_vars = interp.eval("info vars").split()

    # Check if we have type information
    has_type_info = "__configkit_types__" in all_vars and interp.eval("array exists __configkit_types__") == "1"

    # Function to get the type of a variable if available
    def get_var_type(var_name: str, idx: str = None) -> str:
        if not has_type_info:
            return "unknown"

        type_key = var_name
        if idx is not None:
            type_key = f"{var_name}({idx})"

        try:
            return interp.eval(f"set __configkit_types__({type_key})")
        except Exception:
            return "unknown"

    # Function to convert a Tcl value to Python based on type information and mode
    def convert_value(value: str, var_type: str, var_name: str = "") -> Any:
        # If we have explicit type information, use it
        if var_type != "unknown":
            if var_type == "list":
                # It's a list, split by spaces and convert each item
                if value.startswith("[list ") and value.endswith("]"):
                    # Already in list format
                    return value_format_tcl2py(value)
                elif value.startswith("{") and value.endswith("}"):
                    # Braced string, remove braces and split
                    items = interp.splitlist(value[1:-1])
                    return [value_format_tcl2py(item) for item in items]
                else:
                    # Regular space-separated list
                    items = interp.splitlist(value)
                    return [value_format_tcl2py(item) for item in items]
            elif var_type == "bool":
                return value == "1" or value.lower() == "true"
            elif var_type == "none":
                return None
            elif var_type == "number":
                try:
                    if '.' in value:
                        return float(value)
                    else:
                        return int(value)
                except ValueError:
                    return value
            else:  # string or other types
                return value

        # No explicit type information, use mode to determine behavior
        if mode == "str":
            # Always treat as string
            return value
        elif mode == "list":
            # Always convert space-separated values to lists
            if " " in value and not (value.startswith("{") and value.endswith("}")):
                items = interp.splitlist(value)
                return [value_format_tcl2py(item) for item in items]
            else:
                return value_format_tcl2py(value)
        else:  # mode == "auto" or any other value
            # Try to make a best guess
            # 1. If it's already in Tcl list format, convert it
            if value.startswith("[list ") and value.endswith("]"):
                return value_format_tcl2py(value)

            # 2. If it's a braced string, keep it as a string
            if value.startswith("{") and value.endswith("}"):
                return value[1:-1]  # Remove braces

            # 3. If it doesn't contain spaces, convert normally
            if " " not in value:
                return value_format_tcl2py(value)

            # 4. Check if all items are numbers
            items = value.split()
            all_numbers = True
            for item in items:
                try:
                    float(item)
                except ValueError:
                    all_numbers = False
                    break

            if all_numbers and len(items) > 1:
                # Convert to a list of numbers
                return [float(item) if '.' in item else int(item) for item in items]

            # 5. Check if variable name suggests it's a list
            list_hint_names = ["list", "array", "items", "elements", "values"]
            if var_name and any(hint in var_name.lower() for hint in list_hint_names) and len(items) > 1:
                return items

            # 6. Default to string for safety
            return value

    for var in all_vars:
        # Skip special Tcl variables and system variables
        if (var.startswith("tcl_") or var.startswith("auto_") or
            var in ["errorInfo", "errorCode", "env", "argv0", "_tkinter_skip_tk_init", "__configkit_types__"]):
            continue

        # Check if it's an array
        is_array = interp.eval(f"array exists {var}")

        if is_array == "1":
            # Get all array indices
            try:
                indices = interp.eval(f"array names {var}").split()
                var_dict = {}

                for idx in indices:
                    try:
                        # Get the value
                        value = interp.eval(f"set {var}({idx})")

                        # Get the type if available
                        var_type = get_var_type(var, idx)

                        # Convert to Python value based on type and mode
                        py_value = convert_value(value, var_type, f"{var}({idx})")

                        # Handle nested array indices (comma-separated)
                        if ',' in idx:
                            keys = idx.split(',')
                            current = var_dict

                            # Navigate to the nested dictionary
                            for i, key in enumerate(keys):
                                if i == len(keys) - 1:
                                    # Last key, set the value
                                    current[key] = py_value
                                else:
                                    # Create nested dict if needed
                                    if key not in current or not isinstance(current[key], dict):
                                        current[key] = {}
                                    current = current[key]
                        else:
                            var_dict[idx] = py_value
                    except Exception:
                        # Skip indices that can't be accessed
                        continue

                if var_dict:  # Only add if we have values
                    result[var] = var_dict
            except Exception:
                # Skip arrays that can't be accessed
                continue
        else:
            # Simple variable
            try:
                value = interp.eval(f"set {var}")
                var_type = get_var_type(var)
                result[var] = convert_value(value, var_type, var)
            except Exception:
                # Skip variables that can't be accessed
                continue

    return result


def tclfiles2yamlfile(*tcl_files: str, output_file: str, mode: str = "auto") -> None:
    """
    Convert one or more Tcl files to a YAML file.

    Args:
        *tcl_files: One or more paths to Tcl files
        output_file: Path to the output YAML file
        mode: Conversion mode for space-separated values without type information:
              - "auto": Use type information if available, otherwise make best guess
              - "str": Always treat space-separated values as strings
              - "list": Always convert space-separated values to lists

    Returns:
        None

    Raises:
        FileNotFoundError: If any of the Tcl files doesn't exist
    """
    # Load Tcl files into an interpreter
    interp = tclfiles2tclinterp(*tcl_files)

    # Convert interpreter to dictionary
    data = tclinterp2dict(interp, mode=mode)

    # Write dictionary to YAML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Generated by configkit\n")
        yaml.dump(data, f, default_flow_style=False, sort_keys=False)


def yamlfiles2tclfile(*yaml_files: str, output_file: str, add_source_comments: bool = True) -> None:
    """
    Convert one or more YAML files to a Tcl file.
    Each YAML file's content is written sequentially to the Tcl file with source comments.

    Args:
        *yaml_files: One or more paths to YAML files
        output_file: Path to the output Tcl file
        add_source_comments: Whether to add comments indicating the source file for each section

    Returns:
        None

    Raises:
        FileNotFoundError: If any of the YAML files doesn't exist
        yaml.YAMLError: If there's an error parsing any YAML file
    """
    if not yaml_files:
        raise ValueError("At least one YAML file must be provided")

    # Open the output file for writing
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Generated by configkit\n\n")

        # Process each YAML file sequentially
        for yaml_file in yaml_files:
            if not os.path.exists(yaml_file):
                raise FileNotFoundError(f"YAML file not found: {yaml_file}")

            # Get the absolute path of the file
            abs_path = os.path.abspath(yaml_file)

            # Load the YAML file
            with open(yaml_file, 'r', encoding='utf-8') as yf:
                yaml_dict = yaml.safe_load(yf)

            # Add a comment indicating the source file
            if add_source_comments:
                f.write(f"\n# From {abs_path}\n")

            if not yaml_dict:  # Handle empty YAML files
                f.write("# (Empty file - no variables defined)\n")
                continue

            # Convert dictionary to Tcl interpreter
            interp = dict2tclinterp(yaml_dict)

            # Write all variables from this file
            _write_tcl_vars_to_file(interp, f)
