import re                          # regular expression module
from collections import Counter    # Counter counts how many times each item appears

# Reserved words: they look like identifiers but have a special meaning
KEYWORDS = {"if", "else", "while", "int", "float"}

# Each entry is (token name, regex that matches it).
# ORDER MATTERS: the regex engine tries them from top to bottom.
TOKEN_SPECIFICATION = [
    # Comment must come BEFORE OPERATOR, so "//" is one comment and not two "/" operators
    ("COMMENT", r"//[^\n]*"),               # "//" followed by anything except a newline
    ("NUMBER", r"\d+(\.\d+)?"),             # digits, optionally followed by "." and digits
    ("IDENTIFIER", r"[A-Za-z_][A-Za-z0-9_]*"),  # starts with letter/_, then letters/digits/_
    ("OPERATOR", r"==|!=|<=|>=|[+\-*/<>]"),     # two-char operators first, then single-char
    ("ASSIGNMENT", r"="),                   # single "=" (after "==" was tried in OPERATOR)
    ("SEPARATOR", r"[;,(){}]"),             # punctuation
    ("WHITESPACE", r"\s+"),                 # spaces, tabs, newlines
    ("INVALID", r"."),                      # any other single character = error
]


def lexical_analysis(source_code):
    tokens = []     # will store (type, lexeme, line) for each valid token
    errors = []     # will store error messages

    # Build ONE big regex with named groups: (?P<COMMENT>...)|(?P<NUMBER>...)|...
    # "|" means "or", the first group that matches wins
    pattern = "|".join(
        f"(?P<{name}>{regex})"
        for name, regex in TOKEN_SPECIFICATION
    )

    line = 1        # current line number (starts at 1)
    column = 1      # current column number (starts at 1)

    # finditer scans the source and yields each successive match
    for match in re.finditer(pattern, source_code):
        token_type = match.lastgroup    # name of the group that matched, e.g. "NUMBER"
        lexeme = match.group()          # the actual text that matched, e.g. "10"

        # Save the starting position of this match
        # (line/column are updated at the end of the loop, so save them now)
        start_line = line
        start_column = column

        # Ignore comments and whitespace: they are not tokens
        if token_type not in ("COMMENT", "WHITESPACE"):
            if token_type == "INVALID":
                # Record an error with its position
                # !r prints the lexeme with quotes, e.g. '@'
                errors.append(
                    f"Lexical error: {lexeme!r} "
                    f"at line {start_line}, column {start_column}"
                )

            else:
                # Classify keywords: an identifier that is in KEYWORDS becomes KEYWORD
                if token_type == "IDENTIFIER" and lexeme in KEYWORDS:
                    token_type = "KEYWORD"

                # Distinguish integer and real numbers
                if token_type == "NUMBER":
                    if "." in lexeme:
                        token_type = "REAL"
                    else:
                        token_type = "INTEGER"

                # Store token type, lexeme, and line number
                tokens.append((token_type, lexeme, start_line))

        # Update line and column positions
        if "\n" in lexeme:
            # lexeme contains newline(s): move down by that many lines
            line += lexeme.count("\n")
            # column = length of the text after the last newline, + 1
            column = len(lexeme.rsplit("\n", 1)[-1]) + 1
        else:
            # no newline: just move right by the lexeme's length
            column += len(lexeme)

    # Count tokens of each type (token[0] is the type)
    statistics = Counter(token[0] for token in tokens)

    return tokens, errors, statistics


# Example input
source = """int x = 10; // initialize x

float y = 2.5;"""

# Run the lexer; it returns three things
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

# sorted() orders the (type, count) pairs alphabetically by type
for token_type, count in sorted(statistics.items()):
    print(f"{token_type}: {count}")
