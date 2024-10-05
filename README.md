About

What this program does:

I. Initiates a search for files in the path specified by the user.

II. For each file found, it creates a formatted dictionary containing the file's attributes. It also adds a SHA256 hash attribute and a classification attribute categorizing the file into one of the following categories:

    Configuration file
    Linux shell script
    Source file for programming languages
    Bytecode for programming languages
    Windows executable
    Windows batch file
    Windows PowerShell script
    Windows Office document
    Media file
    Other binaries

III. At the end of the search, two reports are generated:

    summary.json: a summary of the results.
    attributes.json: details about each file found.

Running

To run the program, invoke the Python interpreter, specify the program name, and include a --path flag followed by the path (without quotes) of the directory you wish to search:

Example:

    python3 arqrel.py --path [insert path]

To print each file found by the program to the terminal, pass the -v (or --verbose) flag:

    python3 arqrel.py -v --path [insert path]
