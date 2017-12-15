#!/usr/bin/env python3

import argparse
from fountainutils import FountainToPDF


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "Generates a formatted PDF file from a .fountain file.")

    parser.add_argument("file", help="Fountain screenplay to convert to PDF.", metavar="INPUT_FILENAME")
    parser.add_argument("-o", "--output", dest="out", help="Filename for the output PDF file.", metavar="OUTPUT_FILENAME")
    args = parser.parse_args()

    if args.out is None:
        args.out = "./out.pdf"

    converter = FountainToPDF(args.file)
    converter.generatePDF(args.out)
