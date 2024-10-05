## About
*What this program does:*

**I.** Initiates a search for files in the path specified by the user.

**II.** For each file found, it creates a formatted dictionary containing the file's attributes. It also adds a SHA256 hash attribute and a classification attribute, based on file extension.

**III.** At the end of the search, two reports are generated:<br>
+ summary.json: a summary of the results.<br>
+ attributes.json: attributes details for each file found.<br>

## Running
To run the program, invoke the Python interpreter, specify the program name, and include a --path flag followed by the path (no quotes) of the directory you wish to search:

**Example:**
```sh
python3 arqrel.py --path [insert path]
```
**Example 2 (verbose mode):**
```sh
python3 arqrel.py -v --path [insert path]
```
