# app.py - MidiSynth FastAPI Backend
from midigen import MidiGenerator
from ir import IRBuilder
from semantic import SemanticAnalyzer, SemanticError
from parser import Parser
from lexer import tokenize
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import traceback
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class DSLInput(BaseModel):
    code: str


@app.get("/")
def serve_index():
    return FileResponse("index.html")


@app.post("/compile")
def compile_dsl(data: DSLInput):
    result = {
        "lexer":    {"success": False, "tokens": [], "error": None},
        "parser":   {"success": False, "ast": [],    "error": None},
        "semantic": {"success": False, "statements": [], "tempo": None,
                     "instrument": None, "program": None, "error": None},
        "ir":       {"success": False, "timeline": [], "total_duration": None, "error": None},
        "midi":     {"success": False, "file": None,  "error": None},
    }

    # ── Step 1: Lexer ─────────────────────────────────
    try:
        tokens = tokenize(data.code)
        result["lexer"]["success"] = True
        result["lexer"]["tokens"] = [
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
        result["parser"]["ast"] = [repr(s) for s in ast.statements]
    except Exception as e:
        result["parser"]["error"] = str(e)
        return result

    # ── Step 3: Semantic ──────────────────────────────
    try:
        analyzer = SemanticAnalyzer()
        statements, tempo, instrument, program = analyzer.analyze(ast)
        result["semantic"]["success"] = True
        result["semantic"]["statements"] = [repr(s) for s in statements]
        result["semantic"]["tempo"] = tempo
        result["semantic"]["instrument"] = instrument
        result["semantic"]["program"] = program
    except Exception as e:
        result["semantic"]["error"] = str(e)
        return result

    # ── Step 4: IR ────────────────────────────────────
    try:
        builder = IRBuilder(tempo)
        timeline = builder.build(statements)
        result["ir"]["success"] = True
        result["ir"]["total_duration"] = round(builder.current_time, 2)
        result["ir"]["timeline"] = [
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
        result["midi"]["file"] = "output.mid"
    except Exception as e:
        result["midi"]["error"] = str(e)

    return result


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="127.0.0.1", port=8000, reload=True)
