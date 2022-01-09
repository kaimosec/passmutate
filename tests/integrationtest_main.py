import os

commands = {
    'Menu': '',

    'Small mutate': '-i ry1k.txt -m 0 -o tmp.txt',
    'Small mutate, quiet': '-i ry1k.txt -m 0 -o tmp.txt --quiet',
    'Small mutate, verbose': '-i ry1k.txt -m 0 -o tmp.txt --verbose',
    'Small mutate to stdout': '-i ry10.txt -m 0 -o -',

    'Medium mutate': '-i ry1k.txt -m 1 -o tmp.txt',

    'Large mutate with 1 password': '-i ry1.txt -m 2 -o tmp.txt',
    'Large mutate with 10 passwords': '-i ry10.txt -m 2 -o tmp.txt',

    'Mutate too large to fit': '-i ry.txt -m 2 -o tmp.txt',

    'Filter STD_FILTER .......# to stdout': '-i ry1k.txt -f .......# -o -',
    'Filter Regex "^[A-Z]" to stdout': '-i ry1k.txt -r "^[A-Z]" -o -',
    'Filter Length 5 to stdout': '-i ry1k.txt -l 5 -o -',
    'Filter charset 12345 to stdout': '-i ry1k.txt -c 12345 -o -',

    'Filter by ascii': '-i ry1mil.txt -x -o tmp.txt',

    'Pick out 10 to stdout': '-i ry1k.txt -p 10 -o -',

    'Sort file by alphabet': '-i ry1k.txt -s a -o tmp.txt',
    'Sort file by alphabet, use /tmp as tmp dir': '-i ry1k.txt -s a -o tmp.txt --tmp-dir=/tmp',
    'Analyze file': '-a tmp.txt',

    'Sort file by efficacy': '-i ry1k.txt -s e -o tmp.txt',
    'Analyze file again': '-a tmp.txt',

    'Merge 2 wordlist, length 8, mutate 0': '-i ry1k.txt,ry10k.txt -l 8 -m 0 -o tmp.txt',
    'Glob several wordlists, length 5': '-i "ry*k.txt" -l 5 -o tmp.txt',

    'Mutate -m 0, ends in 2 digits, is ascii, length 6-10, pick 1000, sort efficacy':
        '-i ry10k.txt -m 0 -r "[\\d]{2}$" -x -l6:10 -p 1000 -s e -o tmp.txt',
    'Analyse that': '-a tmp.txt',

    'Try share input and output file:': '-i ry1k.txt -m 0 -o ry1k.txt',
    'Try share comma-delimited input and output file:': '-i ry1k.txt,ry10k.txt -m 0 -o ry1k.txt',
    'Try share glob input and output file:': '-i "ry*.txt" -m 0 -o ry1k.txt',

    'Glob and pick': '-i "ry*k.txt" -p 1000 -o tmp.txt',
    'Glob and sort': '-i "ry*k.txt" -s e -o tmp.txt',
    'Glob, pick and sort': '-i "ry*k.txt" -p 1000 -s e -o tmp.txt',

    'Merge files without doing anything else': '-i "ry*k.txt" -o tmp.txt'

}

for name, args in commands.items():
    os.system("clear")
    print(
        """
        ==============================================================
        {}
            {}
        ==============================================================
        """.format(name, args)
    )
    input("Continue?")
    os.system("python3 mutate.py {}".format(args))
    input("Continue?")
