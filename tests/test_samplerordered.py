import unittest
from src.diskutil import DiskUtil
import os
from src.sampler.samplerordered import SamplerOrdered


def get_sampler(lines, pick_num):
    lines = [str(x) + "\n" for x in range(0, lines)]
    filename = DiskUtil.get_unique_filename("/tmp")
    with open(filename, 'w') as file:
        file.writelines(lines)

    sampler = SamplerOrdered(filename, pick_num)

    with open(filename) as file:
        for line in file:
            line = line.strip()
            sampler.process_line(line)

    os.remove(filename)
    return sampler


class TestSamplerOrdered(unittest.TestCase):
    def test_sampleordered(self):
        # Manual check
        sampler = get_sampler(1000, 10)
        self.assertEqual(
            ['0', '100', '200', '300', '400', '500', '600', '700', '800', '900'],
            sampler.get_samples()
        )

        # Automatic checks
        lines_picks_subpicks = [
            (1000, 10, None),
            (1, 1, None),
            (1000, 1, None),
            (1000, 100, 10)
        ]

        for lines, picks, subpicks in lines_picks_subpicks:
            sampler = get_sampler(lines, picks)

            self.assertEqual(lines, sampler.line_count)

            samples = sampler.get_samples()
            self.assertEqual(picks, len(samples))

            if subpicks:
                sub_samples = sampler.get_samples(subpicks)
                self.assertEqual(samples[:subpicks], sub_samples)
