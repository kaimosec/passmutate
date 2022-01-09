"""
Made by Benchi (https://github.com/benchi/big_file_sort)
Modified by Kaimo
"""
__author__ = 'larry'

import heapq
import os
import tempfile
import logging


class BFS:
    def __init__(self):
        self.lines = 0
        self.logger = logging.getLogger('__main__')

    def file_chunk_lines(self, f, chunk_size=65536):
        """Read chunks of lines and yield them one by one
        We default to a smaller chunk than the buffer size because we will be reading this from many files at the same
        time.
        """
        while f:
            lines = f.readlines(chunk_size)
            if not lines:
                break
            for line in lines:
                self.lines += 1
                yield line

    @staticmethod
    def break_into_temp_files(filenames: list, key, temp_file_location, temp_file_size):
        """
        Given an input file
        1. Break it into parts of size indicated by temp_file_size
        2. Sort each of those parts
        3. Write each of those parts to disk in a temp file
        4. Return the list of temp filenames
        """
        temp_filenames = []
        read_size = int(0.95 * temp_file_size)

        for filename in filenames:
            file = open(filename, errors='replace')
            while file:
                lines = file.readlines(read_size)

                if not lines:
                    file.close()
                    file = None

                lines.sort(key=key)

                new_handle, new_filename = tempfile.mkstemp(dir=temp_file_location)
                temp_file = os.fdopen(new_handle, 'w')
                temp_file.writelines(lines)
                temp_file.close()
                temp_filenames.append(new_filename)

        return temp_filenames

    def sort_file(self, filenames: list, output_filename, key=None, temp_file_location=None,
                  temp_file_size=1048576, buffer_size=1048576):
        """
        Given input_filename which indicates a file of arbitrary size
        Write the same data to output_file with lines sorted by key_function
        Contents of output_file should be exactly the same size and the same number of lines
        """
        try:
            os.mkdir(temp_file_location)
        except OSError:
            # If the directory already exists, we don't need to panic
            # If this is another exception, we will fail very soon.
            pass

        self.logger.info('Fragmenting file..')
        temp_filenames = BFS.break_into_temp_files(filenames, key, temp_file_location, temp_file_size)

        with open(output_filename, 'w', buffer_size) as out_file:
            temp_files = [open(filename) for filename in temp_filenames]
            temp_files_iterators = [self.file_chunk_lines(f) for f in temp_files]
            self.logger.info('Heap merging..')
            out_file.writelines(heapq.merge(*temp_files_iterators, key=key))

            for x in temp_files:
                x.close()
            for x in temp_filenames:
                os.remove(x)
