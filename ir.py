# ir.py - MidiSynth Intermediate Representation Builder
# Converts flat validated statements into a timeline of note events

from parser import PlayNode, ChordNode, TempoNode, InstrumentNode

# ---------------------------------------------------------------------------
# Duration map - maps duration name to number of beats
# ---------------------------------------------------------------------------
DURATION_BEATS = {
    'WHOLE':      4.0,
    'HALF':       2.0,
    'QUARTER':    1.0,
    'EIGHTH':     0.5,
    'SIXTEENTH':  0.25,
}

# ---------------------------------------------------------------------------
# Note to MIDI pitch converter
# ---------------------------------------------------------------------------
# MIDI note number formula: (octave + 1) * 12 + semitone
SEMITONES = {
    'C': 0, 'D': 2, 'E': 4, 'F': 5,
    'G': 7, 'A': 9, 'B': 11
}

def note_to_midi(note_str):
    """
    Converts a note string like 'C4', 'BB4', 'D#3' to a MIDI pitch number.
    BB4 = Bb4 = B-flat 4 (lexer uppercased the flat symbol)
    """
    if len(note_str) == 2:
        letter = note_str[0]
        acc    = ''
        octave = int(note_str[1])
    else:
        letter = note_str[0]
        acc    = note_str[1]   # '#' or 'B' (uppercase flat)
        octave = int(note_str[2])

    semitone = SEMITONES[letter]

    if acc == '#':
        semitone += 1
    elif acc == 'B':       # uppercase 'B' = flat
        semitone -= 1

    midi = (octave + 1) * 12 + semitone
    return midi

# ---------------------------------------------------------------------------
# NoteEvent - one event in the timeline
# ---------------------------------------------------------------------------
class NoteEvent:
    def __init__(self, pitches, start_time, duration_secs, velocity=100):
        self.pitches       = pitches        # list of MIDI pitch numbers
        self.start_time    = start_time     # in seconds
        self.duration_secs = duration_secs  # in seconds
        self.velocity      = velocity       # 0-127, loudness

    def __repr__(self):
        note_str = self.pitches if len(self.pitches) > 1 else self.pitches[0]
        return (f'NoteEvent(pitches={note_str}, '
                f'start={self.start_time:.3f}s, '
                f'dur={self.duration_secs:.3f}s)')

# ---------------------------------------------------------------------------
# IR Builder
# ---------------------------------------------------------------------------
class IRBuilder:
    def __init__(self, tempo):
        self.tempo         = tempo
        self.beat_duration = 60.0 / tempo   # seconds per beat
        self.current_time  = 0.0
        self.timeline      = []

    def build(self, statements):
        """
        Walk the flat validated statements and build a timeline.
        Returns list of NoteEvent objects.
        """
        for node in statements:
            if isinstance(node, (TempoNode, InstrumentNode)):
                # Already handled in semantic — skip
                continue
            elif isinstance(node, PlayNode):
                self._add_play(node)
            elif isinstance(node, ChordNode):
                self._add_chord(node)

        print(f"IR built successfully!")
        print(f"  Total note events : {len(self.timeline)}")
        print(f"  Total duration    : {self.current_time:.2f} seconds\n")

        return self.timeline

    def _beats_to_secs(self, duration_name):
        """Convert a duration name to seconds based on current tempo."""
        beats = DURATION_BEATS[duration_name]
        return beats * self.beat_duration

    def _add_play(self, node):
        """Add a single note event to the timeline."""
        pitch    = note_to_midi(node.note)
        duration = self._beats_to_secs(node.duration)

        event = NoteEvent(
            pitches       = [pitch],
            start_time    = self.current_time,
            duration_secs = duration,
        )
        self.timeline.append(event)
        self.current_time += duration

    def _add_chord(self, node):
        """Add a chord event - all notes start at the same time."""
        pitches  = [note_to_midi(n) for n in node.notes]
        duration = self._beats_to_secs(node.duration)

        event = NoteEvent(
            pitches       = pitches,
            start_time    = self.current_time,
            duration_secs = duration,
        )
        self.timeline.append(event)
        self.current_time += duration

# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    from lexer import tokenize
    from parser import Parser
    from semantic import SemanticAnalyzer

    with open('input.msynth', 'r') as f:
        source = f.read()

    tokens     = tokenize(source)
    ast        = Parser(tokens).parse()
    analyzer   = SemanticAnalyzer()
    statements, tempo, instrument, program = analyzer.analyze(ast)

    builder  = IRBuilder(tempo)
    timeline = builder.build(statements)

    print("Timeline:")
    for event in timeline:
        print(f"  {event}")
