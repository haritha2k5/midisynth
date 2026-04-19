# run_tests.py - MidiSynth Test Runner
# Tests both valid and invalid DSL inputs
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from semantic import SemanticAnalyzer, SemanticError
from parser import Parser
from lexer import tokenize


# Add parent directory to path so we can import our modules
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))


# ---------------------------------------------------------------------------
# Test cases - (filename, expected_result, description)
# expected_result: 'pass' or 'fail'
# ---------------------------------------------------------------------------
TEST_CASES = [
    ('test_valid.msynth',            'pass', 'Valid input with all features'),
    ('test_invalid_note.msynth',     'fail', 'Invalid note X4'),
    ('test_invalid_duration.msynth', 'fail', 'Invalid duration TRIPLET'),
    ('test_missing_tempo.msynth',    'fail', 'Missing TEMPO declaration'),
    ('test_missing_instrument.msynth', 'fail', 'Missing INSTRUMENT declaration'),
    ('test_invalid_instrument.msynth', 'fail', 'Invalid instrument: sitar'),
    ('test_invalid_tempo1.msynth',    'fail', 'Tempo out of range (500)'),
    ('test_invalid_repeat.msynth',   'fail', 'Repeat count of 0'),
]

# ---------------------------------------------------------------------------
# Run all tests
# ---------------------------------------------------------------------------


def run_tests():
    passed = 0
    failed = 0
    errors = 0

    print("=" * 60)
    print("  MidiSynth Test Suite")
    print("=" * 60)

    for filename, expected, description in TEST_CASES:
        filepath = os.path.join(os.path.dirname(__file__), filename)

        try:
            with open(filepath, 'r') as f:
                source = f.read()

            tokens = tokenize(source)
            ast = Parser(tokens).parse()
            analyzer = SemanticAnalyzer()
            analyzer.analyze(ast)

            # If we reach here, the analysis passed
            actual = 'pass'

        except (SyntaxError, SemanticError, ValueError, TypeError) as e:
            actual = 'fail'
            error_msg = str(e)

        except Exception as e:
            actual = 'error'
            error_msg = str(e)

        # Check result
        if actual == expected:
            status = '✓ PASS'
            passed += 1
            print(f"\n{status} | {description}")
            if expected == 'fail':
                print(f"         Correctly rejected → {error_msg}")
        elif actual == 'error':
            status = '! ERROR'
            errors += 1
            print(f"\n{status} | {description}")
            print(f"         Unexpected error → {error_msg}")
        else:
            status = '✗ FAIL'
            failed += 1
            print(f"\n{status} | {description}")
            if expected == 'pass':
                print(
                    f"         Should have passed but got error → {error_msg}")
            else:
                print(f"         Should have been rejected but passed!")

    # Summary
    print("\n" + "=" * 60)
    print(f"  Results: {passed} passed | {failed} failed | {errors} errors")
    print(f"  Total  : {len(TEST_CASES)} tests")
    print("=" * 60)


if __name__ == '__main__':
    run_tests()
