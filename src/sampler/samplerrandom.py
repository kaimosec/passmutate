import random
from src.sampler.samplerinterface import SamplerInterface


class SamplerRandom(SamplerInterface):
    """
    Pull samples from a wordlist here and there to give an idea of what's in it.
    The algorithm tries to get a roughly even spread of samples in an efficient way without knowing
    how large the source is
    """
    def __init__(self, sample_size):
        self.samples = []
        self.size = sample_size
        self.puts = 0  # The amount of times a string has tried to be placed

        self.frequency = 1
        self.frequency_mul = 1.008
        self.nextsample = 1

    def process_line(self, string):
        self.puts += 1
        if len(self.samples) < self.size:
            self.samples.append(string)
        else:
            if self.puts >= self.nextsample:
                self.samples[random.randint(0, len(self.samples) - 1)] = string
                self.frequency *= self.frequency_mul
                self.nextsample = self.puts + self.frequency

    def get_samples(self, n=None):
        """Get N samples, randomly picked"""
        if n is None or n > len(self.samples):
            return self.samples

        return random.sample(self.samples, n)
