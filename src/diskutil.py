import shutil
from src.augmentor import Augmentor
import random
import os


class DiskUtil:
    """Manage disk space requirements for program"""
    @staticmethod
    def estimate_required_bytes(args, resource):
        """Try to estimate rough disk space usage, in bytes using args"""
        up_to = False  # If true, usage can be up to BYTES instead of at BYTES

        if args.FILE == '-':
            return False, up_to  # Cannot estimate due to using stdin

        filesizes = [resource.filesize]

        if args.LEN_FILTER or args.CHAR_FILTER or args.STD_FILTER or args.REG_FILTER or args.ASCII_FILTER:
            # Filtering is selected so we don't know exactly how big the result will be, only how big it could be
            up_to = True

        if args.MUTATE_LEVEL is not None:
            ratio = Augmentor.get_approximate_ratios()[args.MUTATE_LEVEL]
            filesizes.append(filesizes[-1] * ratio)

            # Mutation is selected
            if not args.SORT:
                # No sorting
                if args.OUTPUT == '-':
                    # Outputting to stdout
                    return 0, up_to

                return sum(filesizes[1:]), up_to
            else:
                filesizes.append(filesizes[-1])  # Split into temporary files
                filesizes.append(filesizes[-1])  # Save sorted file to new file
                return sum(filesizes[1:]), up_to
        else:
            if not args.SORT:
                if args.OUTPUT == '-':
                    return 0, up_to
                return sum(filesizes), up_to
            else:
                return sum(filesizes)*2, up_to

    @staticmethod
    def get_free_bytes(path):
        return shutil.disk_usage(path)[2]

    @staticmethod
    def generate_random_string(
            length=8,
            prefix="",
            suffix="",
            charset='abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    ):
        return prefix + "".join(random.choices(charset, k=length)) + suffix

    @staticmethod
    def get_unique_filename(base_path="", extension="tmp"):
        """
        Create a randomly-created filename, guaranteed to not already exist.
        """
        # Ensure base path has a / at the end of it unless base_path is empty
        if base_path:
            if base_path[-1] != '/' and base_path[-1] != '\\':
                base_path += '/'

        filename = base_path + DiskUtil.generate_random_string() + "." + extension
        i = 0
        while os.path.exists("{}{}.{}".format(base_path, filename, extension)):
            filename = base_path + DiskUtil.generate_random_string() + "." + extension
            if i > 10000:
                # If you failed to look for a free filename after 10,000 tries, just quit
                raise Exception("Unable to find temporary filename in path '{}'".format(base_path))
            i += 1

        return filename
