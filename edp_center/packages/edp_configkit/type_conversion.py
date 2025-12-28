#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Type conversion functions for Tcl interpreter to Python dictionary conversion.
Handles conversion of values based on type information stored in Tcl interpreter.
"""

from tkinter import Tcl
from typing import Any

from .value_format import value_format_tcl2py, value_format_tcl2py_list_item


def get_var_type(interp: Tcl, var_name: str, idx: str = None, has_type_info: bool = True) -> str:
    """
    Get the type of a variable from type information stored in Tcl interpreter.
    
    Args:
        interp: Tcl interpreter containing type information
        var_name: Variable name
        idx: Optional array index
        has_type_info: Whether type information is available
        
    Returns:
        Type string: "bool", "none", "number", "list", "string", or "unknown"
    """
    if not has_type_info:
        return "unknown"

    type_key = var_name
    if idx is not None:
        type_key = f"{var_name}({idx})"

    try:
        return interp.eval(f"set __configkit_types__({type_key})")
    except Exception:
        return "unknown"


def convert_list_element(interp: Tcl, item: str, list_name: str, index: int, has_type_info: bool) -> Any:
    """
    Convert a list element using its type information if available.
    
    Args:
        interp: Tcl interpreter containing type information
        item: List element as string
        list_name: Name of the list variable
        index: Index of the element in the list
        has_type_info: Whether type information is available
        
    Returns:
        Converted Python value
    """
    if has_type_info:
        try:
            # Use comma-separated format: list_name,0, list_name,1, etc.
            element_type = interp.eval(f"set __configkit_types__({list_name},{index})")
            if element_type == "bool":
                return item == "1" or item.lower() == "true"
            elif element_type == "none":
                return None
            elif element_type == "number":
                try:
                    if '.' in item:
                        return float(item)
                    else:
                        return int(item)
                except ValueError:
                    return item
            elif element_type == "list":
                # Nested list - need to parse it as a list and convert each element recursively
                # The item might be in format like "{a b}" or "[list a b]" or "{} {}" (for empty strings)
                temp_interp = Tcl()
                try:
                    # Try different formats
                    if item.startswith("[list ") and item.endswith("]"):
                        # It's an explicit list format
                        result = temp_interp.eval(f"return {item}")
                        parsed = temp_interp.splitlist(result)
                    elif item.startswith("{") and item.endswith("}"):
                        # It's a braced list, parse it
                        # Try to evaluate it as a Tcl list first
                        try:
                            result = temp_interp.eval(f"return {item}")
                            parsed = temp_interp.splitlist(result)
                        except Exception:
                            # If eval fails, use splitlist directly on the item
                            # splitlist handles braced lists correctly
                            parsed = temp_interp.splitlist(item)
                    else:
                        # It's a space-separated string like "a b" or "{} {}"
                        # Parse it as a list
                        parsed = temp_interp.splitlist(item)
                    
                    # Recursively convert each element using type information
                    # Check if we have type info for nested list elements
                    nested_list_name = f"{list_name},{index}"
                    return [convert_list_element(interp, elem, nested_list_name, i, has_type_info) 
                           for i, elem in enumerate(parsed)]
                except Exception as e:
                    # If parsing fails, return as string
                    return item
            else:  # string
                # For strings, return as-is (don't try to convert to number)
                # Use list item converter to handle empty strings correctly
                # Empty string should be preserved as empty string, not None
                if item == '' or item == '{}' or item == '""':
                    return ""
                return item
        except Exception:
            # If type info not found, fall back to standard conversion
            return value_format_tcl2py_list_item(item)
    else:
        # No type information, use standard list item conversion
        return value_format_tcl2py_list_item(item)


def convert_value(interp: Tcl, value: str, var_type: str, var_name: str = "", 
                 mode: str = "auto", has_type_info: bool = True) -> Any:
    """
    Convert a Tcl value to Python based on type information and mode.
    
    Args:
        interp: Tcl interpreter containing type information
        value: Tcl value as string
        var_type: Type of the variable from type information
        var_name: Name of the variable (for hints)
        mode: Conversion mode: "auto", "str", or "list"
        has_type_info: Whether type information is available
        
    Returns:
        Converted Python value
    """
    # If we have explicit type information, use it
    if var_type != "unknown":
        if var_type == "list":
            # It's a list, split by spaces and convert each item using type information
            if value.startswith("[list ") and value.endswith("]"):
                # Already in list format
                result = interp.eval(f"return {value}")
                items = interp.splitlist(result)
                return [convert_list_element(interp, item, var_name, i, has_type_info) 
                       for i, item in enumerate(items)]
            elif value.startswith("{") and value.endswith("}"):
                # Braced string - could contain multiple braced items like "{a b} {c d}"
                # Use Tcl's splitlist to properly parse it (it handles nested braces correctly)
                try:
                    items = interp.splitlist(value)
                    return [convert_list_element(interp, item, var_name, i, has_type_info) 
                           for i, item in enumerate(items)]
                except Exception:
                    # Fallback: try removing outer braces and splitting
                    items = interp.splitlist(value[1:-1])
                    return [convert_list_element(interp, item, var_name, i, has_type_info) 
                           for i, item in enumerate(items)]
            else:
                # Regular space-separated list
                items = interp.splitlist(value)
                return [convert_list_element(interp, item, var_name, i, has_type_info) 
                       for i, item in enumerate(items)]
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
            # For string type, use value_format_tcl2py to handle empty strings correctly
            if value == "" or value == '""' or value == '{}':
                return ""
            return value

    # No explicit type information, use mode to determine behavior
    if mode == "str":
        # Always treat as string
        # Handle empty string explicitly
        if value == "" or value == '""' or value == '{}':
            return ""
        return value
    elif mode == "list":
        # Always convert space-separated values to lists
        if " " in value and not (value.startswith("{") and value.endswith("}")):
            items = interp.splitlist(value)
            return [value_format_tcl2py_list_item(item) for item in items]
        else:
            return value_format_tcl2py(value)
    else:  # mode == "auto" or any other value
        # Try to make a best guess
        # 1. If it's already in Tcl list format, convert it
        if value.startswith("[list ") and value.endswith("]"):
            result = interp.eval(f"return {value}")
            return [value_format_tcl2py_list_item(item) for item in interp.splitlist(result)]

        # 2. If it's a braced string, keep it as a string
        if value.startswith("{") and value.endswith("}"):
            return value[1:-1]  # Remove braces

        # 3. If it doesn't contain spaces, convert normally
        if " " not in value:
            # Handle empty string explicitly before calling value_format_tcl2py
            if value == "" or value == '""' or value == '{}':
                return ""
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

