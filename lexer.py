# lexer.py - MidiSynth Tokenizer
# Reads raw DSL text and breaks it into a list of tokens
 
import re
 
# ---------------------------------------------------------------------------
# Token definitions - order matters! More specific patterns come first
# ---------------------------------------------------------------------------
TOKEN_TYPES = [
    # Keywords - must come before WORD so they are matched first
    ('TEMPO',      r'\bTEMPO\b'),
    ('INSTRUMENT', r'\bINSTRUMENT\b'),
    ('PLAY',       r'\bPLAY\b'),
    ('REPEAT',     r'\bREPEAT\b'),
    ('CHORD',      r'\bCHORD\b'),
 
    # Durations - must come before NOTE so HALF is not read as note H
    ('DURATION',   r'\b(WHOLE|HALF|QUARTER|EIGHTH|SIXTEENTH)\b'),
 
    # Notes - letter A-G + optional sharp(#) or flat(b) + octave digit 0-8
    # Examples: C4, D#3, Gb5, Bb4, A4
    ('NOTE',       r'\b[A-Ga-g][#b]?[0-8]\b'),
 
    # Instrument names and any other plain words
    ('WORD',       r'\b[a-zA-Z_][a-zA-Z_]*\b'),
 
    # Integer numbers - used for TEMPO value and REPEAT count
    ('NUMBER',     r'\b\d+\b'),
 
    # Symbols
    ('LBRACE',     r'\{'),
    ('RBRACE',     r'\}'),
    ('LBRACKET',   r'\['),
    ('RBRACKET',   r'\]'),
 
    # Skip these - they carry no meaning
    ('COMMENT',    r'#[^\n]*'),
    ('WHITESPACE', r'[ \t\n\r]+'),
]
 
# Combine all patterns into one master regex using named groups
MASTER_PATTERN = re.compile(
    '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_TYPES)
)
 
# ---------------------------------------------------------------------------
# Token class - represents one meaningful unit from the source
# ---------------------------------------------------------------------------
class Token:
    def __init__(self, type_, value, line):
        self.type  = type_   # e.g. 'PLAY', 'NOTE', 'NUMBER'
        self.value = value   # e.g. 'PLAY', 'C4',   '120'
        self.line  = line    # line number for error messages
 
    def __repr__(self):
        return f'Token({self.type}, {self.value!r}, line={self.line})'
 
 
# ---------------------------------------------------------------------------
# Tokenize function - the main entry point
# ---------------------------------------------------------------------------
def tokenize(source_code):
    """
    Takes the raw DSL source string.
    Returns a clean list of Token objects.
    Raises SyntaxError on any unrecognised character.
    """
    tokens      = []
    line_number = 1
 
    for match in MASTER_PATTERN.finditer(source_code):
        token_type = match.lastgroup
        value      = match.group()
 
        # Count newlines to track current line number
        line_number += value.count('\n')
 
        # Skip whitespace and comments
        if token_type in ('WHITESPACE', 'COMMENT'):
            continue
 
        # Uppercase everything except instrument names (WORD)
        # so that 'play' and 'PLAY' are treated the same
        if token_type != 'WORD':
            value = value.upper()
 
        tokens.append(Token(token_type, value, line_number))
 
    # Check if any character was not matched by the regex
    matched_chars = set()
    for match in MASTER_PATTERN.finditer(source_code):
        matched_chars.update(range(match.start(), match.end()))
 
    for i, ch in enumerate(source_code):
        if i not in matched_chars and not ch.isspace():
            raise SyntaxError(f"Unexpected character '{ch}' at position {i}")
 
    return tokens
 
 
# ---------------------------------------------------------------------------
# Quick test - run this file directly to see token output
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    # Read from input.msynth
    with open('input.msynth', 'r') as f:
        source = f.read()
 
    tokens = tokenize(source)
 
    print(f"Total tokens found: {len(tokens)}\n")
    for tok in tokens:
        print(tok)