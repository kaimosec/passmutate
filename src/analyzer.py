import re

from src.sampler.samplerrandom import SamplerRandom
from src.sampler.samplerordered import SamplerOrdered

from src.sortanalyzer import SortAnalyzer
from src.sorter import Sorter

from alive_progress import alive_bar


class Analyzer:
    """Analyze a wordlist and print valuable statistics regarding it"""
    def __init__(self, resource):
        self.resource = resource

        self.sort_anlz_alphabet = SortAnalyzer()
        sorter = Sorter()
        self.sort_anlz_eff = SortAnalyzer(sorter.sort_weight_alphabet)

        self.print_sample_num = 25
        if resource.is_file:
            self.sampler = SamplerOrdered(resource.filenames, self.print_sample_num)
        else:
            self.sampler = SamplerRandom(1000)

    def analyze(self):
        lines = 0
        with_numbers = 0
        with_specialcharacters = 0
        with_uppercase = 0
        with_lowercase = 0

        lengths = {}

        re_numbers = re.compile(r"[0-9]")
        re_specs = re.compile(r"[^A-Za-z0-9]")
        re_upper = re.compile(r"[A-Z]")
        re_lower = re.compile(r"[a-z]")

        with alive_bar(self.resource.lines) as bar:
            for line in self.resource.readline():
                # Sample lines
                self.sampler.process_line(line)

                # Regex
                if re_numbers.search(line):
                    with_numbers += 1

                if re_specs.search(line):
                    with_specialcharacters += 1

                if re_upper.search(line):
                    with_uppercase += 1

                if re_lower.search(line):
                    with_lowercase += 1

                # Lengths
                if len(line) not in lengths:
                    lengths[len(line)] = 1
                else:
                    lengths[len(line)] += 1

                # Sort Analyzer
                self.sort_anlz_alphabet.check_line(line)
                self.sort_anlz_eff.check_line(line)

                bar()
                lines += 1

        if lines == 0:
            raise Exception("Cannot analyze: File(s) ({}) are empty".format(self.resource.filenames))

        print("""
Lines: {:,d}
    Contains lowercase:     {:,d} ({:.1f}%)
    Contains uppercase:     {:,d} ({:.1f}%)
    Contains numbers:       {:,d} ({:.1f}%)
    Contains special chars: {:,d} ({:.1f}%)

Password length chart:
{}
    
Sorting:
    Alphabet Sort Accuracy: {:.3f}%
    Ordering Efficiency Rating: {:.3f}%

{}:
    {}
""".format(
            lines,
            with_lowercase,
            with_lowercase / lines * 100,
            with_uppercase,
            with_uppercase / lines * 100,
            with_numbers,
            with_numbers / lines * 100,
            with_specialcharacters,
            with_specialcharacters / lines * 100,

            Analyzer.get_cli_graph(lengths, lines, 15),

            self.sort_anlz_alphabet.get_accuracy() * 100,
            self.sort_anlz_eff.get_accuracy() * 100,

            "Samples picked from wordlist in order" if self.resource.is_file else
            "Randomly picked samples in random order",
            "\n    ".join(self.sampler.get_samples(self.print_sample_num)),
        ))

    @staticmethod
    def get_cli_graph(lengths: dict, total_lines, graph_height, graph_width=24):
        """Return a text-based graph used to show the frequency of passwords at different lengths"""
        most_common_length = (-1, -1)
        weighted_average = 0
        for k, v in lengths.items():
            if v > most_common_length[1]:
                most_common_length = (k, v)
            weighted_average += k * (v / total_lines)
        weighted_average = round(weighted_average)

        half_width = min(weighted_average, graph_width // 2)

        normalizing_mul = 1 / (most_common_length[1] / total_lines)

        min_domain = weighted_average - half_width
        max_domain = weighted_average + half_width

        output = ''
        for y in range(graph_height, -1, -1):
            y_val = y / graph_height
            for x in range(min_domain - 1, max_domain + 1):
                if y == 0:
                    if x == min_domain - 1:
                        output += '   |'
                    else:
                        output += "{: 3d}|".format(x)
                else:
                    if x == min_domain - 1:
                        if y == graph_height or y == 1:
                            output += '{:02d}%|'.format(min(99, int(y_val / normalizing_mul * 100)))
                        else:
                            output += '   |'
                    else:
                        draw = False
                        if x in lengths:
                            if (lengths[x] / total_lines) * normalizing_mul >= y_val:
                                draw = True

                        if draw:
                            output += '███|'
                        else:
                            output += '   |'

            output += "\n"

        return output
