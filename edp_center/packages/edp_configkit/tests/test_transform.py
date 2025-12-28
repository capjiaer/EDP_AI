#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for configkit transform functions.
"""

import os
import tempfile
import unittest
import yaml
from tkinter import Tcl

from edp_center.packages.edp_configkit import (
    merge_dict,
    yamlfiles2dict,
    value_format_py2tcl,
    value_format_tcl2py,
    dict2tclinterp,
    tclinterp2tclfile,
    tclfiles2tclinterp,
    tclinterp2dict,
    tclfiles2yamlfile,
    yamlfiles2tclfile,
    files2tclfile,
    files2yamlfile,
    files2dict
)

class TestMergeDict(unittest.TestCase):
    """Tests for merge_dict function."""

    def test_merge_simple_dicts(self):
        """Test merging simple dictionaries."""
        dict1 = {'a': 1, 'b': 2}
        dict2 = {'b': 3, 'c': 4}
        result = merge_dict(dict1, dict2)
        self.assertEqual(result, {'a': 1, 'b': 3, 'c': 4})

    def test_merge_nested_dicts(self):
        """Test merging nested dictionaries."""
        dict1 = {'a': 1, 'b': {'c': 2, 'd': 3}}
        dict2 = {'b': {'c': 4, 'e': 5}, 'f': 6}
        result = merge_dict(dict1, dict2)
        self.assertEqual(result, {'a': 1, 'b': {'c': 4, 'd': 3, 'e': 5}, 'f': 6})

    def test_merge_lists(self):
        """Test merging lists in dictionaries."""
        dict1 = {'a': [1, 2], 'b': 3}
        dict2 = {'a': [3, 4], 'c': 5}
        result = merge_dict(dict1, dict2)
        self.assertEqual(result, {'a': [1, 2, 3, 4], 'b': 3, 'c': 5})

class TestValueFormat(unittest.TestCase):
    """Tests for value_format_py2tcl and value_format_tcl2py functions."""

    def test_py2tcl_basic_types(self):
        """Test converting basic Python types to Tcl."""
        self.assertEqual(value_format_py2tcl(None), '""')
        self.assertEqual(value_format_py2tcl(True), '1')
        self.assertEqual(value_format_py2tcl(False), '0')
        self.assertEqual(value_format_py2tcl(42), '42')
        self.assertEqual(value_format_py2tcl(3.14), '3.14')
        self.assertEqual(value_format_py2tcl("hello"), 'hello')
        self.assertEqual(value_format_py2tcl("hello world"), '{hello world}')

    def test_py2tcl_lists(self):
        """Test converting Python lists to Tcl."""
        self.assertEqual(value_format_py2tcl([1, 2, 3]), '[list 1 2 3]')
        self.assertEqual(value_format_py2tcl(["a", "b", "c"]), '[list a b c]')
        self.assertEqual(value_format_py2tcl(["hello world", 42]), '[list {hello world} 42]')

    def test_tcl2py_basic_types(self):
        """Test converting Tcl values to Python basic types."""
        self.assertIsNone(value_format_tcl2py('""'))
        self.assertEqual(value_format_tcl2py('1'), 1)
        self.assertEqual(value_format_tcl2py('0'), 0)
        self.assertEqual(value_format_tcl2py('42'), 42)
        self.assertEqual(value_format_tcl2py('3.14'), 3.14)
        self.assertEqual(value_format_tcl2py('hello'), 'hello')
        self.assertEqual(value_format_tcl2py('{hello world}'), '{hello world}')

    def test_tcl2py_lists(self):
        """Test converting Tcl lists to Python."""
        self.assertEqual(value_format_tcl2py('[list 1 2 3]'), [1, 2, 3])
        self.assertEqual(value_format_tcl2py('[list a b c]'), ['a', 'b', 'c'])

class TestDictTclInterp(unittest.TestCase):
    """Tests for dict2tclinterp and tclinterp2dict functions."""

    def test_dict_to_tclinterp_simple(self):
        """Test converting a simple dictionary to Tcl interpreter."""
        test_dict = {'a': 1, 'b': 'hello', 'c': True}
        interp = dict2tclinterp(test_dict)

        self.assertEqual(interp.eval('set a'), '1')
        self.assertEqual(interp.eval('set b'), 'hello')
        self.assertEqual(interp.eval('set c'), '1')

    def test_dict_to_tclinterp_nested(self):
        """Test converting a nested dictionary to Tcl interpreter."""
        test_dict = {'a': {'b': 1, 'c': {'d': 2}}}
        interp = dict2tclinterp(test_dict)

        self.assertEqual(interp.eval('set a(b)'), '1')
        self.assertEqual(interp.eval('set a(c,d)'), '2')

    def test_tclinterp_to_dict_simple(self):
        """Test converting Tcl interpreter to a simple dictionary."""
        interp = Tcl()
        interp.eval('set a 1')
        interp.eval('set b hello')
        interp.eval('set c 1')

        result = tclinterp2dict(interp)
        self.assertEqual(result, {'a': 1, 'b': 'hello', 'c': 1})

    def test_tclinterp_to_dict_nested(self):
        """Test converting Tcl interpreter with arrays to a nested dictionary."""
        interp = Tcl()
        interp.eval('set a(b) 1')
        interp.eval('set a(c,d) 2')

        result = tclinterp2dict(interp)
        self.assertEqual(result, {'a': {'b': 1, 'c': {'d': 2}}})

    def test_roundtrip(self):
        """Test round-trip conversion: dict -> tclinterp -> dict."""
        test_dict = {
            'simple': 123,
            'string': 'hello',
            'boolean': True,
            'list': [1, 2, 3],
            'nested': {
                'key1': 'value1',
                'key2': {
                    'subkey': 'subvalue'
                }
            }
        }

        interp = dict2tclinterp(test_dict)
        result = tclinterp2dict(interp)

        # Check that the round-trip preserves the structure and values
        self.assertEqual(result['simple'], test_dict['simple'])
        self.assertEqual(result['string'], test_dict['string'])
        self.assertEqual(result['boolean'], test_dict['boolean'])
        self.assertEqual(result['list'], test_dict['list'])
        self.assertEqual(result['nested']['key1'], test_dict['nested']['key1'])
        self.assertEqual(result['nested']['key2']['subkey'], test_dict['nested']['key2']['subkey'])

class TestTclFile(unittest.TestCase):
    """Tests for tclinterp2tclfile and tclfiles2tclinterp functions."""

    def test_tclinterp_to_tclfile(self):
        """Test exporting Tcl interpreter to a file."""
        interp = Tcl()
        interp.eval('set a 1')
        interp.eval('set b hello')
        interp.eval('set c(d) 2')

        with tempfile.NamedTemporaryFile(suffix='.tcl', delete=False) as temp:
            temp_path = temp.name

        try:
            tclinterp2tclfile(interp, temp_path)

            # Check that the file exists and has content
            self.assertTrue(os.path.exists(temp_path))
            with open(temp_path, 'r') as f:
                content = f.read()
                self.assertIn('set a 1', content)
                self.assertIn('set b hello', content)
                self.assertIn('set c(d) 2', content)
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_tclfiles_to_tclinterp(self):
        """Test loading Tcl file into an interpreter."""
        # Create a test Tcl file
        with tempfile.NamedTemporaryFile(suffix='.tcl', delete=False) as temp:
            temp.write(b"set a 1\nset b hello\nset c(d) 2\n")
            temp_path = temp.name

        try:
            interp = tclfiles2tclinterp(temp_path)

            # Check that variables were loaded correctly
            self.assertEqual(interp.eval('set a'), '1')
            self.assertEqual(interp.eval('set b'), 'hello')
            self.assertEqual(interp.eval('set c(d)'), '2')
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_roundtrip_file(self):
        """Test round-trip: dict -> tclinterp -> tclfile -> tclinterp -> dict."""
        test_dict = {
            'a': 1,
            'b': 'hello',
            'c': {'d': 2}
        }

        with tempfile.NamedTemporaryFile(suffix='.tcl', delete=False) as temp:
            temp_path = temp.name

        try:
            # dict -> tclinterp -> tclfile
            interp1 = dict2tclinterp(test_dict)
            tclinterp2tclfile(interp1, temp_path)

            # tclfile -> tclinterp -> dict
            interp2 = tclfiles2tclinterp(temp_path)
            result = tclinterp2dict(interp2)

            # Check that the round-trip preserves the structure and values
            self.assertEqual(result['a'], test_dict['a'])
            self.assertEqual(result['b'], test_dict['b'])
            self.assertEqual(result['c']['d'], test_dict['c']['d'])
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)

class TestModeParameter(unittest.TestCase):
    """Tests for the mode parameter in tclinterp2dict function."""

    def setUp(self):
        """Set up a Tcl interpreter with test values."""
        self.interp = Tcl()
        self.interp.eval('set numbers {1 2 3}')
        self.interp.eval('set words {apple banana cherry}')
        self.interp.eval('set sentence {This is a sentence}')

    def test_auto_mode(self):
        """Test auto mode for tclinterp2dict."""
        result = tclinterp2dict(self.interp, mode="auto")

        # Numbers should be detected as a list of numbers
        self.assertIsInstance(result['numbers'], list)
        self.assertEqual(result['numbers'], [1, 2, 3])

        # Words should be kept as a string in auto mode
        self.assertIsInstance(result['words'], str)
        self.assertEqual(result['words'], 'apple banana cherry')

        # Sentence should be kept as a string
        self.assertIsInstance(result['sentence'], str)
        self.assertEqual(result['sentence'], 'This is a sentence')

    def test_str_mode(self):
        """Test str mode for tclinterp2dict."""
        result = tclinterp2dict(self.interp, mode="str")

        # All values should be kept as strings
        self.assertIsInstance(result['numbers'], str)
        self.assertEqual(result['numbers'], '1 2 3')

        self.assertIsInstance(result['words'], str)
        self.assertEqual(result['words'], 'apple banana cherry')

        self.assertIsInstance(result['sentence'], str)
        self.assertEqual(result['sentence'], 'This is a sentence')

    def test_list_mode(self):
        """Test list mode for tclinterp2dict."""
        result = tclinterp2dict(self.interp, mode="list")

        # All space-separated values should be converted to lists
        self.assertIsInstance(result['numbers'], list)
        self.assertEqual(result['numbers'], [1, 2, 3])

        self.assertIsInstance(result['words'], list)
        self.assertEqual(result['words'], ['apple', 'banana', 'cherry'])

        self.assertIsInstance(result['sentence'], list)
        self.assertEqual(result['sentence'], ['This', 'is', 'a', 'sentence'])


class TestFileConversions(unittest.TestCase):
    """Tests for file conversion functions: tclfiles2yamlfile and yamlfiles2tclfile."""

    def test_tclfiles2yamlfile(self):
        """Test converting Tcl file to YAML file."""
        # Create a test Tcl file
        with tempfile.NamedTemporaryFile(suffix='.tcl', delete=False) as temp:
            temp.write(b"set a 1\nset b hello\nset c(d) 2\n")
            tcl_path = temp.name

        # Create a temporary YAML file path
        yaml_path = tcl_path + '.yaml'

        try:
            # Convert Tcl to YAML
            tclfiles2yamlfile(tcl_path, output_file=yaml_path)

            # Check that the YAML file exists
            self.assertTrue(os.path.exists(yaml_path))

            # Load the YAML file and check its content
            with open(yaml_path, 'r', encoding='utf-8') as f:
                yaml_content = yaml.safe_load(f)

            # Check the content
            self.assertEqual(yaml_content['a'], 1)
            self.assertEqual(yaml_content['b'], 'hello')
            self.assertEqual(yaml_content['c']['d'], 2)
        finally:
            # Clean up
            if os.path.exists(tcl_path):
                os.remove(tcl_path)
            if os.path.exists(yaml_path):
                os.remove(yaml_path)

    def test_yamlfiles2tclfile(self):
        """Test converting YAML file to Tcl file."""
        # Create a test YAML file
        test_data = {
            'a': 1,
            'b': 'hello',
            'c': {'d': 2},
            'list': [1, 2, 3]
        }

        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False, mode='w', encoding='utf-8') as temp:
            yaml.dump(test_data, temp)
            yaml_path = temp.name

        # Create a temporary Tcl file path
        tcl_path = yaml_path + '.tcl'

        try:
            # Convert YAML to Tcl
            yamlfiles2tclfile(yaml_path, output_file=tcl_path)

            # Check that the Tcl file exists
            self.assertTrue(os.path.exists(tcl_path))

            # Load the Tcl file and check its content
            interp = tclfiles2tclinterp(tcl_path)

            # Check the content
            self.assertEqual(interp.eval('set a'), '1')
            self.assertEqual(interp.eval('set b'), 'hello')
            self.assertEqual(interp.eval('set c(d)'), '2')

            # The list might be represented as space-separated values in Tcl
            list_value = interp.eval('set list')
            # Convert back to Python and check
            list_items = interp.splitlist(list_value)
            self.assertEqual(list(list_items), ['1', '2', '3'])

            # Read the file content and check for source comments
            with open(tcl_path, 'r', encoding='utf-8') as f:
                content = f.read()
                abs_path = os.path.abspath(yaml_path)
                self.assertIn(f"# From {abs_path}", content)
        finally:
            # Clean up
            if os.path.exists(yaml_path):
                os.remove(yaml_path)
            if os.path.exists(tcl_path):
                os.remove(tcl_path)

    def test_yamlfiles2tclfile_multiple_sources(self):
        """Test converting multiple YAML files to a Tcl file with source tracking."""
        # Create first test YAML file
        test_data1 = {
            'a': 1,
            'b': 'hello'
        }

        # Create second test YAML file
        test_data2 = {
            'c': {'d': 2},
            'list': [1, 2, 3]
        }

        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False, mode='w', encoding='utf-8') as temp1:
            yaml.dump(test_data1, temp1)
            yaml_path1 = temp1.name

        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False, mode='w', encoding='utf-8') as temp2:
            yaml.dump(test_data2, temp2)
            yaml_path2 = temp2.name

        # Create a temporary Tcl file path
        tcl_path = yaml_path1 + '.tcl'

        try:
            # Convert YAML to Tcl
            yamlfiles2tclfile(yaml_path1, yaml_path2, output_file=tcl_path)

            # Check that the Tcl file exists
            self.assertTrue(os.path.exists(tcl_path))

            # Load the Tcl file and check its content
            interp = tclfiles2tclinterp(tcl_path)

            # Check the content from both files
            self.assertEqual(interp.eval('set a'), '1')
            self.assertEqual(interp.eval('set b'), 'hello')
            self.assertEqual(interp.eval('set c(d)'), '2')

            # Read the file content and check for source comments
            with open(tcl_path, 'r', encoding='utf-8') as f:
                content = f.read()
                abs_path1 = os.path.abspath(yaml_path1)
                abs_path2 = os.path.abspath(yaml_path2)
                self.assertIn(f"# From {abs_path1}", content)
                self.assertIn(f"# From {abs_path2}", content)
        finally:
            # Clean up
            for path in [yaml_path1, yaml_path2, tcl_path]:
                if os.path.exists(path):
                    os.remove(path)

    def test_yamlfiles2tclfile_empty_file(self):
        """Test converting empty YAML file to Tcl file."""
        # Create an empty YAML file
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False, mode='w', encoding='utf-8') as temp_empty:
            # Don't write anything to the file
            empty_yaml_path = temp_empty.name

        # Create a YAML file with content
        test_data = {
            'a': 1,
            'b': 'hello'
        }

        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False, mode='w', encoding='utf-8') as temp_content:
            yaml.dump(test_data, temp_content)
            content_yaml_path = temp_content.name

        # Create a temporary Tcl file path
        tcl_path = empty_yaml_path + '.tcl'

        try:
            # Convert both YAML files to Tcl
            yamlfiles2tclfile(empty_yaml_path, content_yaml_path, output_file=tcl_path)

            # Check that the Tcl file exists
            self.assertTrue(os.path.exists(tcl_path))

            # Load the Tcl file and check its content
            interp = tclfiles2tclinterp(tcl_path)

            # Check the content (should only have variables from the non-empty file)
            self.assertEqual(interp.eval('set a'), '1')
            self.assertEqual(interp.eval('set b'), 'hello')

            # Read the file content and check for source comments
            with open(tcl_path, 'r', encoding='utf-8') as f:
                content = f.read()
                abs_path_empty = os.path.abspath(empty_yaml_path)
                abs_path_content = os.path.abspath(content_yaml_path)

                # Empty file should have a comment
                self.assertIn(f"# From {abs_path_empty}", content)
                self.assertIn("# (Empty file - no variables defined)", content)

                # Non-empty file should have a comment
                self.assertIn(f"# From {abs_path_content}", content)
        finally:
            # Clean up
            for path in [empty_yaml_path, content_yaml_path, tcl_path]:
                if os.path.exists(path):
                    os.remove(path)

    def test_yamlfiles2tclfile_no_comments(self):
        """Test converting YAML file to Tcl file without source comments."""
        # Create a test YAML file
        test_data = {
            'a': 1,
            'b': 'hello'
        }

        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False, mode='w', encoding='utf-8') as temp:
            yaml.dump(test_data, temp)
            yaml_path = temp.name

        # Create a temporary Tcl file path
        tcl_path = yaml_path + '.tcl'

        try:
            # Convert YAML to Tcl without source comments
            yamlfiles2tclfile(yaml_path, output_file=tcl_path, add_source_comments=False)

            # Check that the Tcl file exists
            self.assertTrue(os.path.exists(tcl_path))

            # Load the Tcl file and check its content
            interp = tclfiles2tclinterp(tcl_path)

            # Check the content
            self.assertEqual(interp.eval('set a'), '1')
            self.assertEqual(interp.eval('set b'), 'hello')

            # Read the file content and check that there are no source comments
            with open(tcl_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertNotIn("# From ", content)
        finally:
            # Clean up
            if os.path.exists(yaml_path):
                os.remove(yaml_path)
            if os.path.exists(tcl_path):
                os.remove(tcl_path)

    def test_roundtrip_yaml_tcl(self):
        """Test round-trip: dict -> yaml -> tcl -> yaml -> dict."""
        test_dict = {
            'simple': 123,
            'string': 'hello',
            'boolean': True,
            'list': [1, 2, 3],
            'nested': {
                'key1': 'value1',
                'key2': {
                    'subkey': 'subvalue'
                }
            }
        }

        # Create temporary file paths
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as temp1:
            yaml_path1 = temp1.name
        with tempfile.NamedTemporaryFile(suffix='.tcl', delete=False) as temp2:
            tcl_path = temp2.name
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False) as temp3:
            yaml_path2 = temp3.name

        try:
            # dict -> yaml
            with open(yaml_path1, 'w', encoding='utf-8') as f:
                yaml.dump(test_dict, f)

            # yaml -> tcl
            yamlfiles2tclfile(yaml_path1, output_file=tcl_path)

            # tcl -> yaml
            tclfiles2yamlfile(tcl_path, output_file=yaml_path2)

            # yaml -> dict
            with open(yaml_path2, 'r', encoding='utf-8') as f:
                result_dict = yaml.safe_load(f)

            # Check that the round-trip preserves the structure and values
            self.assertEqual(result_dict['simple'], test_dict['simple'])
            self.assertEqual(result_dict['string'], test_dict['string'])
            self.assertEqual(result_dict['boolean'], test_dict['boolean'])
            self.assertEqual(result_dict['list'], test_dict['list'])
            self.assertEqual(result_dict['nested']['key1'], test_dict['nested']['key1'])
            self.assertEqual(result_dict['nested']['key2']['subkey'], test_dict['nested']['key2']['subkey'])
        finally:
            # Clean up
            for path in [yaml_path1, tcl_path, yaml_path2]:
                if os.path.exists(path):
                    os.remove(path)


class TestMixedFileConversions(unittest.TestCase):
    """Tests for files2tclfile, files2yamlfile, and files2dict functions."""

    def test_files2tclfile_mixed(self):
        """Test converting mixed YAML and Tcl files to a Tcl file."""
        # Create a YAML file
        yaml_data = {
            'a': 1,
            'b': 'hello'
        }

        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False, mode='w', encoding='utf-8') as yaml_temp:
            yaml.dump(yaml_data, yaml_temp)
            yaml_path = yaml_temp.name

        # Create a Tcl file
        with tempfile.NamedTemporaryFile(suffix='.tcl', delete=False, mode='w', encoding='utf-8') as tcl_temp:
            tcl_temp.write("set c 42\nset d {test string}\n")
            tcl_path = tcl_temp.name

        # Create a temporary output Tcl file path
        output_tcl_path = yaml_path + '.output.tcl'

        try:
            # Convert both files to a single Tcl file
            files2tclfile(yaml_path, tcl_path, output_file=output_tcl_path)

            # Check that the output file exists
            self.assertTrue(os.path.exists(output_tcl_path))

            # Load the output file and check its content
            interp = tclfiles2tclinterp(output_tcl_path)

            # Check content from both input files
            self.assertEqual(interp.eval('set a'), '1')
            self.assertEqual(interp.eval('set b'), 'hello')
            self.assertEqual(interp.eval('set c'), '42')
            self.assertEqual(interp.eval('set d'), 'test string')

            # Read the file content and check for source comments
            with open(output_tcl_path, 'r', encoding='utf-8') as f:
                content = f.read()
                abs_yaml_path = os.path.abspath(yaml_path)
                abs_tcl_path = os.path.abspath(tcl_path)
                self.assertIn(f"# From {abs_yaml_path}", content)
                self.assertIn(f"# From {abs_tcl_path}", content)
        finally:
            # Clean up
            for path in [yaml_path, tcl_path, output_tcl_path]:
                if os.path.exists(path):
                    os.remove(path)

    def test_files2yamlfile_mixed(self):
        """Test converting mixed YAML and Tcl files to a YAML file."""
        # Create a YAML file
        yaml_data = {
            'a': 1,
            'b': 'hello'
        }

        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False, mode='w', encoding='utf-8') as yaml_temp:
            yaml.dump(yaml_data, yaml_temp)
            yaml_path = yaml_temp.name

        # Create a Tcl file
        with tempfile.NamedTemporaryFile(suffix='.tcl', delete=False, mode='w', encoding='utf-8') as tcl_temp:
            tcl_temp.write("set c 42\nset d {test string}\n")
            tcl_path = tcl_temp.name

        # Create a temporary output YAML file path
        output_yaml_path = yaml_path + '.output.yaml'

        try:
            # Convert both files to a single YAML file
            files2yamlfile(yaml_path, tcl_path, output_file=output_yaml_path)

            # Check that the output file exists
            self.assertTrue(os.path.exists(output_yaml_path))

            # Load the output file and check its content
            with open(output_yaml_path, 'r', encoding='utf-8') as f:
                result_dict = yaml.safe_load(f)

            # Check content from both input files
            self.assertEqual(result_dict['a'], 1)
            self.assertEqual(result_dict['b'], 'hello')
            self.assertEqual(result_dict['c'], 42)
            self.assertEqual(result_dict['d'], 'test string')
        finally:
            # Clean up
            for path in [yaml_path, tcl_path, output_yaml_path]:
                if os.path.exists(path):
                    os.remove(path)

    def test_files2tclfile_unknown_extension(self):
        """Test files2tclfile with an unknown file extension."""
        # Create a file with unknown extension
        with tempfile.NamedTemporaryFile(suffix='.unknown', delete=False, mode='w', encoding='utf-8') as unknown_temp:
            unknown_temp.write("This is not a YAML or Tcl file")
            unknown_path = unknown_temp.name

        # Create a YAML file
        yaml_data = {'a': 1}
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False, mode='w', encoding='utf-8') as yaml_temp:
            yaml.dump(yaml_data, yaml_temp)
            yaml_path = yaml_temp.name

        # Create a temporary output Tcl file path
        output_tcl_path = yaml_path + '.output.tcl'

        try:
            # Convert both files to a single Tcl file
            files2tclfile(unknown_path, yaml_path, output_file=output_tcl_path)

            # Check that the output file exists
            self.assertTrue(os.path.exists(output_tcl_path))

            # Load the output file and check its content
            interp = tclfiles2tclinterp(output_tcl_path)

            # Check content from YAML file
            self.assertEqual(interp.eval('set a'), '1')

            # Read the file content and check for unknown extension comment
            with open(output_tcl_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn("# Skipping file with unknown extension: .unknown", content)
        finally:
            # Clean up
            for path in [unknown_path, yaml_path, output_tcl_path]:
                if os.path.exists(path):
                    os.remove(path)

    def test_files2dict_mixed(self):
        """Test converting mixed YAML and Tcl files to a Python dictionary."""
        # Create a YAML file
        yaml_data = {
            'a': 1,
            'b': 'hello'
        }

        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False, mode='w', encoding='utf-8') as yaml_temp:
            yaml.dump(yaml_data, yaml_temp)
            yaml_path = yaml_temp.name

        # Create a Tcl file
        with tempfile.NamedTemporaryFile(suffix='.tcl', delete=False, mode='w', encoding='utf-8') as tcl_temp:
            tcl_temp.write("set c 42\nset d {test string}\n")
            tcl_path = tcl_temp.name

        try:
            # Convert both files to a dictionary
            result_dict = files2dict(yaml_path, tcl_path)

            # Check content from both input files
            self.assertEqual(result_dict['a'], 1)
            self.assertEqual(result_dict['b'], 'hello')
            self.assertEqual(result_dict['c'], 42)
            self.assertEqual(result_dict['d'], 'test string')
        finally:
            # Clean up
            for path in [yaml_path, tcl_path]:
                if os.path.exists(path):
                    os.remove(path)

    def test_files2dict_skip_errors(self):
        """Test files2dict with skip_errors option."""
        # Create a YAML file
        yaml_data = {'a': 1}
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False, mode='w', encoding='utf-8') as yaml_temp:
            yaml.dump(yaml_data, yaml_temp)
            yaml_path = yaml_temp.name

        # Non-existent file path
        nonexistent_path = yaml_path + '.nonexistent'

        try:
            # Test with skip_errors=True
            result_dict = files2dict(nonexistent_path, yaml_path, skip_errors=True)

            # Should only contain content from the existing file
            self.assertEqual(result_dict['a'], 1)
            self.assertEqual(len(result_dict), 1)

            # Test with skip_errors=False (default)
            with self.assertRaises(FileNotFoundError):
                files2dict(nonexistent_path, yaml_path)
        finally:
            # Clean up
            if os.path.exists(yaml_path):
                os.remove(yaml_path)

    def test_files2dict_unknown_extension(self):
        """Test files2dict with an unknown file extension."""
        # Create a file with unknown extension
        with tempfile.NamedTemporaryFile(suffix='.unknown', delete=False, mode='w', encoding='utf-8') as unknown_temp:
            unknown_temp.write("This is not a YAML or Tcl file")
            unknown_path = unknown_temp.name

        # Create a YAML file
        yaml_data = {'a': 1}
        with tempfile.NamedTemporaryFile(suffix='.yaml', delete=False, mode='w', encoding='utf-8') as yaml_temp:
            yaml.dump(yaml_data, yaml_temp)
            yaml_path = yaml_temp.name

        try:
            # Unknown extensions are silently skipped
            result_dict = files2dict(unknown_path, yaml_path)

            # Should only contain content from the YAML file
            self.assertEqual(result_dict['a'], 1)
            self.assertEqual(len(result_dict), 1)
        finally:
            # Clean up
            for path in [unknown_path, yaml_path]:
                if os.path.exists(path):
                    os.remove(path)


if __name__ == '__main__':
    unittest.main()
