import unittest
from src.sorter import Sorter


class TestSorter(unittest.TestCase):
    string_combo_weight = {
        '': (0, 0),
        'a' * 64: (4+16, 0),
        'ABCDEG': (1+8, -1 * 13.589506867179 * 0.025659230223093306),
        'Ass': (2 + 8 + 16, -1 * 0.017491157345 * 0.01221963341099767),  # 26
        'a': (4 + 16, -1 * 0.000341596935 * 0.7680569582912513),  # 20
        'a3': (4 + 16 + 32 + 256, -1 * 0.002398149911 * 0.27592172234832957),  # 308
        'z!': (4 + 16 + 64 + 512, -1 * 0.002398149911 * 0.005859824205273842),  # 596
        'car0us3l': (4 + 16 + 128 + 256, -1 * 20.684642519853 * 0.017599472015839526),  # 404
        'M!lk': (2 + 8 + 16 + 128 + 512, -1 * 0.127366857192 * 4.999850004499865e-05),  # 666
        '12345678': (1024 + 256, -1 * 20.684642519853 * 0.1933541993740188),  # 1280
    }

    def test_get_combo(self):
        for string, result in self.string_combo_weight.items():
            self.assertEqual(result[0], Sorter.get_combo(string))

    def test_sort_weight_alphabet(self):
        sorter = Sorter()
        for string, result in self.string_combo_weight.items():
            self.assertEqual(result[1], sorter.sort_weight_alphabet(string)[0])
