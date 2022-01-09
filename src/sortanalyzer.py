class SortAnalyzer:
    """Determine how accurate a sort is given a key"""
    def __init__(self, key=None):
        self.discrepancy_count = 0
        self.lines_checked = 0

        self.key = key

        self.last_weight = 0
        self.last_line = ''

    def check_line(self, line):
        weight = line if not self.key else self.key(line)
        if self.lines_checked > 0:
            if self.last_weight > weight:
                self.discrepancy_count += 1

        self.last_weight = weight
        self.lines_checked += 1

    def get_accuracy(self):
        return (self.lines_checked - self.discrepancy_count) / self.lines_checked
