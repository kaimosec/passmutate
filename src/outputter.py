class Outputter:
    """Standardizes outputting to both file and stdout"""
    def __init__(self, filename):
        if filename == '-':
            self.is_file = False
        else:
            self.is_file = True
            self.file = open(filename, 'w')

        self.output_count = 0

    def output(self, line):
        self.output_count += 1
        if self.is_file:
            self.file.write(line+'\n')
        else:
            print(line)

    def close(self):
        if self.is_file:
            self.file.close()
