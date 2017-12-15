import re


def tokenize(doc):

    def is_scene_heading(line, prev, fol):
        return line.isupper() and re.match("(^INT.|^EXT.)", line) and not (prev or fol)

    def is_character(line, prev, fol):
        return line.isupper() and not line.startswith('>') and (not prev and fol)

    def is_transition(line, prev, fol):
        return line.isupper() and line.endswith("TO:") and not (prev or fol)

    def is_section_header(line, prev, fol):
        return line.startswith("#")

    tokens = []

    dialog_flag = False
    for ix, line in enumerate(doc):
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
        elif re.match("^\(", line):
            token = "PARENTHETICAL"
        elif re.match("\[\[.*\]\]", line):
            token = "NOTE"
        elif re.match("^=", line):
            token = "SYNOPSE"

        # Get previous and following line, since most elements depend
        # on whether some combo of these are empty
        prev = doc[ix - 1] if ix > 0 else ''
        fol = doc[ix + 1] if ix < len(doc) - 1 else ''

        # Strip the lines, since only action elements can have leading whitespace
        stline = line.strip()
        stprev = prev.strip()
        stfol = fol.strip()

        # If we had a forced token, skip the redundant checking
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
        else:
            token = "DIALOG" if dialog_flag else "ACTION"

        # Only action lines have leading whitespace
        if token != "ACTION":
            line = stline

        # Characters have dialog following them
        if token == "CHARACTER":
            if line.endswith("^"):
                token = "CHARACTERDD"
            dialog_flag = True

        tokens.append((line, token))

    return tokens


def test():
    # Test scene headings
    assert tokenize(["", "INT. WAREHOUSE - DAY", ""])[1][1] == "SCENE"
    assert tokenize(["", "INT. warehouse - DAY", ""])[1][1] == "ACTION"
    assert tokenize(["", "INT. WAREHOUSE - DAY", "t"])[1][1] == "CHARACTER" 
    assert tokenize(["", ".INT. WAREHOUSE - DAY", "t"])[1][1] == "SCENE"

    # Test character names
    assert tokenize(["", "JIM-BOB", "I'm Jim-Bob!"])[1][1] == "CHARACTER"
    assert tokenize(["", "JIM-BOB", "I'm Jim-Bob!"])[2][1] == "DIALOG"
    assert tokenize(["", "@JIM-McBOB", "I'm Jim-McBob!"])[1][1] == "CHARACTER"
    assert tokenize(["", "JIM-McBOB", "I'm Jim-McBob!"])[1][1] == "ACTION"

    # Test dialog
    assert tokenize(["", "@JIM-McBOB", "I'm Jim-McBob!", "This is dialog."])[2][1] == "DIALOG"
    assert tokenize(["", "JIM-BOB", "I'm Jim-Bob!", "This is dialog."])[2][1] == "DIALOG"
    assert tokenize(["", "@JIM-McBOB", "I'm Jim-McBob!", "This is dialog."])[3][1] == "DIALOG"
    assert tokenize(["", "@JIM-McBOB", "I'm Jim-McBob!", "", "This is action."])[4][1] == "ACTION"
    assert tokenize(["", "@JIM-McBOB", "I'm Jim-McBob!", "  ", "This is dialog."])[4][1] == "DIALOG"
    assert tokenize(["", "@JIM-McBOB", "I'm Jim-McBob!", "  ", "This is dialog."])[3][1] == "DIALOG"
    assert tokenize(["", "@JIM-McBOB ^", "I'm Jim-McBob!"])[1][1] == "CHARACTERDD"

    # Test centered text
    assert tokenize(["", "> THE END <", ""])[1][1] == "ACTION"
    assert tokenize(["", "@> THE END <", ""])[1][1] == "CHARACTER"

    # Test lyrics
    assert tokenize(["", "~These are lyrics", ""])[1][1] == "LYRIC"
    assert tokenize(["", "jfkd~These are not lyrics", ""])[1][1] == "ACTION"

    # Test parentheticals
    assert tokenize(["", "(over the hill)", ""])[1][1] == "PARENTHETICAL"

    # Test non-printing text
    assert tokenize(["", "[[this is a note]]", ""])[1][1] == "NOTE"
    assert tokenize(["", "= this is a synopse", ""])[1][1] == "SYNOPSE"
    assert tokenize(["", "# this is an H1", ""])[1][1] == "SECTION"
    assert tokenize(["", "####### this is a very deep heading", ""])[1][1] == "SECTION"


    return "All tests passed."


def main():
    with open("../test.fountain", "r") as f:
        lines = f.readlines()
    lines = [line.strip('\n') for line in lines]

    tokenized = tokenize(lines)
    return tokenized


if __name__ == '__main__':
    print(test())
    main()
