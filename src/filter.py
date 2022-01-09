import re


class Filter:
    """Class for filtering words by various methods. Words not passing the criteria results in returning false"""
    op_chars = ['.', '#', '^', '\\', '%', '&']

    @staticmethod
    def filter_length(min_length, max_length, string):
        if not min_length <= len(string) <= max_length:
            return False
        return True

    @staticmethod
    def filter_charset(chars, string):
        """If chars = ['a', 'b', 'c'] then string must consist of nothing else but the letters a, b and c."""
        return not any([char not in chars for char in string])

    @staticmethod
    def filter_regex(pattern, string):
        if type(pattern) == str:
            search = re.search(pattern, string)
        else:
            # pattern is compiled regex pattern
            search = pattern.search(string)

        return bool(search)

    @staticmethod
    def process_std_pattern(pattern):
        """Compile std pattern for use in filter_std"""
        literal_chars = []
        previous_backslash = False

        # remove backslashes and mark the literal chars
        i = 0
        while i < len(pattern):
            char = pattern[i]

            if char in Filter.op_chars and previous_backslash:
                # current char is op char and previous char was a backslash
                # so previous backslash needs to be removed
                pattern = pattern[0:i - 1] + pattern[i:]
                i -= 1
                literal_chars.append(i)
                previous_backslash = False
            elif char == '\\':
                previous_backslash = True
            else:
                previous_backslash = False

            i += 1

        if previous_backslash:
            literal_chars.append(i)

        return pattern, literal_chars

    # . = any single character
    # \ = escape character
    # # = any number
    # ^ = any uppercase character
    # % = any lowercase character
    # & = any special character
    @staticmethod
    def filter_std(std_pattern, string):
        """Custom-made filtering pattern for those who are understandably scared of regex"""
        if type(std_pattern) == str:
            pattern, literal_chars = Filter.process_std_pattern(std_pattern)
        else:
            pattern, literal_chars = std_pattern

        if len(string) != len(pattern):
            return False

        for i in range(0, len(string)):
            pattern_char = pattern[i]
            string_char = string[i]
            string_ord = ord(string_char)

            if pattern_char not in Filter.op_chars or i in literal_chars:
                if pattern_char != string_char:
                    return False
            else:
                # pattern_char is an op
                if pattern_char == '.':
                    continue
                if pattern_char == '#':
                    if not 48 <= string_ord <= 57:
                        return False
                if pattern_char == '^':
                    if not 65 <= string_ord <= 90:
                        return False
                if pattern_char == '%':
                    if not 97 <= string_ord <= 122:
                        return False
                if pattern_char == '&':
                    if 48 <= string_ord <= 57 \
                            or 65 <= string_ord <= 90 \
                            or 97 <= string_ord <= 122:
                        return False
        return True
