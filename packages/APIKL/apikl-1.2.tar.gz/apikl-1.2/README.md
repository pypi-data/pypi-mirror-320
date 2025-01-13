# API Key Locator (APIKL) #

## What is this? ##
This module allows you to find API keys and passwords in your project. \
In short, it uses regular expressions to find suspicious strings and Shannon’s entropy prove that they are API keys.\
This module successfully finds not only API keys but also passwords.\
It doesn't use any web services so your API keys are in safe, you may check all the code in my GitHub. 

## Quick Guide ##
The module is based on the following structure:

    files = ['...']
    probability = 6
    locator = APIKL(files, probability)
    locator.find_keys()

***files*** is for files you want to check *(blank to check the current folder)*\
***probability*** defines level of keys to show *(from 1 to 10, 5 is default)*

----------


### Using ###

Using the library is as simple and convenient as possible:

First, import everything from the library (use the `from `...` import *` construct).

Examples of all operations:

Finding keys in *files_to_check*  `find_keys(files_to_check: list)` \
If *files_to_check* is blank, it will check for keys in _locator.files_to_check_ which is defined in constructor

    files = ['path/to/file1', 'path/to/file2']
    locator.find_keys(files)



----------
## Troubleshooting ##
This module doesn't pose much of a problem since it's quite simple. But there's one issue that cannot be fixed.

    APIKL(['C:\Users\User\Desktop\database.xml'], 6).find_keys()

You may get `SyntaxError: (unicode error) 'unicodeescape' codec can't decode bytes in position 2-3: 
truncated \UXXXXXXXX escape`. In this case just place "r" before your path to replace it with raw string.
Example: 

    APIKL([r'C:\Users\User\Desktop\database.xml'], 6).find_keys()





## Developer ##
My site: https://github.com/VitalyKalinsky