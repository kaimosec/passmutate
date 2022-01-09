import argparse
import shutil
import sys
import re
import logging
import os
from datetime import datetime

from alive_progress import alive_bar
from src.benchi.big_file_sort import BFS

from src.analyzer import Analyzer

from src.resource import Resource
from src.outputter import Outputter

from src.filter import Filter
from src.sorter import Sorter
from src.augmentor import Augmentor

from src.logformatter import LogFormatter
from src.diskutil import DiskUtil

from src.sampler.samplerordered import SamplerOrdered
from src.sampler.samplerrandom import SamplerRandom

"""
Made by Kaimo (https://github.com/kaimosensei)
"""


class Parser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write('Error: %s\n\n' % message)
        self.print_help()
        sys.exit(2)


if __name__ == '__main__':
    start_time = datetime.now()
    version = '1.0'

    # Argument Parsing
    parser = Parser('mutate.py')

    # Mode category
    group_modes = parser.add_argument_group(title="Modes of operation")
    group_modes.add_argument(
        '-i',
        dest='FILE',
        help="process FILE. 'FILENAME' to grab 1 file, 'FILENAME1,FILENAME2,...' to grab multiple, './*.txt' to grab"
             " all .txt files in the folder or '-' for stdin"
    )
    group_modes.add_argument('-a', dest='ANALYZE_FILE', help='Analyze wordlist ANALYZE_FILE. Can analyze multiple files'
                             ' together as shown in -i')

    # General processing category
    group_process = parser.add_argument_group(title="General processing options")
    group_process.add_argument(
        '-m',
        dest='MUTATE_LEVEL',
        help='Mutate passwords for level of complexity 0, 1 or 2',
        type=int
    )
    group_process.add_argument(
        '-s',
        dest='SORT',
        help='Sort wordlist (a)lphabetically or by (e)fficacy (-s a, -s e). -o must be a filename'
    )
    group_process.add_argument('-o', dest='OUTPUT', help='Output to save to. Filename or - for stdout')

    # Filtering category
    group_filter = parser.add_argument_group(title="Wordlist filtering")
    group_filter.add_argument('-f', dest='STD_FILTER', help='Filter wordlist using standard filter (see docs)')
    group_filter.add_argument('-r', dest='REG_FILTER', help='Filter wordlist with regex')
    group_filter.add_argument(
        '-l',
        dest='LEN_FILTER',
        help='Filter wordlist by length(s) (e.g. 7 for 7 chars, 7:9 for between 7 and 9 chars, inclusive)'
    )
    group_filter.add_argument(
        '-x',
        dest='ASCII_FILTER',
        action='store_true',
        help='Filter passwords that only contain standard ascii characters (e.g. A-Z a-z 0-9 !@#$^&...)'
    )
    group_filter.add_argument('-c', dest='CHAR_FILTER', help='Filter wordlist using a charset (e.g. -c "abcdefg")')
    group_filter.add_argument(
        '-p',
        dest='PICK_NUM',
        help='Pick out PICK_NUM distributed passwords from a wordlist',
        type=int
    )

    # General category
    group_general = parser.add_argument_group(title="General options")
    group_general.add_argument(
        '-q', '--quiet',
        dest='QUIET',
        action='store_true',
        help='Run with no unnecessary output. Enabled automatically when outputting to stdout'
    )
    group_general.add_argument(
        '-v', '--verbose',
        help="Print verbose information",
        action="store_const", dest="loglevel", const=logging.INFO,
        default=logging.INFO
    )
    group_general.add_argument(
        '--ignore',
        dest='IGNORE',
        action='store_true',
        help='Ignore warnings about insufficient disk-space, etc.'
    )

    # Advanced Category
    group_advanced = parser.add_argument_group(title="Advanced options")
    group_advanced.add_argument(
        '--tmp-dir',
        dest='TEMP_DIR',
        help='Set the temporary directory'
    )

    logo = """
      _____              __  __       _        _       
     |  __ \            |  \/  |     | |      | |      
     | |__) |_ _ ___ ___| \  / |_   _| |_ __ _| |_ ___ 
     |  ___/ _` / __/ __| |\/| | | | | __/ _` | __/ _ \\
     | |  | (_| \__ \__ \ |  | | |_| | || (_| | ||  __/
     |_|   \__,_|___/___/_|  |_|\__,_|\__\__,_|\__\___|   v{}
                        By Kaimo
            """.format(version)

    # Print logo with help if no arguments
    if len(sys.argv) == 1:
        print(logo)
        parser.print_help()
        sys.exit(1)

    # Define arg variables and intentions
    args = parser.parse_args()

    # Names of filters not including picking
    filter_names = [
        'LEN_FILTER',
        'CHAR_FILTER',
        'STD_FILTER',
        'REG_FILTER',
        'ASCII_FILTER'
    ]
    will_filter = any(map(lambda x: args.__dict__[x] is not False and args.__dict__[x] is not None, filter_names))

    # List of args that mean the file is being processed in any way before sorting
    file_processing_names = [
        "MUTATE_LEVEL",
        "PICK_NUM"
    ] + filter_names.copy()

    loading_multiple_files = False
    if args.ANALYZE_FILE is None:
        if '*' in args.FILE or ',' in args.FILE:
            loading_multiple_files = True

    will_process_file = any(map(
        lambda x: args.__dict__[x] is not False and args.__dict__[x] is not None, file_processing_names
    )) or loading_multiple_files or (args.FILE == '-' and args.SORT is not None)

    # List of args to check if nothing is being done
    doing_anything_names = [
        'SORT',
        'ANALYZE_FILE',
    ] + file_processing_names.copy()
    will_do_something = any(map(
        lambda x: args.__dict__[x] is not False and args.__dict__[x] is not None, doing_anything_names
    )) or loading_multiple_files

    # Define paths and folders. tmp_folder must end in /
    abs_path = (os.path.dirname(__file__) or '.') + '/'
    if args.TEMP_DIR:
        tmp_folder = args.TEMP_DIR
        if tmp_folder[-1] != '/':
            tmp_folder += '/'
    elif os.path.isdir('/tmp'):
        # If /tmp folder exists, use that
        tmp_folder = '/tmp/passmutate/'
    else:
        tmp_folder = abs_path + "tmp/"

    # If tmp_folder doesn't exist, create it
    if not os.path.isdir(tmp_folder):
        os.mkdir(tmp_folder)

    # Process logger and quiet variable
    if args.QUIET or args.OUTPUT == '-':
        quiet = True
        loglevel = logging.ERROR
    else:
        quiet = False
        loglevel = args.loglevel

    log_filename = tmp_folder + 'log.log'

    # Make sure log.log doesn't already exist
    if os.path.isfile(log_filename):
        os.remove(log_filename)

    log_formatter = LogFormatter()
    logging.basicConfig(filename=log_filename)
    logger = logging.getLogger(__name__)
    logger.setLevel(loglevel)

    ch = logging.StreamHandler()
    ch.setLevel(level=loglevel)
    ch.setFormatter(log_formatter)

    logger.addHandler(ch)

    # Check if tmp folder contains more than log.log
    if len(list(os.scandir(tmp_folder))) > 1 and not quiet and not args.IGNORE:
        logger.warning("WARNING: Temporary folder '{}' is not empty.".format(tmp_folder))

    if not quiet:
        print(logo)

    # Validate args
    if args.MUTATE_LEVEL is not None:
        if not 0 <= args.MUTATE_LEVEL <= 2:
            logger.error('-m must be 0, 1 or 2')
            exit(1)
    if args.SORT is not None:
        if args.SORT != 'e' and args.SORT != 'a':
            logger.error('-s must be a or e')
            exit(1)

    if not will_do_something:
        # All sort, mutate, analyze and filter args are set to None so there's no point in running the program
        logger.error("There's nothing to do. Quitting..")
        exit(1)

    if not args.ANALYZE_FILE:
        # If not analyzing, both -i and -o must be defined
        if not args.FILE:
            logger.error('-i must be specified')
            exit(1)

        if not args.OUTPUT:
            logger.error('-o must be specified')
            exit(1)

    # Main stuff
    # Mode: Analyze file
    if args.ANALYZE_FILE:
        filenames = Resource.process_arg(args.ANALYZE_FILE)
        resource = Resource(filenames)
        if not quiet:
            logger.info(
                "Analyzing {}..".format("standard input" if args.ANALYZE_FILE == '-' else ", ".join(resource.filenames))
            )

        analyzer = Analyzer(resource)
        analyzer.analyze()

    # Mode: Standard(input, (opt) augment, (opt) filter, (opt) sort, output)
    elif args.FILE:
        # Define resource (input) and output

        # process args.FILE for resource
        if args.FILE == '-':
            filenames = '-'
        else:
            filenames = Resource.process_arg(args.FILE)

        # input and output can't be the same file
        if type(filenames) == list and not args.OUTPUT == '-':
            if args.OUTPUT in filenames:
                logger.error('input file cannot be the same as the output file (inputs: {})'.format(filenames))
                exit(1)

        resource = Resource(filenames)
        output = Outputter(args.OUTPUT)

        if not args.IGNORE:
            # Make sure there's enough disk space
            bytes_needed, bytes_up_to = DiskUtil.estimate_required_bytes(args, resource)
            free_bytes = DiskUtil.get_free_bytes('.')

            if bytes_needed is not False:
                # Number of bytes needed for operation can be defined
                logger.debug("Use {}{:,}MB, free space {:,}MB".format(
                    "up to " if bytes_up_to else "",
                    bytes_needed / 1024 // 1024,
                    free_bytes / 1024 // 1024
                ))
                if bytes_needed > free_bytes:
                    # Potentially not enough space
                    help_size_message = "If you have low disk space, consider not sorting (uses a lot of disk space)," \
                                        " lowering the mutate level or outputting to stdout (-o -) "

                    if bytes_up_to:
                        # Up to bytes_needed will be used (i.e. the estimation is not exact)
                        inp = input(
                            "(skip this with --ignore) WARNING: You only have {:,}MB of free space but up to {:,}MB may"
                            " be used, depending on filtering. \n{}\n"
                            "Type enter to continue anyways or any key to quit: "
                            .format(free_bytes / 1024 // 1024, bytes_needed / 1024 // 1024, help_size_message)
                            )
                        if inp != '':
                            exit(1)
                    else:
                        # Exactly bytes_needed will be used
                        logger.error("(skip this with --ignore) ERROR: You only have {:,}MB of free space but {:,}MB is"
                                     " required. Quitting.."
                                     .format(free_bytes / 1024 // 1024, bytes_needed / 1024 // 1024)
                                     )
                        logger.error(help_size_message)
                        exit(1)

        logger.info(
            "Processing {}..".format(
                "standard input" if filenames == '-' else ", ".join(filenames)
            )
        )

        if will_process_file:
            # Define the line generator getpwfunc. If mutating, getpwfunc runs thorugh that.
            # Otherwise, getpwfunc just iterates line by line as normal
            if args.MUTATE_LEVEL is not None:
                # Print augmentation info
                if resource.lines > 0:
                    augment_string = "({:,.0f} -> ~{:,.0f} passwords)".format(
                        resource.lines,
                        resource.lines * Augmentor.get_approximate_ratios()[args.MUTATE_LEVEL]
                    )
                else:
                    augment_string = "(create ~{:,.0f} passwords per 1)".format(
                        Augmentor.get_approximate_ratios()[args.MUTATE_LEVEL]
                    )
                logger.info("Augmenting at level {} {}..".format(args.MUTATE_LEVEL, augment_string))

                augmentor = Augmentor(resource, args.MUTATE_LEVEL)
                getpwfunc = augmentor.augment_from_resource
            else:
                getpwfunc = resource.readline

            # Print filter info
            if args.LEN_FILTER or args.CHAR_FILTER or args.STD_FILTER or args.REG_FILTER or args.ASCII_FILTER:
                filter_desc_dict = {
                    'LEN_FILTER': 'length',
                    'CHAR_FILTER': 'characters',
                    'STD_FILTER': 'standard filter',
                    'REG_FILTER': 'regex',
                    'ASCII_FILTER': 'ascii'
                }
                logger.info("Filtering based on {}..".format(
                    ", ".join([v for k, v in filter_desc_dict.items() if args.__dict__[k]]))
                )

            # Print picker info
            sampler = None
            if args.PICK_NUM:
                if filenames == '-' or will_filter:
                    logger.info("Picking out {} passwords in random order".format(args.PICK_NUM))
                    sampler = SamplerRandom(args.PICK_NUM)
                else:
                    logger.info("Picking out {} ordered, evenly distributed passwords".format(args.PICK_NUM))
                    sampler = SamplerOrdered(filenames, args.PICK_NUM)

            # Prepare to process line by line
            process_count = 0  # Number of lines processed
            filter_count = 0  # Number of lines filtered out
            output_count = 0  # Number of lines written to file or stdout

            # Calculate total steps for progress bar
            total_passwords = resource.lines
            if args.MUTATE_LEVEL is not None:
                total_passwords *= Augmentor.get_approximate_ratios()[args.MUTATE_LEVEL]

            # Compile standard and regex filters before looping for optimization
            std_filter = None
            re_pattern = None
            if args.STD_FILTER:
                std_filter = Filter.process_std_pattern(args.STD_FILTER)
            if args.REG_FILTER:
                re_pattern = re.compile(args.REG_FILTER)

            # Parse length filtering for optimization
            filter_length = None
            if args.LEN_FILTER:
                if ':' in args.LEN_FILTER:
                    filter_length = list(map(int, args.LEN_FILTER.split(':')))
                else:
                    filter_length = int(args.LEN_FILTER), int(args.LEN_FILTER)

            # Loop line by line
            with alive_bar(total_passwords, disable=quiet) as bar:
                for line in getpwfunc():
                    bar()
                    process_count += 1

                    # FILTERING
                    # Automatically filter blank lines
                    if line == '':
                        filter_count += 1
                        continue

                    # Ascii filter
                    if args.ASCII_FILTER:
                        is_ascii = True
                        for c in line:
                            if not 32 <= ord(c) <= 126:
                                is_ascii = False
                                break
                        if not is_ascii:
                            filter_count += 1
                            continue

                    # Length filter
                    if filter_length:
                        if not Filter.filter_length(filter_length[0], filter_length[1], line):
                            filter_count += 1
                            continue

                    # Charset filter
                    if args.CHAR_FILTER:
                        if not Filter.filter_charset(args.CHAR_FILTER, line):
                            filter_count += 1
                            continue

                    # Standard pattern filter
                    if std_filter:
                        if not Filter.filter_std(std_filter, line):
                            filter_count += 1
                            continue

                    # Regex filter
                    if re_pattern:
                        if not Filter.filter_regex(re_pattern, line):
                            filter_count += 1
                            continue

                    # Output
                    # If there's no sampler, just output the line straight away
                    # Otherwise, store the results and output them later
                    if sampler is None:
                        output.output(line)
                    else:
                        sampler.process_line(line)

                # Set bar to 100% if it finishes processing before the bar fills up
                bar(total_passwords - process_count)

            # Output (continued)
            if sampler is not None:
                samples = sampler.get_samples(args.PICK_NUM)
                for line in samples:
                    output.output(line)

            # Finished processing line by line.
            output.close()

            # Print statistics
            if not quiet:
                logger.info("Passwords inputted: {:,}".format(resource.count))
                if 'MUTATE_LEVEL' in args:
                    logger.info("Passwords added via mutation: {:,}".format(process_count - resource.count))
                if filter_count > 0:
                    logger.info("Passwords filtered out: {:,}".format(filter_count))
                logger.info("Passwords outputted: {:,}".format(output.output_count))

                elapsed = datetime.now() - start_time

                logger.info("Processed {:,} passwords in {}h {}m {}s at a rate of {:,.0f} p/s".format(
                    process_count,
                    elapsed.seconds // 3600,
                    elapsed.seconds // 60 % 60,
                    elapsed.seconds % 60,
                    process_count / elapsed.total_seconds()
                ))

        # Sort file
        if args.SORT is not None:
            start_sort_time = datetime.now()

            # Cannot continue if the output wasn't saved to a file
            if args.OUTPUT == '-':
                raise Exception("Cannot sort when -o is not a filename")

            # Define input file
            # If the file was never changed, read from -i, otherwise, read from -o which was just written to.
            if will_process_file:
                sort_input_file = [args.OUTPUT]
            else:
                sort_input_file = filenames

            # Sort the file and save to TMP_FILENAME
            tmp_filename = DiskUtil.get_unique_filename(tmp_folder)
            bfs_sorter = BFS()
            if args.SORT == 'a':
                # Alphabetical sort
                logger.info("Sorting alphabetically..")
                bfs_sorter.sort_file(
                    sort_input_file,
                    tmp_filename,
                    temp_file_location=tmp_folder
                )
            else:
                # Efficacy sort
                logger.info("Sorting by efficacy..")
                sorter = Sorter()
                bfs_sorter.sort_file(
                    sort_input_file,
                    tmp_filename,
                    temp_file_location=tmp_folder,
                    key=sorter.sort_weight_alphabet
                )

            # If the input file was already processed and saved delete it and move the sorted output there, replacing it
            if will_process_file:
                os.remove(args.OUTPUT)
            shutil.move(tmp_filename, args.OUTPUT)

            # Print sort info
            elapsed = datetime.now() - start_sort_time
            logger.info("Sorted {:,} passwords in {}h {}m {:.2f}s at a rate of {:,.0f} p/s".format(
                    bfs_sorter.lines,
                    elapsed.seconds // 3600,
                    elapsed.seconds // 60 % 60,
                    elapsed.total_seconds() % 60,
                    bfs_sorter.lines / elapsed.total_seconds()
                ))
    else:
        print("How did you get here?")

    if not quiet:
        print("Done!")
