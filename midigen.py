# midigen.py - MidiSynth MIDI File Generator
# Converts the IR timeline into a standard .mid file using midiutil

from midiutil import MIDIFile

# ---------------------------------------------------------------------------
# MIDI Generator
# ---------------------------------------------------------------------------
class MidiGenerator:
    def __init__(self, tempo, program, output_file='output.mid'):
        self.tempo       = tempo
        self.program     = program       # MIDI instrument number
        self.output_file = output_file
        self.track       = 0
        self.channel     = 0

    def generate(self, timeline):
        """
        Takes a list of NoteEvent objects and writes a .mid file.
        """
        midi = MIDIFile(1)   # 1 track

        # Set tempo and instrument
        midi.addTempo(self.track, 0, self.tempo)
        midi.addProgramChange(self.track, self.channel, 0, self.program)

        # Add each note event
        for event in timeline:
            # Convert seconds to beats for midiutil
            start_beat    = event.start_time    / (60.0 / self.tempo)
            duration_beat = event.duration_secs / (60.0 / self.tempo)

            for pitch in event.pitches:
                midi.addNote(
                    track    = self.track,
                    channel  = self.channel,
                    pitch    = pitch,
                    time     = start_beat,
                    duration = duration_beat,
                    volume   = event.velocity,
                )

        # Write to file
        with open(self.output_file, 'wb') as f:
            midi.writeFile(f)

        print(f"MIDI file written: {self.output_file}")
        print(f"  Instrument : MIDI program {self.program}")
        print(f"  Tempo      : {self.tempo} BPM")
        print(f"  Events     : {len(timeline)}\n")

# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    from lexer import tokenize
    from parser import Parser
    from semantic import SemanticAnalyzer
    from ir import IRBuilder

    with open('input.msynth', 'r') as f:
        source = f.read()

    tokens     = tokenize(source)
    ast        = Parser(tokens).parse()
    analyzer   = SemanticAnalyzer()
    statements, tempo, instrument, program = analyzer.analyze(ast)

    builder  = IRBuilder(tempo)
    timeline = builder.build(statements)

    generator = MidiGenerator(tempo, program, 'output.mid')
    generator.generate(timeline)

    print("Done! Check output.mid in your folder.")