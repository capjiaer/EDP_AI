# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2023-11-15

### Added
- Initial release of ConfigKit
- Core functionality for converting between Python dictionaries, YAML files, and Tcl files/interpreters
- Support for nested structures and complex data types
- Type preservation during conversions
- Source tracking for configuration files
- Comprehensive test suite
- Bilingual documentation (English and Chinese)

### Functions
- `merge_dict`: Merge two dictionaries with nested structure support
- `yamlfiles2dict`: Load one or more YAML files into a Python dictionary
- `value_format_py2tcl`: Convert a Python value to Tcl format
- `value_format_tcl2py`: Convert a Tcl value to Python format
- `dict2tclinterp`: Convert a Python dictionary to a Tcl interpreter
- `tclinterp2dict`: Convert a Tcl interpreter to a Python dictionary
- `tclinterp2tclfile`: Write a Tcl interpreter to a Tcl file
- `tclfiles2tclinterp`: Load one or more Tcl files into a Tcl interpreter
- `tclfiles2yamlfile`: Convert one or more Tcl files to a YAML file
- `yamlfiles2tclfile`: Convert one or more YAML files to a Tcl file
- `files2tclfile`: Convert mixed YAML and Tcl files to a Tcl file
- `files2yamlfile`: Convert mixed YAML and Tcl files to a YAML file
- `files2dict`: Convert mixed YAML and Tcl files to a Python dictionary
