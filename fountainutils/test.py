from fountainutils import FountainToPDF

def test():
    converter = FountainToPDF()
    # Test scene headings
    assert converter._tokenize(["", "INT. WAREHOUSE - DAY", ""])[1][1] == "SCENE"
    assert converter._tokenize(["", "INT. warehouse - DAY", ""])[1][1] == "ACTION"
    assert converter._tokenize(["", "INT. WAREHOUSE - DAY", "t"])[1][1] == "CHARACTER"
    assert converter._tokenize(["", ".INT. WAREHOUSE - DAY", "t"])[1][1] == "SCENE"

    # Test character names
    assert converter._tokenize(["", "JIM-BOB", "I'm Jim-Bob!"])[1][1] == "CHARACTER"
    assert converter._tokenize(["", "JIM-BOB", "I'm Jim-Bob!"])[2][1] == "DIALOG"
    assert converter._tokenize(["", "@JIM-McBOB", "I'm Jim-McBob!"])[1][1] == "CHARACTER"
    assert converter._tokenize(["", "JIM-McBOB", "I'm Jim-McBob!"])[1][1] == "ACTION"

    # Test dialog
    assert converter._tokenize(["", "@JIM-McBOB", "I'm Jim-McBob!", "This is dialog."])[2][1] == "DIALOG"
    assert converter._tokenize(["", "JIM-BOB", "I'm Jim-Bob!", "This is dialog."])[2][1] == "DIALOG"
    assert converter._tokenize(["", "@JIM-McBOB", "I'm Jim-McBob!", "This is dialog."])[3][1] == "DIALOG"
    assert converter._tokenize(["", "@JIM-McBOB", "I'm Jim-McBob!", "", "This is action."])[4][1] == "ACTION"
    assert converter._tokenize(["", "@JIM-McBOB", "I'm Jim-McBob!", "  ", "This is dialog."])[4][1] == "DIALOG"
    assert converter._tokenize(["", "@JIM-McBOB", "I'm Jim-McBob!", "  ", "This is dialog."])[3][1] == "DIALOG"
    # assert converter._tokenize(["", "@JIM-McBOB ^", "I'm Jim-McBob!"])[1][1] == "CHARACTERDD"

    # Test centered text
    assert converter._tokenize(["", "> THE END <", ""])[1][1] == "CENTERED"
    assert converter._tokenize(["", "@> THE END <", ""])[1][1] == "CHARACTER"

    # Test lyrics
    assert converter._tokenize(["", "~These are lyrics", ""])[1][1] == "LYRIC"
    assert converter._tokenize(["", "jfkd~These are not lyrics", ""])[1][1] == "ACTION"

    # Test parentheticals
    assert converter._tokenize(["", "(over the hill)", ""])[1][1] == "PARENTHETICAL"

    # Test non-printing text
    assert converter._tokenize(["", "[[this is a note]]", ""])[1][1] == "NOTE"
    assert converter._tokenize(["", "= this is a synopse", ""])[1][1] == "SYNOPSE"
    assert converter._tokenize(["", "# this is an H1", ""])[1][1] == "SECTION"
    assert converter._tokenize(["", "####### this is a very deep heading", ""])[1][1] == "SECTION"

    return "All tests passed."


if __name__ == '__main__':
    print(test())
