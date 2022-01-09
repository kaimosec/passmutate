import glob
import os
import sys


class Resource:
    """Provides a kind of interface between files and stdin so that they act similarly"""
    """filename can be a list if reading multiple files is required"""
    def __init__(self, filenames=None, count_lines=True):
        self.filenames = filenames

        self.count = 0  # The amount of lines yielded so far
        self.lines = 0  # Total lines present in all files
        self.filesize = 0  # Total filesize of all files

        if self.filenames != '-' and type(self.filenames) != list:
            raise Exception("Filenames must be a list or '-'")

        if self.filenames == '-':
            self.is_file = False
        else:
            if len(self.filenames) == 0:
                raise Exception("No files found for query {}".format(filenames))

            if count_lines:
                self.lines, self.filesize = self.count_lines()

            self.is_file = True

    @staticmethod
    def process_arg(filenames):
        """Ensure filename is a list. Potentially process glob string or comma-separated string."""
        # Process filenames into usable list
        if type(filenames) != list:
            if ',' in filenames:
                # -i filename1,filename2,...
                filenames = filenames.split(',')
            elif '*' in filenames:
                # -i ./*
                filenames = glob.glob(filenames, recursive=False)
                filenames = [x for x in filenames if not os.path.isdir(x)]  # Filter out directories
            else:
                filenames = [filenames]

        return filenames

    def readline(self):
        """Generate lines of either stdin or files"""
        if not self.is_file:
            with open(sys.stdin.fileno(), 'r', errors='replace') as inp:
                for line in inp:
                    line = line.strip()
                    if len(line) > 0:
                        yield line
                        self.count += 1
        else:
            for filename in self.filenames:
                with open(filename, errors='replace') as file:
                    for line in file:
                        line = line.strip()
                        if len(line) > 0:
                            yield line
                            self.count += 1

    def count_lines(self):
        """Return filesize and total lines of files loaded"""
        lines = 0
        filesize = 0
        for filename in self.filenames:
            with open(filename, errors='replace') as f:
                for line in f:
                    lines += 1
                    filesize += len(line)

        return lines, filesize
