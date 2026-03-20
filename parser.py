# parser.py - MidiSynth Parser
# Takes a list of tokens and builds an AST (Abstract Syntax Tree)

from lexer import tokenize

# ---------------------------------------------------------------------------
# AST Node classes - each represents one musical instruction
# ---------------------------------------------------------------------------


class TempoNode:
    def __init__(self, bpm):
        self.bpm = bpm          # integer e.g. 120

    def __repr__(self):
        return f'TempoNode(bpm={self.bpm})'


class InstrumentNode:
    def __init__(self, name):
        self.name = name        # string e.g. 'piano'

    def __repr__(self):
        return f'InstrumentNode(name={self.name})'


class PlayNode:
    def __init__(self, note, duration):
        self.note = note      # string e.g. 'C4', 'BB4'
        self.duration = duration  # string e.g. 'QUARTER'

    def __repr__(self):
        return f'PlayNode(note={self.note}, duration={self.duration})'


class RepeatNode:
    def __init__(self, count, body):
        self.count = count  # integer e.g. 2
        self.body = body   # list of AST nodes inside the block

    def __repr__(self):
        return f'RepeatNode(count={self.count}, body={self.body})'


class ChordNode:
    def __init__(self, notes, duration):
        self.notes = notes     # list of strings e.g. ['C4','E4','G4']
        self.duration = duration  # string e.g. 'HALF'

    def __repr__(self):
        return f'ChordNode(notes={self.notes}, duration={self.duration})'


class ProgramNode:
    def __init__(self, statements):
        self.statements = statements  # list of all top-level AST nodes

    def __repr__(self):
        return f'ProgramNode({self.statements})'


# ---------------------------------------------------------------------------
# Parser class - recursive descent
# ---------------------------------------------------------------------------

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0         # current position in token list

    # ── Helper methods ───────────────────────────────────────────────────────

    def current(self):
        """Return the current token without consuming it."""
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected_type=None):
        """
        Consume and return the current token.
        If expected_type is given, raise error if type doesn't match.
        """
        token = self.current()
        if token is None:
            raise SyntaxError("Unexpected end of input")
        if expected_type and token.type != expected_type:
            raise SyntaxError(
                f"Line {token.line}: Expected {expected_type} but got {token.type} ({token.value!r})"
            )
        self.pos += 1
        return token

    # ── Parsing methods ──────────────────────────────────────────────────────

    def parse(self):
        """Entry point - parse the full program."""
        statements = []
        while self.current() is not None:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
        return ProgramNode(statements)

    def parse_statement(self):
        """Decide which statement to parse based on current token."""
        token = self.current()

        if token.type == 'TEMPO':
            return self.parse_tempo()
        elif token.type == 'INSTRUMENT':
            return self.parse_instrument()
        elif token.type == 'PLAY':
            return self.parse_play()
        elif token.type == 'REPEAT':
            return self.parse_repeat()
        elif token.type == 'CHORD':
            return self.parse_chord()
        else:
            raise SyntaxError(
                f"Line {token.line}: Unexpected token {token.type} ({token.value!r})"
            )

    def parse_tempo(self):
        """TEMPO <number>"""
        self.consume('TEMPO')
        number = self.consume('NUMBER')
        return TempoNode(int(number.value))

    def parse_instrument(self):
        """INSTRUMENT <word>"""
        self.consume('INSTRUMENT')
        name = self.consume('WORD')
        return InstrumentNode(name.value.lower())

    def parse_play(self):
        """PLAY <note> <duration>"""
        self.consume('PLAY')
        note = self.consume('NOTE')
        duration = self.consume('DURATION')
        return PlayNode(note.value, duration.value)

    def parse_repeat(self):
        """REPEAT <number> { <statements> }"""
        self.consume('REPEAT')
        count = self.consume('NUMBER')
        self.consume('LBRACE')

        body = []
        while self.current() and self.current().type != 'RBRACE':
            body.append(self.parse_statement())

        self.consume('RBRACE')
        return RepeatNode(int(count.value), body)

    def parse_chord(self):
        """CHORD [ <note> <note> ... ] <duration>"""
        self.consume('CHORD')
        self.consume('LBRACKET')

        notes = []
        while self.current() and self.current().type == 'NOTE':
            notes.append(self.consume('NOTE').value)

        if not notes:
            raise SyntaxError("CHORD must contain at least one note")

        self.consume('RBRACKET')
        duration = self.consume('DURATION')
        return ChordNode(notes, duration.value)


# ---------------------------------------------------------------------------
# Quick test - run this file directly to see AST output
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    with open('input.msynth', 'r') as f:
        source = f.read()

    tokens = tokenize(source)
    parser = Parser(tokens)
    ast = parser.parse()

    print("AST successfully built!\n")
    for node in ast.statements:
        print(node)
