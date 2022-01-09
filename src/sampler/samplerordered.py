from src.sampler.samplerinterface import SamplerInterface
import os


class SamplerOrdered(SamplerInterface):
    def __init__(self, filenames, sample_num=1000):
        # Ensure sample_num is > 0
        if sample_num <= 0:
            raise ValueError("sample_num must be at least 1")

        self.filenames = filenames

        if type(self.filenames) == str:
            self.filenames = [self.filenames]

        # Ensure all files exist
        missing_files = [x for x in self.filenames if not os.path.isfile(x)]
        if missing_files:
            raise ValueError("File(s) '{}' does not exist".format(missing_files))

        self.sample_num = sample_num
        self.line_count = self.count_lines()
        self.line_num = 0
        self.next_sample = 0
        self.samples = []

    def count_lines(self):
        lines = 0
        for filename in self.filenames:
            with open(filename, errors='replace') as file:
                lines += sum(1 for _ in file)

        return lines

    def process_line(self, line):
        if self.line_num >= self.next_sample:
            self.samples.append(line)
            self.next_sample += self.line_count / self.sample_num

        self.line_num += 1

    def get_samples(self, n=None):
        if n is None or n > len(self.samples):
            return self.samples

        return self.samples[0:n]
