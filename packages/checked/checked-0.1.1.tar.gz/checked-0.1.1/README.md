# Checked - CLI

A simple command-line application to convert HTML files (made by exporting Proton Documents to HTML) to Spreadsheets (using the `ODS` format). Made for the Fact-Checking Process at [Fumaça](https://fumaca.pt).

## Installation

1. Install using `pip`: `pip install checked`;

## Usage

```bash
usage: checked-cli [-h] [-l {EN,PT}] file

A simple CLI app to convert HTML files to Spreadsheets, for Fact-Checking

positional arguments:
  file                  The HTML file to be converted

options:
  -h, --help            show this help message and exit
  -l, --language {EN,PT}
                        Language for column headers (default: EN)

```

You can use this application by writing in your terminal: `checked-cli [DOCUMENT NAME]`. You may optionally select another language for your Fact-Checking table, using the `-l` flag.

## QOL before Version 1

- [ ] GUI Application;
- [ ] Add dropdown options for Status and Confirmation;
- [ ] Add customizable target for tables (i.e. all of the quotes on a document);
- [ ] Package for Windows and MacOS;


## Assumptions

1. File is an HTML file;
2. File has multiple paragraphs;
3. File name does not include spaces;
4. Target paragraphs for Fact-Checking are indented (`padding-inline-start: 40px;`);

## Result

You will get a file with the following Columns (in Portuguese or English):

|Status|Fact|Confirmation|Source|Notes|Revision|
|---|---|---|---|---|---|
