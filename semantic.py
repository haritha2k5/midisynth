# semantic.py - MidiSynth Semantic Analyzer
# Validates the AST and expands REPEAT blocks into flat lists of nodes

from parser import (ProgramNode, TempoNode, InstrumentNode,
                    PlayNode, RepeatNode, ChordNode)

# ---------------------------------------------------------------------------
# Valid values
# ---------------------------------------------------------------------------

VALID_NOTES = ['C', 'D', 'E', 'F', 'G', 'A', 'B']

VALID_DURATIONS = ['WHOLE', 'HALF', 'QUARTER', 'EIGHTH', 'SIXTEENTH']

VALID_INSTRUMENTS = {
    'piano':    0,
    'violin':   40,
    'guitar':   24,
    'flute':    73,
    'drums':    118,
    'bass':     32,
    'trumpet':  56,
    'organ':    19,
}

# ---------------------------------------------------------------------------
# Helper - parse a note string like 'C4', 'BB4', 'D#3'
# ---------------------------------------------------------------------------


def parse_note(note_str):
    """
    Accepts note strings from the lexer (already uppercased).
    'BB4' means Bb4 (B-flat 4) - lexer uppercased the flat symbol.
    Returns (letter, accidental, octave) tuple.
    Raises ValueError if invalid.
    """
    # Note string is uppercased e.g. C4, D#3, BB4, GB5
    if len(note_str) == 2:
        # e.g. C4, D3
        letter = note_str[0]
        acc = ''
        octave = int(note_str[1])
    elif len(note_str) == 3:
        # e.g. D#3, BB4, GB5
        letter = note_str[0]
        acc = note_str[1]   # '#' or 'B' (uppercase of 'b')
        octave = int(note_str[2])
    else:
        raise ValueError(f"Invalid note format: {note_str!r}")

    if letter not in VALID_NOTES:
        raise ValueError(f"Invalid note letter: {letter!r} in {note_str!r}")

    if acc not in ('', '#', 'B'):
        raise ValueError(f"Invalid accidental: {acc!r} in {note_str!r}")

    if octave < 0 or octave > 8:
        raise ValueError(
            f"Octave out of range (0-8): {octave} in {note_str!r}")

    return letter, acc, octave


# ---------------------------------------------------------------------------
# Semantic Analyzer class
# ---------------------------------------------------------------------------

class SemanticAnalyzer:
    def __init__(self):
        self.tempo = None   # BPM
        self.instrument = None   # instrument name
        self.program = 0      # MIDI program number

    def analyze(self, ast):
        """
        Entry point.
        Validates the full AST and returns a flat list of checked statements.
        REPEAT blocks are expanded here.
        """
        if not isinstance(ast, ProgramNode):
            raise TypeError("Expected a ProgramNode at the root")

        flat_statements = []

        for node in ast.statements:
            result = self.check_node(node)
            # check_node returns a list (REPEAT expands to multiple nodes)
            flat_statements.extend(result)

        # Make sure TEMPO and INSTRUMENT were set
        if self.tempo is None:
            raise SemanticError("Missing TEMPO declaration")
        if self.instrument is None:
            raise SemanticError("Missing INSTRUMENT declaration")

        print(f"Semantic check passed!")
        print(f"  Tempo      : {self.tempo} BPM")
        print(
            f"  Instrument : {self.instrument} (MIDI program {self.program})")
        print(
            f"  Statements : {len(flat_statements)} (after REPEAT expansion)\n")

        return flat_statements, self.tempo, self.instrument, self.program

    def check_node(self, node):
        """
        Validate a single node.
        Returns a list of nodes (REPEAT returns multiple, others return one).
        """
        if isinstance(node, TempoNode):
            return self.check_tempo(node)
        elif isinstance(node, InstrumentNode):
            return self.check_instrument(node)
        elif isinstance(node, PlayNode):
            return self.check_play(node)
        elif isinstance(node, RepeatNode):
            return self.check_repeat(node)
        elif isinstance(node, ChordNode):
            return self.check_chord(node)
        else:
            raise SemanticError(f"Unknown node type: {type(node)}")

    def check_tempo(self, node):
        if node.bpm <= 0 or node.bpm > 300:
            raise SemanticError(
                f"TEMPO must be between 1 and 300, got {node.bpm}")
        self.tempo = node.bpm
        return [node]

    def check_instrument(self, node):
        name = node.name.lower()
        if name not in VALID_INSTRUMENTS:
            raise SemanticError(
                f"Unknown instrument: {name!r}. "
                f"Valid: {list(VALID_INSTRUMENTS.keys())}"
            )
        self.instrument = name
        self.program = VALID_INSTRUMENTS[name]
        return [node]

    def check_play(self, node):
        # Validate note
        parse_note(node.note)   # raises ValueError if invalid
        # Validate duration
        if node.duration not in VALID_DURATIONS:
            raise SemanticError(f"Invalid duration: {node.duration!r}")
        return [node]

    def check_repeat(self, node):
        if node.count <= 0:
            raise SemanticError(
                f"REPEAT count must be positive, got {node.count}")
        if node.count > 100:
            raise SemanticError(f"REPEAT count too large: {node.count}")

        # Validate all nodes inside the body
        validated_body = []
        for child in node.body:
            validated_body.extend(self.check_node(child))

        # Expand: repeat the body N times into a flat list
        expanded = []
        for _ in range(node.count):
            expanded.extend(validated_body)

        return expanded

    def check_chord(self, node):
        # Validate each note in the chord
        for note in node.notes:
            parse_note(note)
        if node.duration not in VALID_DURATIONS:
            raise SemanticError(f"Invalid duration: {node.duration!r}")
        return [node]


# ---------------------------------------------------------------------------
# Custom error class
# ---------------------------------------------------------------------------

class SemanticError(Exception):
    pass


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------

if __name__ == '__main__':
    from lexer import tokenize
    from parser import Parser

    with open('input.msynth', 'r') as f:
        source = f.read()

    tokens = tokenize(source)
    ast = Parser(tokens).parse()
    analyzer = SemanticAnalyzer()

    try:
        statements, tempo, instrument, program = analyzer.analyze(ast)
        print("Validated statements:")
        for s in statements:
            print(f"  {s}")
    except (SemanticError, ValueError) as e:
        print(f"Error: {e}")
