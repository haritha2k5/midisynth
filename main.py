# main.py - MidiSynth Full Pipeline
# Ties everything together: DSL → Lexer → Parser → Semantic → IR → MIDI → Audio

import sys
from lexer import tokenize
from parser import Parser
from semantic import SemanticAnalyzer, SemanticError
from ir import IRBuilder
from midigen import MidiGenerator
from render import Renderer

# ---------------------------------------------------------------------------
# Full pipeline
# ---------------------------------------------------------------------------


def run(input_file='input.msynth', output_file='output.mid'):

    print("=" * 50)
    print("  MidiSynth - DSL Music Compiler")
    print("=" * 50)
    print(f"\nInput  : {input_file}")
    print(f"Output : {output_file}\n")

    # ── Phase 1: Front End ─────────────────────────────
    print("── Phase 1: Front End ──────────────────────")

    # Step 1: Lexing
    print("\n[1] Lexing...")
    try:
        with open(input_file, 'r') as f:
            source = f.read()
        tokens = tokenize(source)
        print(f"    {len(tokens)} tokens found")
    except SyntaxError as e:
        print(f"Lexer Error: {e}")
        sys.exit(1)
    except FileNotFoundError:
        print(f"Error: File not found: {input_file}")
        sys.exit(1)

    # Step 2: Parsing
    print("\n[2] Parsing...")
    try:
        ast = Parser(tokens).parse()
        print(f"    AST built successfully")
    except SyntaxError as e:
        print(f"Parser Error: {e}")
        sys.exit(1)

    # Step 3: Semantic Analysis
    print("\n[3] Semantic Analysis...")
    try:
        analyzer = SemanticAnalyzer()
        statements, tempo, instrument, program = analyzer.analyze(ast)
    except (SemanticError, ValueError) as e:
        print(f"Semantic Error: {e}")
        sys.exit(1)

    # ── Phase 2: Back End ──────────────────────────────
    print("── Phase 2: Back End ───────────────────────")

    # Step 4: IR Building
    print("\n[4] Building IR timeline...")
    builder = IRBuilder(tempo)
    timeline = builder.build(statements)

    # Step 5: MIDI Generation
    print("\n[5] Generating MIDI file...")
    generator = MidiGenerator(tempo, program, output_file)
    generator.generate(timeline)

    # Step 6: Playback
    print("\n[6] Playing audio...")
    print("=" * 50)
    renderer = Renderer(output_file)
    renderer.play()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    # Allow custom input file from command line
    # Usage: python main.py [input_file]
    input_file = sys.argv[1] if len(sys.argv) > 1 else 'input.msynth'
    run(input_file)
