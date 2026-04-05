# 🎵 MidiSynth — DSL Music Compiler




## Overview

MidiSynth is a lightweight music composition system built on compiler design principles. Users write music using a custom Domain-Specific Language (DSL) in a `.msynth` file. The system compiles these instructions through a full compiler pipeline — lexing, parsing, semantic analysis, IR generation — and produces a playable MIDI file with an interactive web interface.

---

## Project Structure

```
midisynth/
├── input.msynth        # Sample DSL input (Happy Birthday)
├── lexer.py            # Phase 1 · Tokenizer
├── parser.py           # Phase 1 · Recursive descent parser + AST
├── semantic.py         # Phase 1 · Semantic analyzer + validator
├── visualize_ast.py    # Phase 1 · AST tree visualization (matplotlib)
├── ir.py               # Phase 2 · IR timeline builder
├── midigen.py          # Phase 2 · MIDI file generator
├── render.py           # Phase 2 · Audio playback
├── main.py             # Full pipeline (CLI entry point)
├── app.py              # FastAPI backend (web interface)
├── index.html          # Web frontend

```

---

## The DSL

MidiSynth has its own music description language. Here is the full syntax:

```
# Comments start with #

TEMPO 120               # Set BPM (1–300)
INSTRUMENT piano        # Set instrument

PLAY C4 QUARTER         # Play a note: PLAY <note> <duration>
PLAY D#4 EIGHTH         # Sharp notes
PLAY Bb4 HALF           # Flat notes

REPEAT 2 {              # Repeat a block N times
    PLAY E4 QUARTER
    PLAY G4 QUARTER
}

CHORD [C4 E4 G4] HALF   # Play multiple notes simultaneously
```

### Valid Notes
`C D E F G A B` + optional `#` (sharp) or `b` (flat) + octave `0–8`

Examples: `C4`, `D#3`, `Gb5`, `Bb4`, `A4`

### Valid Durations
| Name | Beats |
|---|---|
| WHOLE | 4 |
| HALF | 2 |
| QUARTER | 1 |
| EIGHTH | 0.5 |
| SIXTEENTH | 0.25 |

### Valid Instruments
`piano`, `violin`, `guitar`, `flute`, `drums`, `bass`, `trumpet`, `organ`

---

## Compiler Pipeline

### Phase 1 — Front End (Language Processing)

```
input.msynth
     ↓
 lexer.py      →  Tokenizes raw text into 79 tokens
     ↓
 parser.py     →  Builds Abstract Syntax Tree (AST)
     ↓
 semantic.py   →  Validates meaning, expands REPEAT blocks
```

**Lexer** breaks the source into tokens — keywords (`PLAY`, `TEMPO`), notes (`C4`, `Bb4`), durations (`QUARTER`), numbers, and symbols. Uses a master regex with named groups.

**Parser** uses recursive descent parsing to build an AST with nodes: `ProgramNode`, `TempoNode`, `InstrumentNode`, `PlayNode`, `RepeatNode`, `ChordNode`.

**Semantic Analyzer** validates note letters, octave ranges, duration names, instrument names, tempo range (1–300), and required declarations. Expands `REPEAT` blocks into flat lists.

### Phase 2 — Back End (Music Generation)

```
semantic output (flat validated statements)
     ↓
  ir.py        →  Converts notes to MIDI pitches + timestamps
     ↓
midigen.py     →  Writes .mid file using midiutil
     ↓
 render.py     →  Plays .mid file
```

**IR Builder** converts note names (`C4` → MIDI pitch `60`) and calculates exact start times in seconds based on tempo.

**MIDI Generator** writes a standard `.mid` file using `midiutil`, setting the instrument via MIDI program numbers.

---

## Installation

```bash
# Clone the repository
git clone https://github.com/haritha2k5/midisynth.git
cd midisynth

# Install dependencies
pip install midiutil pygame fastapi uvicorn matplotlib
```

---

## Usage

### Option 1 — Command Line

```bash
# Run the full pipeline on Happy Birthday
python main.py

# Run on a custom DSL file
python main.py my_song.msynth
```

### Option 2 — Web Interface

```bash
# Start the backend
python app.py

# Open index.html in your browser
# Click Compile & Run
```

The web interface shows:
- **Phase 1 · Lexer** — all tokens as colored chips
- **Phase 1 · Parser** — AST visualization image + node list
- **Phase 1 · Semantic** — tempo, instrument, validated statements
- **Phase 2 · IR** — full note timeline with timestamps
- **Phase 2 · Player** — in-browser audio playback with tempo slider

---


## Tech Stack

| Component | Technology |
|---|---|
| DSL Parser | Handwritten Recursive Descent (Python) |
| Tokenizer | Python `re` module (regex-based) |
| AST Visualization | `matplotlib` |
| MIDI Generation | `midiutil` |
| Audio Playback (CLI) | `pygame` |
| Audio Playback (Web) | Web Audio API |
| Backend | `FastAPI` + `uvicorn` |
| Frontend | Vanilla HTML / CSS / JS |

---

## Dependencies

```
midiutil
pygame
fastapi
uvicorn
matplotlib
```

Install all at once:
```bash
pip install midiutil pygame fastapi uvicorn matplotlib
```

---

## Sample Input — Happy Birthday

```
# MidiSynth DSL - Happy Birthday
TEMPO 120
INSTRUMENT piano

PLAY C4 EIGHTH
PLAY C4 EIGHTH
PLAY D4 QUARTER
PLAY C4 QUARTER
PLAY F4 QUARTER
PLAY E4 HALF
...
```

Produces a 12.5 second MIDI file with 25 note events across 4 melodic lines.

---

## Key Design Decisions

- **Handwritten lexer and parser** over PLY/ANTLR — more readable, easier to debug, better for understanding compiler concepts
- **Pygame for CLI playback** — simple cross-platform MIDI playback with no external synthesizer required
- **Web Audio API for browser playback** — no CDN dependencies, works entirely in-browser using oscillator synthesis
- **Phase split** — clean separation between front end (language processing) and back end (music generation) mirrors real compiler architecture

---

*MidiSynth — where compiler design meets music* 🎹
