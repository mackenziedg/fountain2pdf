#!/usr/bin/env python3

import argparse
import re
from matplotlib.font_manager import findSystemFonts
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.units import inch
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont, TTFError


class FountainToPDF:

    def __init__(self, path=None):
        """Loads in a .fountain file from a path and tokenizes it.

        Parameters
        ----------
        path -- String path to .fountain file to be converted. (optional)
        """

        if path is not None:
            self.read_file(path)
        else:
            self.lines = None

        try:
            font_locations = findSystemFonts()
            for font in font_locations:
                if font.endswith("Courier Prime.ttf"):
                    courier_prime_loc = font
                elif font.endswith("Courier Prime Bold.ttf"):
                    courier_prime_bold_loc = font
                elif font.endswith("Courier Prime Italic.ttf"):
                    courier_prime_italic_loc = font
                elif font.endswith("Courier Prime Bold Italic.ttf"):
                    courier_prime_bold_italic_loc = font

            pdfmetrics.registerFont(TTFont('Courier Prime', courier_prime_loc))
            pdfmetrics.registerFont(TTFont('Courier Prime Bold', courier_prime_bold_loc))
            pdfmetrics.registerFont(TTFont('Courier Prime Italic', courier_prime_italic_loc))
            pdfmetrics.registerFont(TTFont('Courier Prime Bold Italic', courier_prime_bold_italic_loc))
            self.fontname = 'Courier Prime'
            self.fontname_bold = 'Courier Prime Bold'
            self.fontname_italic = 'Courier Prime Italic'
            self.fontname_bold_italic = 'Courier Prime Bold Italic'
            pdfmetrics.registerFontFamily(self.fontname, normal=self.fontname, bold=self.fontname_bold, italic=self.fontname_italic, boldItalic=self.fontname_bold_italic)
            print("Using Courier Prime.")
            
        except TTFError:
            self.fontname = 'Courier'
            self.fontname_bold = 'Courier'
            self.fontname_italic = 'Courier'
            self.fontname_bold_italic = 'Courier'
            print("Courier Prime not found. Using Courier.")
            
        self.styles = {
            'TITLE': ParagraphStyle(
                'TITLE',
                fontName=self.fontname,
                fontSize=12,
                alignment=TA_CENTER
            ),

            'CREDIT': ParagraphStyle(
                'CREDIT',
                fontName=self.fontname,
                fontSize=12,
                alignment=TA_CENTER
            ),

            'AUTHOR': ParagraphStyle(
                'AUTHOR',
                fontName=self.fontname,
                fontSize=12,
                alignment=TA_CENTER
            ),

            'SOURCE': ParagraphStyle(
                'SOURCE',
                fontName=self.fontname,
                fontSize=12,
                alignment=TA_CENTER
            ),

            'DRAFT_DATE': ParagraphStyle(
                'DRAFT_DATE',
                fontName=self.fontname,
                fontSize=12,
                alignment=TA_RIGHT
            ),

            'CONTACT': ParagraphStyle(
                'CONTACT',
                fontName=self.fontname,
                fontSize=12,
                alignment=TA_LEFT
            ),

            'ACTION': ParagraphStyle(
                'ACTION',
                fontName=self.fontname,
                fontSize=12,
                allowWidows=1,
                allowOrphans=1,
                leftIndent=0,
                rightIndent=0,
                alignment=TA_LEFT
            ),

            'CENTERED': ParagraphStyle(
                'CENTERED',
                fontName=self.fontname,
                fontSize=12,
                leftIndent=0,
                rightIndent=0,
                alignment=TA_CENTER
            ),

            'SCENE': ParagraphStyle(
                'SCENE',
                fontName=self.fontname,
                fontSize=12,
                leftIndent=0,
                rightIndent=0,
                alignment=TA_LEFT
            ),

            'CHARACTER': ParagraphStyle(
                'CHARACTER',
                fontName=self.fontname,
                fontSize=12,
                leftIndent=2.0*inch,
                rightIndent=0,
                alignment=TA_LEFT
            ),

            'DIALOG': ParagraphStyle(
                'DIALOG',
                fontName=self.fontname,
                fontSize=12,
                leftIndent=1.0*inch,
                rightIndent=1.5*inch,
                alignment=TA_LEFT
            ),

            'PARENTHETICAL': ParagraphStyle(
                'PARENTHETICAL',
                fontName=self.fontname,
                fontSize=12,
                leftIndent=1.5*inch,
                rightIndent=2.0*inch,
                alginment=TA_LEFT
            ),

            'TRANSITION': ParagraphStyle(
                'TRANSITION',
                fontName=self.fontname,
                fontSize=12,
                leftIndent=4.0*inch,
                rightIndent=0,
                alignment=TA_LEFT
            )
        }   

    def read_file(self, path):
        """Reads in and tokenizes a .fountain file
        
        Parameters
        ----------
        path -- String file path to .fountain file to be converted
        """
        with open(path) as f:
            lines = f.readlines()
        self.lines = [line.strip("\n") for line in lines]
        self.tokenized_lines = self._tokenize(self.lines)

    def _format_line(self, line):
        """Replaces Markdown-style formatting with HTML-style formatting for reportlab to use.
       
        Parameters
        ----------
        line -- A string corresponding to the current line

        Returns
        -------
        line -- The same line with Markdown-style formatting swapped for HTML-style formatting
        """
        bi_reg = re.compile(r"([^\\]|^)(\*{3}.*?[^ \\]\*{3})")
        bd_reg = re.compile(r"([^\\]|^)(\*{2}.*?[^ \\]\*{2})")
        it_reg = re.compile(r"([^\\]|^)(\*.*[^ \\]\*)")
        ul_reg = re.compile(r"([^\\]|^)(_.*[^ \\]_)")

        regs = [bi_reg, bd_reg, it_reg, ul_reg]
        subs = [
            ['<b><i>', '</i></b>', 3],
            ['<b>', '</b>', 2],
            ['<i>', '</i>', 1],
            ['<u>', '</u>', 1]
        ]
        reg_dict = dict(zip(regs, subs))

        for reg in regs:
            opening = reg_dict[reg][0]
            closing = reg_dict[reg][1]
            length = reg_dict[reg][2]

            fi = re.findall(reg, line)
            if fi:
                for match in fi:
                    sub = match[1]
                    formatted_sub = opening + sub[length:-length] + closing 
                    line = line.replace(sub, formatted_sub)
        return line

    def _format_meta(self, meta):
        """Formats metadata (ie. title, author etc.)

        Parameters
        ----------
        meta -- List of metadata

        Returns
        -------
        meta_out -- List of (string, token) values
        """

        # TODO: Not properly reading values with the data not on the same line as the token
        meta_out = []
        token_dict = {
            'Title': 'TITLE',
            'Author': 'AUTHOR',
            'Credit': 'CREDIT',
            'Source': 'SOURCE',
            'Draft date': 'DRAFT_DATE',
            'Contact': 'CONTACT'
        }
        current_token = None
        data = []
        for line in meta:
            temp_token = current_token
            current_token = token_dict.get(line.split(':')[0], current_token)
            if temp_token != current_token and temp_token:
                meta_out.append(('\n'.join([i.strip() for i in data if i]), temp_token))
                data = []
                line = line[len(current_token)+2:]
                data.append(line)
            else:
                data.append(line)

        return meta_out

    def _tokenize(self, lines):
        """Tokenizes lines of the read-in .fountain file.

        Parameters
        ----------
        lines -- Array of strings where each string is the contents of one line

        Returns
        -------
        tokens -- A list of (line, token) pairs for each line in the file
        

        The method for identifying each type of line was taken from https://fountain.io/syntax
        It is current as of Fountain v1.1
        """

        def is_scene_heading(line, prev, fol):
            return line.isupper() and re.match("(^INT.|^EXT.)", line) and not (prev or fol)

        def is_character(line, prev, fol):
            return line.isupper() and not line.startswith('>') and (not prev and fol)

        def is_transition(line, prev, fol):
            return line.isupper() and line.endswith("TO:") and not (prev or fol)

        def is_section_header(line, prev, fol):
            return line.startswith("#")

        def is_centered(line, prev, fol):
            return line.startswith(">") and line.endswith("<")

        def is_right_aligned(line, prev, fol):
            return line.startswith(">") and not line.endswith("<")

        def is_parenthetical(line, prev, fol):
            return line.startswith("(") and line.endswith(")")
            
        tokens = []

        dialog_flag = False
        meta_flag = False
        meta_info = []
        for ix, line in enumerate(lines):
            if (meta_flag and line) or (ix == 0 and re.match("^Title:", line)):
                meta_flag = True               
                meta_info.append(line)                
                continue
            elif (meta_flag and not line):
                meta_flag = False
                tokens = self._format_meta(meta_info)
                continue

            # Process forced elements first
            token = None
            if re.match("^@", line):
                token = "CHARACTER"
            elif re.match("^\.", line):
                token = "SCENE"
            elif re.match("^!", line):
                token = "ACTION"
            elif re.match("^~", line):
                token = "LYRIC"
            elif re.match("\[\[.*\]\]", line):
                token = "NOTE"
            elif re.match("^=", line):
                token = "SYNOPSE"
            elif re.match(">.*[^<]$", line):
                token = "TRANSITION"

            if token is not None:
                line = line[1:]

            # Get previous and following line, since most elements depend
            # on whether some combo of these are empty
            prev = lines[ix - 1] if ix > 0 else ''
            fol = lines[ix + 1] if ix < len(lines) - 1 else ''

            # Strip the lines, since only action elements can have leading whitespace
            stline = line.strip()
            stprev = prev.strip()
            stfol = fol.strip()

            # If we had a forced token, skip the redundant checking
            # TODO: Combine the forced-token-checking to avoid stripping every line no matter what
            if token is not None:
                pass

            # otherwise, check away!
            elif not line:
                dialog_flag = False
                token = ''
            elif is_scene_heading(stline, stprev, stfol):
                token = "SCENE"
            elif is_character(stline, stprev, stfol):
                token = "CHARACTER"
            elif is_transition(stline, stprev, stfol):
                token = "TRANSITION"
            elif is_section_header(stline, stprev, stfol):
                token = "SECTION"
            elif is_parenthetical(stline, stprev, stfol):
                token = "PARENTHETICAL"
            else:
                token = "DIALOG" if dialog_flag else "ACTION"

            # Only action lines have leading whitespace
            if token != "ACTION":
                line = stline
            else:
                if is_centered(line, prev, fol):
                    line = line[1:-1].strip()
                    token = "CENTERED"

            line = self._format_line(line)

            # Characters have dialog following them
            if token == "CHARACTER":
                # Add dual-dialog support later
                # if line.endswith("^"):
                    # token = "CHARACTERDD"
                dialog_flag = True

            tokens.append((line, token))

        return tokens

    def generatePDF(self, path="out.pdf"):
        """Create a .pdf file from the tokenized lines of the input .fountain file.
        
        Parameters
        ----------
        path -- String file path for the output file

        The formatting rules were taken from https://www.writersstore.com/how-to-write-a-screenplay-a-guide-to-scriptwriting/
        """

        def addPageNums(canvas, doc):
            canvas.saveState()
            canvas.setFont(self.fontname, 12)
            canvas.drawString(7.5*inch, 10.5*inch, "{}.".format(doc.page))
            canvas.restoreState()

        doc = SimpleDocTemplate(path, leftMargin=1.5*inch, rightMargin=inch, topMargin=inch, bottomMargin=inch, pagesize=letter)
        emptyline = Spacer(1, (1/6)*inch)
        story = []
        for line in self.tokenized_lines:
            if line[1] not in ["SECTION", "SYNOPSE", "NOTE"]:
                text = line[0]
                token = line[1]

                if not token:
                    story.append(emptyline)
                else:
                    style = self.styles.get(token, 'ACTION')
                    p = Paragraph(text, style)
                    story.append(p)

        doc.build(story, onLaterPages=addPageNums)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description = "Generates a formatted PDF file from a .fountain file.")

    parser.add_argument("file", help="Fountain screenplay to convert to PDF.", metavar="INPUT_FILENAME")
    parser.add_argument("-o", "--output", dest="out", help="Filename for the output PDF file.", metavar="OUTPUT_FILENAME")
    args = parser.parse_args()

    if args.out is None:
        args.out = "./out.pdf"

    converter = FountainToPDF(args.file)
    converter.generatePDF(args.out)
