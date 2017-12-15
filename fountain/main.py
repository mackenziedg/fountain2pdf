import re
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import letter
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.lib.units import inch

class FountainToPDF:

    def __init__(self, path=None):
        if path is not None:
            self.read_file(path)

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
        with open(path) as f:
            lines = f.readlines()
        self.lines = [line.strip("\n") for line in lines]
        self.lines = self._tokenize()

    def _tokenize(self):

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
        for ix, line in enumerate(self.lines):
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
            prev = self.lines[ix - 1] if ix > 0 else ''
            fol = self.lines[ix + 1] if ix < len(self.lines) - 1 else ''

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

                # TODO: Markdown-like formatting to come later

            # Characters have dialog following them
            if token == "CHARACTER":
                # Add dual-dialog support later
                # if line.endswith("^"):
                    # token = "CHARACTERDD"
                dialog_flag = True

            tokens.append((line, token))

        return tokens

    def generatePDF(self, path):

        def addPageNums(canvas, doc):
            canvas.saveState()
            canvas.setFont('Courier',12)
            canvas.drawString(7.5*inch, 10.5*inch, "{}.".format(doc.page))
            canvas.restoreState()

        doc = SimpleDocTemplate(path, leftMargin=1.5*inch, rightMargin=inch, topMargin=inch, bottomMargin=inch, pagesize=letter)
        emptyline = Spacer(1, (1/6)*inch)
        story = []
        for line in self.lines:
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
