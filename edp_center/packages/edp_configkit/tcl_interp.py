#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tcl interpreter conversion functions for configkit.
Provides functions for converting between Python dictionaries and Tcl interpreters.
"""

import os
from tkinter import Tcl
from typing import Dict, List, Any, Optional

from .value_format import value_format_py2tcl, value_format_tcl2py, value_format_tcl2py_list_item, detect_tcl_list
from .type_conversion import get_var_type, convert_list_element, convert_value


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
        elif isinstance(value, list):
            # Handle lists specially - record type for each element
            type_key = name
            if parent_keys:
                type_key = f"{name}({','.join(parent_keys)})"
            
            # Record that this is a list
            interp.eval(f"set __configkit_types__({type_key}) list")
            
            # Convert list to TCL format and record type for each element
            tcl_elements = []
            for i, item in enumerate(value):
                # Record type for each list element
                # Use comma-separated format: list_name,0, list_name,1, etc.
                element_type_key = f"{type_key},{i}"
                if isinstance(item, bool):
                    interp.eval(f"set __configkit_types__({element_type_key}) bool")
                elif item is None:
                    interp.eval(f"set __configkit_types__({element_type_key}) none")
                elif isinstance(item, (int, float)):
                    interp.eval(f"set __configkit_types__({element_type_key}) number")
                elif isinstance(item, list):
                    interp.eval(f"set __configkit_types__({element_type_key}) list")
                    # For nested lists, recursively record type for each nested element
                    # Use format: list_name,0,0 for nested list elements
                    def record_nested_list_types(nested_list, parent_key, depth=0):
                        """Recursively record types for nested list elements"""
                        for j, nested_item in enumerate(nested_list):
                            nested_element_type_key = f"{parent_key},{j}"
                            if isinstance(nested_item, bool):
                                interp.eval(f"set __configkit_types__({nested_element_type_key}) bool")
                            elif nested_item is None:
                                interp.eval(f"set __configkit_types__({nested_element_type_key}) none")
                            elif isinstance(nested_item, (int, float)):
                                interp.eval(f"set __configkit_types__({nested_element_type_key}) number")
                            elif isinstance(nested_item, list):
                                interp.eval(f"set __configkit_types__({nested_element_type_key}) list")
                                # Recursively record deeper nested lists
                                record_nested_list_types(nested_item, nested_element_type_key, depth + 1)
                            else:
                                interp.eval(f"set __configkit_types__({nested_element_type_key}) string")
                    record_nested_list_types(item, element_type_key)
                else:
                    interp.eval(f"set __configkit_types__({element_type_key}) string")
                
                # Convert element to TCL format
                tcl_elements.append(value_format_py2tcl(item))
            
            # Join elements and set the list value
            tcl_value = f"[list {' '.join(tcl_elements)}]"
            
            if not parent_keys:
                # Simple variable
                interp.eval(f"set {name} {tcl_value}")
            else:
                # Array variable with keys joined by commas
                array_indices = ','.join(parent_keys)
                interp.eval(f"set {name}({array_indices}) {tcl_value}")
        else:
            tcl_value = value_format_py2tcl(value)

            # Record type information
            type_key = name
            if parent_keys:
                type_key = f"{name}({','.join(parent_keys)})"

            # Store the Python type
            if isinstance(value, bool):
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
                            # Handle empty string - must use "" or {} to avoid Tcl parsing issues
                            if value == "":
                                f.write(f'set {var}({idx}) ""\n')
                            # Properly quote the value to ensure it's valid Tcl
                            elif ' ' in value or any(c in value for c in '{}[]$"\\'):
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
                    # Handle empty string - must use "" or {} to avoid Tcl parsing issues
                    if value == "":
                        f.write(f'set {var} ""\n')
                    # Properly quote the value to ensure it's valid Tcl
                    elif ' ' in value or any(c in value for c in '{}[]$"\\'):
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
                        # Handle empty string - must use "" or {} to avoid Tcl parsing issues
                        if value == "":
                            file.write(f'set {var}({idx}) ""\n')
                        # Properly quote the value to ensure it's valid Tcl
                        elif ' ' in value or any(c in value for c in '{}[]$"\\'):
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

                # Handle empty string - must use "" or {} to avoid Tcl parsing issues
                if value == "":
                    file.write(f'set {var} ""\n')
                # Properly quote the value to ensure it's valid Tcl
                elif ' ' in value or any(c in value for c in '{}[]$"\\'):
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
            # Sort indices to keep output consistent (list element types after list type)
            type_indices.sort()

            for idx in type_indices:
                try:
                    type_value = interp.eval(f"set __configkit_types__({idx})")
                    # Properly quote both the index and value
                    # Handle indices with commas (list element types like "list_name,0")
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


def expand_variable_references(interp: Tcl) -> None:
    """
    Expand variable references (e.g., $a, ${a}) in Tcl interpreter variables.
    This allows variables defined earlier to be referenced in later values.
    
    Example:
        If interp has: a=1, b="$a"
        After expansion: b="1"
    
    Args:
        interp: Tcl interpreter containing variables to expand
    """
    def expand_single_value(value: str) -> str:
        """Expand variable references in a single value."""
        if '$' not in value:
            return value
        
        # If value is wrapped in braces, remove them before expanding
        value_to_subst = value
        if value.startswith('{') and value.endswith('}') and len(value) > 2:
            value_to_subst = value[1:-1]
        
        try:
            # Use subst with -nocommands and -novariables flags to avoid command substitution
            # But we need variable substitution, so we'll use a safer approach
            # Escape the value properly for Tcl subst command
            # Replace $ with \$ for parts that shouldn't be expanded, then use subst
            # Actually, Tcl's subst will handle ${var} correctly, but $var might be ambiguous
            # We'll use a more careful approach: wrap in braces and use subst
            expanded = interp.eval(f"subst {{{value_to_subst}}}")
            return expanded if expanded != value_to_subst else value
        except (RuntimeError, ValueError, SyntaxError) as e:
            # Tcl execution error (syntax error, variable not found, etc.), return original value
            # This can happen if variable name is ambiguous (e.g., $a_suffix tries to read $a_suffix)
            # In such cases, we should use ${a}_suffix format, but for now return original
            return value
    
    all_vars = interp.eval("info vars").split()
    for var in all_vars:
        if var.startswith("tcl_") or var.startswith("auto_") or var == "__configkit_types__":
            continue
        try:
            # Check if it's an array
            is_array = interp.eval(f"array exists {var}")
            if is_array == "1":
                # Handle array
                indices = interp.eval(f"array names {var}").split()
                for idx in indices:
                    try:
                        value = interp.eval(f"set {var}({idx})")
                        expanded = expand_single_value(value)
                        if expanded != value:
                            interp.eval(f"set {var}({idx}) {{{expanded}}}")
                    except (RuntimeError, ValueError, SyntaxError):
                        # Tcl execution error, skip this variable
                        continue
            else:
                # Handle simple variable
                value = interp.eval(f"set {var}")
                expanded = expand_single_value(value)
                if expanded != value:
                    interp.eval(f"set {var} {{{expanded}}}")
        except (RuntimeError, ValueError, SyntaxError):
            # Tcl execution error, skip this variable
            continue


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
                        var_type = get_var_type(interp, var, idx, has_type_info)

                        # Convert to Python value based on type and mode
                        py_value = convert_value(interp, value, var_type, f"{var}({idx})", mode, has_type_info)

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
                var_type = get_var_type(interp, var, None, has_type_info)
                result[var] = convert_value(interp, value, var_type, var, mode, has_type_info)
            except Exception:
                # Skip variables that can't be accessed
                continue

    return result

