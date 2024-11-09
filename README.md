## About
*What this program does:*

**I.** Initiates a search for files in the path specified by the user.

**II.** For each file found, it creates a formatted dictionary containing the file's attributes. It also adds a SHA256 hash attribute and a classification attribute, based on file extension.

**III.** At the end of the search, two reports are generated:<br>
+ summary.json: a summary of the results.<br>
+ attributes.json: attributes details for each file found.<br>

## Running
Every program run must include the "--path" flag followed by the path to a valid directory<br>

Example:

**1. basic running:**
```sh
python3 arqrel.py --path [insert path]
```
**2. using relative path and real time logging:**
```sh
python3 arqrel.py -v --path .
```
