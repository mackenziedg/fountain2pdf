# Description

Converts a Fountain file into a (more-or-less) properly formatted screenplay. A description of the Fountain syntax can be found [here](https://fountain.io/).

# Usage

1. Clone the repository to your machine.

2. Use `fountain2pdf.py INPUT_FILENAME [-o OUTPUT_FILENAME]` to convert a Fountain-formatted text file into a properly formatted pdf file at `OUTPUT_FILENAME` (default `./out.pdf`)

# Known issues

* Does not format title pages at all

* Does not do rich text formatting (ie. italics, bold, underline etc.) as described in the Fountain specs

* Does not format dual dialogue properly

* There's no error handling or anything, so be careful. It shouldn't delete anything, but just fyi.

All of these will be added... eventually.
