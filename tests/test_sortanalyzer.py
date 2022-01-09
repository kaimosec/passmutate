import unittest
from src.sortanalyzer import SortAnalyzer


class TestSortAnalyzer(unittest.TestCase):
    def test_sortanalyzer(self):
        anal = SortAnalyzer()

        lst = [
            'apple',
            'banana',
            'durian',
            'cherry',
            'fig',
            'hackberry',
            'grape'
        ]

        for line in lst:
            anal.check_line(line)

        self.assertEqual(7, anal.lines_checked)
        self.assertEqual(2, anal.discrepancy_count)
        self.assertEqual('grape', anal.last_weight)
        self.assertEqual(5/7, anal.get_accuracy())
