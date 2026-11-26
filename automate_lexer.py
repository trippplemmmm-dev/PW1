from collections import Counter

# Words that look like identifiers but are reserved
KEYWORDS = {"if", "else", "while", "int", "float"}

# ---------------------------------------------------------------
# 1. CHARACTER CLASSES: the DFA's "alphabet" (we group characters)
# ---------------------------------------------------------------
def char_class(ch):
    if ch.isalpha() or ch == "_":
        return "LETTER"
    if ch.isdigit():
        return "DIGIT"
    if ch == ".":
        return "DOT"
    if ch == "/":
        return "SLASH"
    if ch == "=":
        return "EQ"
    if ch == "!":
        return "BANG"
    if ch in "<>":
        return "LTGT"
    if ch in "+-*":
        return "ARITH"
    if ch in ";,(){}":
        return "SEP"
    if ch == "\n":
        return "NEWLINE"
    if ch.isspace():
        return "SPACE"
    return "OTHER"


# ---------------------------------------------------------------
# 2. TRANSITION TABLE: (current_state, character_class) -> next_state
#    If a pair is missing, the DFA is "stuck" (no move possible).
# ---------------------------------------------------------------
TRANSITIONS = {
    ("START", "LETTER"): "ID",
    ("START", "DIGIT"): "INT",
    ("START", "SLASH"): "SLASH",
    ("START", "EQ"): "ASSIGN",
    ("START", "BANG"): "BANG",
    ("START", "LTGT"): "REL",
    ("START", "ARITH"): "ARITH",
    ("START", "SEP"): "SEP",
    ("START", "SPACE"): "WS",
    ("START", "NEWLINE"): "WS",

    ("ID", "LETTER"): "ID",       # identifier continues with letters...
    ("ID", "DIGIT"): "ID",        # ...or digits

    ("INT", "DIGIT"): "INT",      # more digits: still an integer
    ("INT", "DOT"): "DOT",        # a dot: maybe a real number

    ("DOT", "DIGIT"): "REAL",     # need a digit after the dot
    ("REAL", "DIGIT"): "REAL",

    ("SLASH", "SLASH"): "COMMENT",  # "//" starts a comment

    ("ASSIGN", "EQ"): "EQEQ",     # "=="
    ("BANG", "EQ"): "NEQ",        # "!="
    ("REL", "EQ"): "RELEQ",       # "<=" or ">="

    ("WS", "SPACE"): "WS",
    ("WS", "NEWLINE"): "WS",
}


def next_state(state, cls):
    # Inside a comment, every character except newline keeps us in COMMENT
    if state == "COMMENT":
        return "COMMENT" if cls != "NEWLINE" else None
    # Otherwise look the move up in the table (None if no move exists)
    return TRANSITIONS.get((state, cls))


# ---------------------------------------------------------------
# 3. ACCEPTING (FINAL) STATES: which states mean "a token is complete"
#    DOT and BANG are NOT here: "3." and "!" alone are incomplete.
# ---------------------------------------------------------------
ACCEPTING = {
    "ID": "IDENTIFIER",
    "INT": "NUMBER",
    "REAL": "NUMBER",
    "SLASH": "OPERATOR",     # a single "/" is division
    "COMMENT": "COMMENT",
    "ASSIGN": "ASSIGNMENT",  # a single "="
    "EQEQ": "OPERATOR",
    "NEQ": "OPERATOR",
    "REL": "OPERATOR",       # "<" or ">"
    "RELEQ": "OPERATOR",
    "ARITH": "OPERATOR",
    "SEP": "SEPARATOR",
    "WS": "WHITESPACE",
}


def lexical_analysis(source_code):
    tokens = []
    errors = []
    line = 1
    column = 1
    pos = 0                      # where the next token starts
    n = len(source_code)

    while pos < n:
        # Every token starts with the DFA reset to START
        state = "START"
        last_accept = None       # (token_type, end_position) of the longest match so far
        i = pos                  # scanning pointer

        # Run the DFA as far as it can go
        while i < n:
            nxt = next_state(state, char_class(source_code[i]))
            if nxt is None:      # stuck: no transition, stop
                break
            state = nxt          # take the transition
            i += 1               # consume the character
            if state in ACCEPTING:                      # remember the latest accepting point
                last_accept = (ACCEPTING[state], i)

        if last_accept is None:
            # DFA never reached a final state -> invalid character
            token_type = "INVALID"
            end = pos + 1
        else:
            # "Maximal munch": back up to the longest accepted lexeme
            token_type, end = last_accept

        lexeme = source_code[pos:end]
        pos = end                # next token begins right after this one

        # ---- everything below is the same as your regex version ----
        start_line = line
        start_column = column

        if token_type not in ("COMMENT", "WHITESPACE"):
            if token_type == "INVALID":
                errors.append(
                    f"Lexical error: {lexeme!r} "
                    f"at line {start_line}, column {start_column}"
                )
            else:
                if token_type == "IDENTIFIER" and lexeme in KEYWORDS:
                    token_type = "KEYWORD"
                if token_type == "NUMBER":
                    token_type = "REAL" if "." in lexeme else "INTEGER"
                tokens.append((token_type, lexeme, start_line))

        if "\n" in lexeme:
            line += lexeme.count("\n")
            column = len(lexeme.rsplit("\n", 1)[-1]) + 1
        else:
            column += len(lexeme)

    statistics = Counter(token[0] for token in tokens)
    return tokens, errors, statistics


# Example input
source = """int x = 10; // initialize x

float y = 2.5;"""

tokens, errors, statistics = lexical_analysis(source)

print("TOKENS:")
for token in tokens:
    print(token)

print("\nLEXICAL ERRORS:")
if errors:
    for error in errors:
        print(error)
else:
    print("No lexical errors.")

print("\nTOKEN STATISTICS:")
print("Total tokens:", len(tokens))
for token_type, count in sorted(statistics.items()):
    print(f"{token_type}: {count}")
