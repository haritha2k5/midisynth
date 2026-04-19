# app.py - MidiSynth FastAPI Backend
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import traceback
import base64
import io
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))

from lexer       import tokenize
from parser      import Parser
from semantic    import SemanticAnalyzer, SemanticError
from ir          import IRBuilder
from midigen     import MidiGenerator
from visualise_ast import ast_to_tree, compute_width, assign_positions, draw_tree

import matplotlib
matplotlib.use('Agg')   # non-interactive backend - no window popup
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

NODE_COLORS = {
    'Program':    '#4A90D9',
    'Tempo':      '#7B68EE',
    'Instrument': '#20B2AA',
    'Play':       '#3CB371',
    'Repeat':     '#FF8C00',
    'Chord':      '#DC143C',
    'Note':       '#57A65A',
    'Duration':   '#C8A200',
    'Literal':    '#888888',
}

class DSLInput(BaseModel):
    code: str

@app.get("/")
def serve_index():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return FileResponse(os.path.join(base_dir, "index.html"))

@app.post("/compile")
def compile_dsl(data: DSLInput):
    result = {
        "lexer":    {"success": False, "tokens": [],     "error": None},
        "parser":   {"success": False, "ast": [],        "error": None, "ast_image": None},
        "semantic": {"success": False, "statements": [], "tempo": None,
                     "instrument": None, "program": None, "error": None},
        "ir":       {"success": False, "timeline": [],   "total_duration": None, "error": None},
        "midi":     {"success": False, "file": None,     "error": None},
    }

    # ── Step 1: Lexer ─────────────────────────────────
    try:
        tokens = tokenize(data.code)
        result["lexer"]["success"] = True
        result["lexer"]["tokens"]  = [
            {"type": t.type, "value": t.value, "line": t.line}
            for t in tokens
        ]
    except Exception as e:
        result["lexer"]["error"] = str(e)
        return result

    # ── Step 2: Parser ────────────────────────────────
    try:
        ast = Parser(tokens).parse()
        result["parser"]["success"] = True
        result["parser"]["ast"]     = [repr(s) for s in ast.statements]

        # Generate AST image as base64
        try:
            tree = ast_to_tree(ast)
            compute_width(tree)
            assign_positions(tree)

            tree_w = tree.width
            fig_w  = max(20, tree_w * 0.55)
            fig_h  = 6

            fig, ax = plt.subplots(figsize=(fig_w, fig_h))
            fig.patch.set_facecolor('#1a1a2e')
            ax.set_facecolor('#1a1a2e')

            draw_tree(tree, ax)

            ax.autoscale()
            ax.set_aspect('equal')
            ax.axis('off')
            ax.margins(0.02)
            ax.set_title('MidiSynth — Abstract Syntax Tree',
                         color='white', fontsize=11, fontweight='bold', pad=10)

            legend_handles = [
                mpatches.Patch(color=NODE_COLORS['Program'],    label='Program'),
                mpatches.Patch(color=NODE_COLORS['Tempo'],      label='TEMPO'),
                mpatches.Patch(color=NODE_COLORS['Instrument'], label='INSTRUMENT'),
                mpatches.Patch(color=NODE_COLORS['Play'],       label='PLAY'),
                mpatches.Patch(color=NODE_COLORS['Repeat'],     label='REPEAT'),
                mpatches.Patch(color=NODE_COLORS['Chord'],      label='CHORD'),
                mpatches.Patch(color=NODE_COLORS['Note'],       label='Note'),
                mpatches.Patch(color=NODE_COLORS['Duration'],   label='Duration'),
            ]
            ax.legend(handles=legend_handles, loc='upper right',
                      fontsize=7, facecolor='#2e2e4e',
                      labelcolor='white', edgecolor='#444466')

            buf = io.BytesIO()
            plt.tight_layout()
            plt.savefig(buf, format='png', dpi=120,
                        bbox_inches='tight', facecolor='#1a1a2e')
            plt.close(fig)
            buf.seek(0)
            result["parser"]["ast_image"] = base64.b64encode(buf.read()).decode('utf-8')
        except Exception as img_err:
            result["parser"]["ast_image"] = None

    except Exception as e:
        result["parser"]["error"] = str(e)
        return result

    # ── Step 3: Semantic ──────────────────────────────
    try:
        analyzer = SemanticAnalyzer()
        statements, tempo, instrument, program = analyzer.analyze(ast)
        result["semantic"]["success"]    = True
        result["semantic"]["statements"] = [repr(s) for s in statements]
        result["semantic"]["tempo"]      = tempo
        result["semantic"]["instrument"] = instrument
        result["semantic"]["program"]    = program
    except Exception as e:
        result["semantic"]["error"] = str(e)
        return result

    # ── Step 4: IR ────────────────────────────────────
    try:
        builder  = IRBuilder(tempo)
        timeline = builder.build(statements)
        result["ir"]["success"]        = True
        result["ir"]["total_duration"] = round(builder.current_time, 2)
        result["ir"]["timeline"]       = [
            {
                "pitches":    e.pitches,
                "start_time": round(e.start_time, 3),
                "duration":   round(e.duration_secs, 3),
                "velocity":   e.velocity,
            }
            for e in timeline
        ]
    except Exception as e:
        result["ir"]["error"] = str(e)
        return result

    # ── Step 5: MIDI ──────────────────────────────────
    try:
        gen = MidiGenerator(tempo, program, "output.mid")
        gen.generate(timeline)
        result["midi"]["success"] = True
        result["midi"]["file"]    = "output.mid"
    except Exception as e:
        result["midi"]["error"] = str(e)

    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8001, reload=True)