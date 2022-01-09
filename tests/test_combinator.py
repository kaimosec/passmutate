import unittest
import src.combinator as combinator


class TestCombinator(unittest.TestCase):
    @staticmethod
    def check_combinations(expected, result):
        """Compares a list against another list while being order-insensitive"""
        for r in result:
            # Expected ran out before result did
            if len(expected) == 0:
                return False
            if r not in expected:
                return False
            expected.remove(r)

        # Not all results were matched to expecteds
        if len(expected) > 0:
            return False

        return True

    def test_getpossibilities(self):
        test = [
            ['a', 'b'],
            ['c'],
            ['d']
        ]

        expect = [
            ['a'],
            ['b'],
            ['c'],
            ['d'],
            ['a', 'c'],
            ['b', 'c'],
            ['a', 'd'],
            ['b', 'd'],
            ['c', 'a'],
            ['c', 'b'],
            ['c', 'd'],
            ['d', 'a'],
            ['d', 'b'],
            ['d', 'c'],
            ['a', 'c', 'd'],
            ['b', 'c', 'd'],
            ['a', 'd', 'c'],
            ['b', 'd', 'c'],
            ['c', 'a', 'd'],
            ['c', 'b', 'd'],
            ['c', 'd', 'a'],
            ['c', 'd', 'b'],
            ['d', 'a', 'c'],
            ['d', 'b', 'c'],
            ['d', 'c', 'a'],
            ['d', 'c', 'b']
        ]

        self.assertTrue(TestCombinator.check_combinations(expect, list(combinator.Combinator.getpossibilities(test))))
