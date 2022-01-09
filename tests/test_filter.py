import unittest
from src.filter import Filter
import math
import random
import re


class TestFilter(unittest.TestCase):
    def test_filterlength(self):
        test = ['apple', 'ban', 'c', 'delta', 'errantry', 'fox', 'git', 'hippopotamus', 'indigo', 'jumpstart my car']

        self.assertEqual(sum([Filter.filter_length(3, 3, word) for word in test]), 3)
        self.assertEqual(sum([Filter.filter_length(0, 0, word) for word in test]), 0)
        self.assertEqual(sum([Filter.filter_length(0, 1, word) for word in test]), 1)
        self.assertEqual(sum([Filter.filter_length(0, 100, word) for word in test]), 10)
        self.assertEqual(sum([Filter.filter_length(-1, math.pi, word) for word in test]), 4)
        self.assertEqual(sum([Filter.filter_length(15, 17, word) for word in test]), 1)

    def test_filtercharset(self):
        # Check functionality with strings
        self.assertTrue(Filter.filter_charset('', ''))
        self.assertTrue(Filter.filter_charset('abc', 'cbcbbbabcbabc'))
        self.assertFalse(Filter.filter_charset('abc', 'abcabcba '))

        # Check functionality with lists
        self.assertTrue(Filter.filter_charset(['', '', ''], ''))
        self.assertTrue(Filter.filter_charset(['a', 'b', 'c'], 'cbcbbbabcbabc'))
        self.assertFalse(Filter.filter_charset(['a', 'b', 'c'], 'abcabcbaA'))

        # Test special characters
        hiragana = "あぃいぅうぇえぉおかがきぎくぐけげこごさざしじすずせぜそぞただちぢっつづてでとどなにぬねのはばぱひびぴふぶぷへべぺほぼぽまみむめもゃやゅゆょよらりるれろゎわゐゑをん"
        self.assertTrue(Filter.filter_charset(hiragana, "ひらがなでかいてるいくぜぇぇぇぇなにそれうおおお"))
        self.assertFalse(Filter.filter_charset(hiragana, "おぉこんかいもひらがなでかいてるけどもう漢字があるおっす"))

        # Make up 100 random words and ensure they all pass
        self.assertTrue(
            all([Filter.filter_charset(hiragana, "".join(random.choices(hiragana, k=20))) for _ in range(100)])
        )

    def test_filter_regex(self):
        password = "Mypassword69!"
        other_password = "pass!Word"

        # Password ends in special character
        self.assertTrue(Filter.filter_regex(r"[^A-Za-z0-9]{1}$", password))
        self.assertFalse(Filter.filter_regex(r"[^A-Za-z0-9]{1}$", other_password))

        # Password starts in uppercase character
        self.assertTrue(Filter.filter_regex(r"^[A-Z]{1}", password))
        self.assertFalse(Filter.filter_regex(r"^[A-Z]{1}", other_password))

        # Numbers are present
        self.assertTrue(Filter.filter_regex(r"[0-9]", password))
        self.assertFalse(Filter.filter_regex(r"[0-9]", other_password))

        # There are no z's
        self.assertFalse(Filter.filter_regex(r"z", password))

        # There is an o
        self.assertTrue(Filter.filter_regex(r"o", password))

        # Accepts compiled patterns
        self.assertTrue(Filter.filter_regex(re.compile(r"^[A-Z][a-z]+[0-9]{2}[^A-Za-z0-9]$"), password))

    def test_filter_std(self):
        # Test escaping
        self.assertTrue(Filter.filter_std("\\\\\\\\.", "\\\\a"))

        self.assertTrue(Filter.filter_std(".\\..", "a.c"))
        self.assertFalse(Filter.filter_std(".\\..", "abc"))

        # Other tests
        self.assertTrue(Filter.filter_std(".....", "a1!s["))
        self.assertFalse(Filter.filter_std(".....", "a1!s"))

        self.assertTrue(Filter.filter_std(".\\\\#^%&", "a\\1Az!"))
