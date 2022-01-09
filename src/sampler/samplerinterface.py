import abc


class SamplerInterface(abc.ABC):
    @abc.abstractmethod
    def process_line(self, line):
        pass

    @abc.abstractmethod
    def get_samples(self, n):
        pass
