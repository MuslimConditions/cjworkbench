import datetime
import unittest
import pandas as pd
import numpy as np
from server.modules.sortfromtable import SortFromTable
from server.modules.types import ProcessResult


class MockWfModule:
    # A mock module that stores parameter data,
    # for directly testing a module's render() function
    # We can move this into test utils if it's more widely applicable

    def __init__(self, **kwargs):
        self.params = kwargs

    def get_param_raw(self, name, ptype):
        if name in self.params:
            return self.params[name]
        return ''

    def get_param_column(self, name):
        if name in self.params:
            return self.params[name]
        return ''

    def get_param_menu_idx(self, name):
        if name in self.params:
            return self.params[name]
        return ''


class SortFromTableTests(unittest.TestCase):
    # Current dtype choices: "String|Number|Date"
    # Current direction choices: "Select|Ascending|Descending"
    # If the position of the values change, tests will need to be updated

    # NaN and NaT always appear last as the policy in SortFromTable dictates

    def test_order_missing_direction(self):
        table = pd.DataFrame({'A': ['a', 'c', 'b'], 'B': [1, 2, 3]})
        # no-op because no direction is specified
        # TODO nix the very _possibility_ of no direction. Why would anybody
        # ever want to sort by no direction?
        wf_module = MockWfModule(column='A', dtype=0, direction=0)
        result = SortFromTable.render(wf_module, table)
        expected = ProcessResult(
            pd.DataFrame({'A': ['a', 'c', 'b'], 'B': [1, 2, 3]})
        )
        self.assertEqual(result, expected)

    def test_order_str_as_str_ascending(self):
        table = pd.DataFrame({'A': ['a', 'c', 'b'], 'B': [1, 2, 3]})
        wf_module = MockWfModule(column='A', dtype=0, direction=1)
        result = SortFromTable.render(wf_module, table)
        expected = ProcessResult(
            pd.DataFrame({'A': ['a', 'b', 'c'], 'B': [1, 3, 2]})
        )
        self.assertEqual(result, expected)

    def test_order_cat_str_as_str_ascending(self):
        table = pd.DataFrame({'A': ['a', 'c', 'b'], 'B': [1, 2, 3]})
        table['A'] = table['A'].astype('category')
        wf_module = MockWfModule(column='A', dtype=0, direction=1)
        result = SortFromTable.render(wf_module, table)
        expected = ProcessResult(
            pd.DataFrame({'A': ['a', 'b', 'c'], 'B': [1, 3, 2]})
        )
        expected.dataframe['A'] = expected.dataframe['A'].astype('category')
        self.assertEqual(result, expected)

    def test_order_str_as_str_descending(self):
        table = pd.DataFrame({'A': ['a', 'c', 'b'], 'B': [1, 2, 3]})
        wf_module = MockWfModule(column='A', dtype=0, direction=2)
        result = SortFromTable.render(wf_module, table)
        expected = ProcessResult(
            pd.DataFrame({'A': ['c', 'b', 'a'], 'B': [2, 3, 1]})
        )
        self.assertEqual(result, expected)

    def test_order_number_as_str(self):
        table = pd.DataFrame({'A': ['a', 'b', 'c'], 'B': [1, 3, 22]})
        wf_module = MockWfModule(column='B', dtype=0, direction=1)
        result = SortFromTable.render(wf_module, table)
        expected = ProcessResult(
            pd.DataFrame({'A': ['a', 'c', 'b'], 'B': [1, 22, 3]})
        )
        self.assertEqual(result, expected)

    def test_order_number_as_number_ascending(self):
        table = pd.DataFrame({'A': [3.0, np.nan, 2.1], 'B': ['a', 'b', 'c']})
        wf_module = MockWfModule(column='A', dtype=1, direction=1)
        result = SortFromTable.render(wf_module, table)
        expected = ProcessResult(
            pd.DataFrame({'A': [2.1, 3.0, np.nan], 'B': ['c', 'a', 'b']})
        )
        self.assertEqual(result, expected)

    def test_order_number_as_number_descending(self):
        table = pd.DataFrame({'A': [3.0, np.nan, 2.1], 'B': ['a', 'b', 'c']})
        wf_module = MockWfModule(column='A', dtype=1, direction=2)
        result = SortFromTable.render(wf_module, table)
        expected = ProcessResult(
            pd.DataFrame({'A': [3.0, 2.1, np.nan], 'B': ['a', 'c', 'b']})
        )
        self.assertEqual(result, expected)

    def test_order_str_as_number(self):
        table = pd.DataFrame({'A': ['30', '..nan', '4'], 'B': ['a', 'b', 'c']})
        wf_module = MockWfModule(column='A', dtype=1, direction=1)
        result = SortFromTable.render(wf_module, table)
        expected = ProcessResult(
            pd.DataFrame({'A': ['4', '30', '..nan'], 'B': ['c', 'a', 'b']})
        )
        self.assertEqual(result, expected)

    def test_order_date(self):
        d1 = datetime.datetime(2018, 8, 15, 1, 23, 45)
        d2 = datetime.datetime(2018, 8, 15, 1, 34, 56)
        table = pd.DataFrame({'A': [d2, d1], 'B': ['a', 'b']})
        wf_module = MockWfModule(column='A', dtype=2, direction=1)
        result = SortFromTable.render(wf_module, table)
        expected = ProcessResult(
            pd.DataFrame({'A': [d1, d2], 'B': ['b', 'a']})
        )
        self.assertEqual(result, expected)
