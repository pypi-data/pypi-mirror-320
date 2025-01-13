# Project Summary:
This is an application for (manually) tracking the user's financial transactions, and generating reports in a manner which makes them easy to declare for taxes.

## Features:
This application supports:
  * A simple GUI, written in Qt for Python.
  * Local storage to an SQLite database.
  * The operating-systems of MacOS and Linux (tested on the Ubuntu22 platform).
  * Well-validated entry of financial transactions, in a manner similar to the use of a checkbook.
  * Generation of printable reports, summarizing the records from a given timespan.
  * Searching of existing records by date, categories, or name.
  * User-definition of transaction-categories, for flexible data-grouping.

This application does *not* support:
  * Cloud-storage.
  * Windows OS.

## Initial Setup On Mac

1. run `python3 -m venv env`
2. run `source env/bin/activate`
3. run `pip install PySide6`
4. Need to select the .venv interpreter in VS code using command-shift-p
5. alternately, you can execute the correct python version with `./env/bin/python`