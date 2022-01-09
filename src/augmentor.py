from src.combinator import Combinator
import datetime


class Augmentor:
    """
    Manages augmentation/mutation of passwords.
    Attempts to generate multiple passwords from a single one while removing as many duplicates as possible.
    """
    def __init__(self, resource=None, complexity=0):
        self.resource = resource
        self.complexity = complexity

        self.augment_funcs = {
            0: Augmentor.get_simple_list(),
            1: Augmentor.get_medium_list(),
            2: Augmentor.get_advanced_list()
        }

        # Start by preparing the functions that will be used to mutate passwords, along with which functions are PIF
        self.all_functions, self.pif_count = self.augment_funcs[self.complexity]

        # Generate all possible combinations of mutation functions ahead of time for optimization's sake
        self.combinations = list(Combinator.getpossibilities(self.all_functions))

    def augment(self, string, debug=False):
        """
        A generator that mutates a string in many possible ways together to create new strings and avoids duplicates
        Always yields the original string first
        """
        if not string:
            return False

        yield string

        # Example of combination (i.e. funclist): [Augment.upper, Augment.remove_numbers_at_end, '>6']
        # Will take a string, convert it to uppercase, remove numbers at end if applicable then add a 6
        for funclist in self.combinations:
            continue_combo = False

            string_hist = [string]
            i = 0

            for func in funclist:
                # Augmentor.upper, Augmentor.lower and Augmentor.firstupper are the only PIF functions present so this
                # algorithm works for now but will need to change in the future.
                # If a PIF function is out of order, funclist is invalid
                if i > 0:
                    if func == Augmentor.upper or func == Augmentor.lower or func == Augmentor.firstupper:
                        continue_combo = True
                        break

                # Augment string with current func from funclist
                curstring = Augmentor.funclist_interpret(func, string_hist[-1])

                # If func didn't do anything, funclist is invalid
                # If string reverted back to how it was in a previous step, funclist is invalid
                if not curstring or curstring in string_hist:
                    continue_combo = True
                    break

                string_hist.append(curstring)

                i += 1

            if continue_combo:
                continue

            if not debug:
                yield string_hist[-1]
            else:
                yield string_hist[-1], string, funclist

    def augment_from_resource(self):
        for x in self.resource.readline():
            for y in self.augment(x):
                yield y

    """
    Modify and return a string based on FUNC instructions.
    Func can either be a callable function or a string that is interpreted manually.
    
    Func strings:
    >{} = Add to end of string only if no number at end
    !{} = Add to end if spec. char not at end
    @{} = Add to end, regardless
    """
    @staticmethod
    def funclist_interpret(func, string):
        if callable(func):
            return func(string)
        if type(func) == str:
            if func[0] == ">":
                # Add to end of string only if no number at end
                if not 48 <= ord(string[-1]) <= 57:
                    return string + func[1:]
                return False
            elif func[0] == "!":
                # Add common spec. char at end if no spec.char is present
                if not Augmentor.ord_is_spec(ord(string[-1])):
                    return string + func[1:]
                return False
            elif func[0] == "@":
                # Add to end, regardless
                return string + func[1:]
        raise Exception("Instruction undefined: {}".format(func))

    @staticmethod
    def ord_is_spec(num):
        """Return whether or not NUM (integer version of a char) is a special character"""
        return not (48 <= num <= 57 or 65 <= num <= 90 or 97 <= num <= 122)

    """
    Return 2 lists
    List 1: group of augmentation functions to augment a password.
    The combinator provides every possible combination between these groups.
    Position-Independent-Functions should always be first in the list.
    
    Combinations are generated in groups of functions instead of functions themselves because it prevents those
    functions grouped together from mutating against each other, which would be inefficient.
    e.g. it doesn't make sense to convert to upper then convert to lower in the same combination.
    
    List 2: How many elements from the beginning of list 1 are position-independent functions.
    (i.e. which functions will not change the final password at all based on its own position.)
    Labelling these means I can avoid generating a password if the position-independent function is in a different
    position, which helps to cur out duplicates. 
    """
    @staticmethod
    def get_simple_list():
        return ([
            [
                Augmentor.upper,
                Augmentor.lower,
                Augmentor.firstupper,
            ],

            [Augmentor.remove_numbers_at_end],
            [Augmentor.remove_specs_at_end],

            # Add 0-9 and common numbers at end if no number at end exists
            # Add common spec. characters to end of string if no spec. characters at end
            ['>123', '>69'] + [">{}".format(i) for i in range(0, 10)] +
            ["!{}".format(x) for x in ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')']],
        ],
            # Don't forget to change the PIF-detection algorithm in should_augment if ever having more than 1 PIF
            1  # i.e. Only the first category is a pif-category
        )

    @staticmethod
    def get_medium_list():
        lst = Augmentor.get_simple_list()

        year = int(datetime.date.today().strftime("%Y"))
        lst[0][3] += ['>1234'] + [">{}".format(i) for i in range(10, 30)] +\
                     [">{}".format(i) for i in range(year - 80, year + 2)]
        lst[0][3] += ["!{}".format(x) for x in ['`', '~', '-', '_', '+', '=', '|', '\\', '/', ',', '.', '<', '>']]

        return lst

    @staticmethod
    def get_advanced_list():
        lst = Augmentor.get_simple_list()

        year = int(datetime.date.today().strftime("%Y"))
        suffixes = ['>123', '>1234', '>00', '>666']
        suffixes += [">{}".format(i) for i in range(0, 100)]
        suffixes += [">{}".format(i) for i in range(year - 80, year + 5)]
        lst[0][3] = suffixes

        all_specs = ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')', '`', '~', '-', '_', '+',
                     '=', '|', '\\', '/', ',', '.', '<', '>']
        suffixes_spec = ['!{}'.format(x) for x in all_specs]
        lst[0].append(suffixes_spec)

        return lst

    @staticmethod
    def get_approximate_ratios():
        """
        Approximately how many passwords are created from a single password per level of complexity.
        Helps to be able to estimate how large files will be or how long a process might take.
        Note that results will vary from this.
        """
        return {
            0: 60,
            1: 350,
            2: 24200
        }

    # Mutators
    # Cases
    @staticmethod
    def upper(s):
        return s.upper()

    @staticmethod
    def lower(s):
        return s.lower()

    @staticmethod
    def firstupper(s):
        return s[0].upper() + s[1:]

    # Suffixes
    @staticmethod
    def remove_numbers_at_end(s):
        if not 48 <= ord(s[-1]) <= 57:
            return False

        while 48 <= ord(s[-1]) <= 57:
            s = s[:-1]
            if s == '':
                return False

        return s

    @staticmethod
    def remove_specs_at_end(s):
        num = ord(s[-1])
        if 48 <= num <= 57 or 65 <= num <= 90 or 97 <= num <= 122:
            return False

        while not (48 <= num <= 57 or 65 <= num <= 90 or 97 <= num <= 122):
            s = s[:-1]
            if s == '':
                return False
            num = ord(s[-1])

        return s
