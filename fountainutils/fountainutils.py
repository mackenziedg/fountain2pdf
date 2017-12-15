import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_LEFT, TA_CENTER 
from reportlab.lib.units import inch

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

        self.styles = {
            'ACTION': ParagraphStyle(
                'ACTION',
                fontName='Courier',
                fontSize=12,
                allowWidows=1,
                allowOrphans=1,
                leftIndent=0,
                rightIndent=0,
                alignment=TA_LEFT
            ),
            'CENTERED': ParagraphStyle(
                'CENTERED',
                fontName='Courier',
                fontSize=12,
                leftIndent=0,
                rightIndent=0,
                alignment=TA_CENTER
            ),
            'SCENE': ParagraphStyle(
                'SCENE',
                fontName='Courier',
                fontSize=12,
                leftIndent=0,
                rightIndent=0,
                alignment=TA_LEFT
            ),
            'CHARACTER': ParagraphStyle(
                'CHARACTER',
                fontName='Courier',
                fontSize=12,
                leftIndent=2.0*inch,
                rightIndent=0,
                alignment=TA_LEFT
            ),
            'DIALOG': ParagraphStyle(
                'DIALOG',
                fontName='Courier',
                fontSize=12,
                leftIndent=1.0*inch,
                rightIndent=1.5*inch,
                alignment=TA_LEFT
            ),
            'PARENTHETICAL': ParagraphStyle(
                'PARENTHETICAL',
                fontName='Courier',
                fontSize=12,
                leftIndent=1.5*inch,
                rightIndent=2.0*inch,
                alginment=TA_LEFT
            ),
            'TRANSITION': ParagraphStyle(
                'TRANSITION',
                fontName='Courier',
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
        for ix, line in enumerate(lines):
            token = None
            # Process forced elements first
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
                # TODO: Markdown-like text formatting (bold, italics etc.) to come later

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
            canvas.setFont('Courier',12)
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