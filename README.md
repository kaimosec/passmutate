PassMutate
=======
![](https://img.shields.io/badge/build-passing-brightgreen) ![](https://img.shields.io/badge/license-GPL%203-blue) ![](https://img.shields.io/badge/passmutate-v1.0-blue)

PassMutate is a tool that enhances the efficacy of any given
wordlist (AKA password list) for brute-forcing passwords in the pentesting field.

It also aids in the management and creation of wordlists.

Its main use is the mutation of passwords in a wordlist to increase the
size and "fill in the gaps" of that wordlist. Mutation works by
expanding on every password in a wordlist and creating similar variations of those passwords.

A good example of why mutation is useful is the cewl tool. Cewl scrapes
a website and generates a wordlist. If the password to mycarshop.com is
ford123, cewl may find "ford" on a webpage but will never get "ford123". Combining cewl
with passmutate "fills in the gaps" to increase the likeliness of a
correct guess.

Even the famed rockyou could benefit from mutation, allowing you to not only guess its passwords but adjacent passwords
as well, that almost certainly exist in the real world but haven't been scraped yet
(e.g Jessica@ and Jessica! may be in the wordlist but not Jessica1, which can be added automatically via mutation).

# Features
- Mutate wordlists
- Filter down wordlists based on length, charset, ascii, regex and standard filter
- Sort wordlists by alphabet or efficacy
- Analyze a wordlist and print statistical information
- Take input from a file or stdin
- Output to a file or stdin
- Merge wordlists
- Pick out n number of distributed samples from wordlist

# How Mutation Works

Mutation works by altering a password into more passwords to "fill out the gaps" of a wordlist and increase the chance
of getting a hit when brute forcing.

For example, if your password list consists of:

```
apple
banana
cherry
```

Mutating the list could result in:

```
apple
Apple
APPLE
apple1
apple2
...
Banana123
Banana123!
...
CHERRY
CHERRY!
...
```

When passwords are mutated, every possible combination of mutation functions for all possible orders and lengths are
used against every password while removing duplicates in real-time.

# Requirements
- Python3 (tested only on Windows + Debian Linux)
- alive-progress >=2.1.0

# Installation
1. Ensure alive-progress is installed with *python3 -m pip install alive-progress*
2. Download and run with *python3 mutate.py*

# Usage
```commandline
> python3 mutate.py

      _____              __  __       _        _       
     |  __ \            |  \/  |     | |      | |      
     | |__) |_ _ ___ ___| \  / |_   _| |_ __ _| |_ ___ 
     |  ___/ _` / __/ __| |\/| | | | | __/ _` | __/ _ \
     | |  | (_| \__ \__ \ |  | | |_| | || (_| | ||  __/
     |_|   \__,_|___/___/_|  |_|\__,_|\__\__,_|\__\___|   v1.0
                        By Kaimo
            
usage: mutate.py [-h] [-i FILE] [-a ANALYZE_FILE] [-m MUTATE_LEVEL] [-s SORT] [-o OUTPUT] [-f STD_FILTER]
                 [-r REG_FILTER] [-l LEN_FILTER] [-x] [-c CHAR_FILTER] [-p PICK_NUM] [-q] [-v] [--ignore]
                 [--tmp-dir TEMP_DIR]

optional arguments:
  -h, --help          show this help message and exit

Modes of operation:
  -i FILE             process FILE. 'FILENAME' to grab 1 file, 'FILENAME1,FILENAME2,...' to grab multiple, './*.txt'
                      to grab all .txt files in the folder or '-' for stdin
  -a ANALYZE_FILE     Analyze wordlist ANALYZE_FILE. Can analyze multiple files together as shown in -i

General processing options:
  -m MUTATE_LEVEL     Mutate passwords for level of complexity 0, 1 or 2
  -s SORT             Sort wordlist (a)lphabetically or by (e)fficacy (-s a, -s e). -o must be a filename
  -o OUTPUT           Output to save to. Filename or - for stdout

Wordlist filtering:
  -f STD_FILTER       Filter wordlist using standard filter (see docs)
  -r REG_FILTER       Filter wordlist with regex
  -l LEN_FILTER       Filter wordlist by length(s) (e.g. 7 for 7 chars, 7:9 for between 7 and 9 chars, inclusive)
  -x                  Filter passwords that only contain standard ascii characters (e.g. A-Z a-z 0-9 !@#$^&...)
  -c CHAR_FILTER      Filter wordlist using a charset (e.g. -c "abcdefg")
  -p PICK_NUM         Pick out PICK_NUM distributed passwords from a wordlist

General options:
  -q, --quiet         Run with no unnecessary output. Enabled automatically when outputting to stdout
  -v, --verbose       Print verbose information
  --ignore            Ignore warnings about insufficient disk-space, etc.

Advanced options:
  --tmp-dir TEMP_DIR  Set the temporary directory
```

# Arguments that require further explanation

### -i FILE
-i can take in multiple files in different ways.

*Note: -a (for analysis) works in the same way.*

**Load a single file:**  
-i file.txt

**Load multiple files, separated by comma:**  
-i file1.txt,file2.txt

**Load multiple files using a glob statement (https://en.wikipedia.org/wiki/Glob_(programming)):**  
(Will load all text files in current folder that start with 'list')  
*Note that glob strings must be encased in quotes*  
-i "list*.txt"

### -m 0,1,2

Mutate a password with level 0, 1 or 2.

Level 0 generates ~60 unique passwords per password.  
Level 1 generates ~350 unique passwords per password.  
Level 2 generates ~24,200 unique passwords per password.

**NOTE: For this reason, level 2 should only be used for very powerful computers.**

### -r REGEX_PATTERN

Filter passwords by regex. Any passwords, generated or otherwise that do not match the pattern will not be outputted.

### -f STRING

Filter passwords using a custom made filter similar to Crunch.

. = any single character  
&#35; = any number  
^ = any uppercase character  
% = any lowercase character  
& = any special character  
Escape a character with backslash \

For example: **-f "...ket&#35;&#35;&"** means filter only by words that start with any 3 characters, then the letters
ket, then any 2 numbers, then a special character.  
So, something like ticket69! would make it through.

### -c STRING

Filter passwords by a charset. For example, if **-c abc123**, if a password has a character in it that is not a, b, c,
1, 2 or 3, it will be filtered out.

### -s a,e

Sort the resultant wordlist either alphabetically or by efficacy, respectively.

Sorting by efficacy means that passwords considered most likely to be THE password will be further towards
the top, while unlikely passwords are pushed to the bottom. Sorting by efficacy is recommended if what
you're brute forcing is speed-limited.  

A password's efficacy is calculated using statistics on password types and lengths.  
If, for example, a password has an unusual length, is not lowercase or has numbers or characters at its end, it's considered to be
less likely to be THE password, depending on the combination of those factors.

**NOTE:** Sorting uses far more disk space (initial_filesize * mutation_rate * 3). This space is only taken up during
the sorting process.

**NOTE:** Sorting can only be used when outputting to a file (e.g. -o filename.txt).

### -p PICK_NUM
Pick PICK_NUM passwords out of a wordlist (or multiple wordlists) and output to -o.

*Note: Picking is done after all mutating and filtering*

If the total passwords cannot be predetermined (e.g. picking passwords out of stdin instead of a file), it will pick
PICK_NUM passwords in random order and do its best to ensure they're evenly distributed.

Otherwise, the picks will always be in order and evenly distributed accurately.

### --tmp-dir=DIR
Store temporary files in DIR. If undefined, temporary files will be stored in /tmp. If /tmp doesn't exist, temporary
files will be stored in PROJECT_DIR/tmp.

#Examples
Mutate a wordlist into a bigger wordlist with basic mutation:

```commandline
python3 mutate.py -i rockyou.txt -m 0 -o new_rockyou.txt
```

Analyze a wordlist:

```commandline
python3 mutate.py -a rockyou.txt
```

Filter down a wordlist by passwords that contain only specific characters:

```commandline
python3 mutate.py -i rockyou.txt -c "あいうえおかき..." -o new_rockyou.txt
```

Sort a wordlist by efficacy

```commandline
python3 mutate.py -i rockyou.txt -s e -o new_rockyou.txt
```

Merge 2 wordlists

```commandline
python3 mutate.py -i list1.txt,list2.txt -o new_list.txt
```

Pick out 1000 evenly distributed passwords from a wordlist
and output to stdout:

```commandline
python3 mutate.py -i rockyou.txt -p 1000 -o -
```

Mutate 2 wordlists at once, filter them by ascii only and lengths between 8-10 characters, then sort it by efficacy
and save to a single wordlist:

```commandline
python3 mutate.py -i rockyou.txt,mywordlist.txt -m 0 -x -l 8:10 -s e -o new_rockyou.txt
```

A website only allows users to have a password 8-16
characters long, all ascii, with one special character and one number.
Brute force from rockyou.txt, only guessing passwords that meet this
criteria, without creating an extra wordlist:

```commandline
python3 mutate.py -i rockyou.txt -l 8:16 -x -r "(?=[0-9])(?=[^A-Za-z0-9])" -o - | hydra ...
```

Pipe through a previously-known password, mutate it into ~24,200 similar passwords and pipe it through to john:  
(This will run with no disk usage)

```commandline
echo "mypassword123" | python3 mutate.py -i - -m 2 -o - | john ...
```

Generate passwords via crunch and pipe through the output, mutate them, filter by
passwords that both end in 1 special character and are between 10 and 12
characters long, then pipe those straight into hydra:

```commandline
crunch 8 8 "abcd0123456789!@" | python3 mutate.py -i - -m 0 -l 10:12 -r "[^A-Za-z0-9]{1}$" -o - | hydra ...
```

Take in all wordlists in the current folder with the word "wordlist" in it,
mutate them, filter by passwords that are only ascii characters, are
between 5-12 characters long and have a first uppercase character, sort
resultant passwords by efficacy, then pick out 1000 evenly distributed
passwords from the results and save that to a new file:

```commandline
python3 mutate.py -i "./*wordlist*" -m 0 -x -l 5:12 -r "^[A-Z]{1}" -s e -p 1000 -o new_wordlist.txt
```

# Limitations

Mutating at level 2 is currently slow at 1/3 normal mutation speed.

Although no duplicates should be made **per password** in the file, duplicates may still arise depending on
what passwords are in the wordlist. For example, if "jessica" and "jessica1" are in the same wordlist, crossover
mutations will result in some duplicates. Removing these duplicates would sacrifice speed, RAM and/or disk usage.
I might look into a solution next version.

Sorting requires disk usage as it uses an algorithm that splits up a wordlist and sorts in chunks. It is done this way
to increase speed and reduce RAM usage when sorting very large wordlists.

Temporary files such as the log and temporary wordlist files (only present when sorting) are temporarily stored in the
project's tmp directory and deleted soon after, but they aren't wiped, meaning the working log and temporary wordlist
files are recoverable. If you don't want this, adjust the temporary directory path with --tmp-dir=PATH to either
/dev/null or some kind of RAM-based file system.

# Disclaimer
This tool is for educational purposes only.

# Contact
You can email me at kaimo.sensei@protonmail.com

# Special Thanks
- Freudenstein - Testing
- Benchi - Code for sorting large files (https://github.com/benchi/big_file_sort)

# Boring Stuff

## How does mutation work?

Mutation works by taking a single password and creating many similar variations out of it.

It starts by taking a list of mutator functions (i.e. a function that takes a string and alters it in some way).  
For example, the set of mutator functions for -m 0 is:

```python
[
    [
        Augmentor.upper,  # Convert to uppercase
        Augmentor.lower,  # Convert to lowercase
        Augmentor.firstupper,  # Convert first character to uppercase
    ],

    [Augmentor.remove_numbers_at_end],
    [Augmentor.remove_specs_at_end],

    ['>123'] + [">{}".format(i) for i in range(0, 10)] +  # Add 123, 0, 1, 2.. to end of string if number isn't at end
    ["!{}".format(x) for x in ['!', '@', '#', '$', '%', '^', '&', '*', '(', ')']], # Likewise but for special characters
]
```
It then uses such a list to generate every possible combination of those elements for all orders and lengths,
while avoiding combinations that contain more than 1 element from the same section or sublist
(converting to uppercase then converting to lowercase in the same combination wouldn't make sense)
and avoiding duplicate mutations.

When mutating, it will iterate through every possible combination of these functions to mutate passwords. Such
combinations may look like:

```
[Augmentor.upper],
[Augmentor.firstupper, remove_numbers_at_end],
[Augmentor.firstupper, remove_numbers_at_end, '>2'],
[Augmentor.lower, remove_numbers_at_end, '!!']
```

A password mutates through every combination to create a new password. For example, the above combinations would create
the below passwords if mutating from **password1**.

```
PASSWORD1
Password
Password2
password!
```

Mutate settings 1 and 2 are similar but contain more in-depth mutation functions to create many more combinations.
They can be viewed in augmentor.py.

The approximate mutation rates (i.e. how many passwords are created from a single password) are:

**Level 0:** 1:60  
**Level 1:** 1:350  
**Level 2:** 1:24,200

## How does Sorting by efficacy work?

Sorting by efficacy means that passwords considered most common are sorted to the top. This should prove useful when
brute-forcing targets cannot be done at full speed (e.g. testing a remote server vs. a local hash).

It determines how common a password would be by comparing its features (e.g. does it have uppercase characters?
Does it end in a special character? How long is the password?).

Specifically it looks at the **combination** of features for a password and looks at how common passwords are with that
exact combination of features.

rockyou.txt was used for analysis. If we analyze the password **k1ckme123!**, it has the following features:

- Is 10 characters long    
- all lowercase (as compared to uppercase)
- contains "leet" characters
- contains numbers
- Ends in a special character

We might find, for example, that only 0.02% of rockyou.txt's passwords have this exact combination of features,
meaning it's a relatively uncommon combination and will thus be sorted accordingly.

By analyzing the probability of every possible combination of a password's features, a more accurate sorting
algorithm is achieved, albeit with a reduction in sorting speed.

Of course, sorting accuracy is limited to the features of a password, not the password itself, so it cannot
differentiate "password" from "aienhpof", for example, as their features are identical.

Here's an example of a wordlist before and after sorting by efficiency:

```
Before                              After
---------------                     ---------------
!!!5539o679!!!                      castillo
0109381602                          malditas
mara                                katlyn
*7¡Vamos!                           buddie32
malditas                            buddy3558
cxz                                 0109381602
castillo                            CELTIC
CELTIC                              mara
katlyn                              cxz
buddie32                            !!!5539o679!!!
buddy3558                           *7¡Vamos!
```

It may be surprising to see "CELTIC", "mara" and "cxz" so low but short passwords and uppercase passwords are
quite rare in rockyou.txt