# render.py - MidiSynth Audio Renderer
# Plays the generated .mid file using Windows built-in MIDI player
# Falls back to pygame if available

import os
import sys
import time
import subprocess


class Renderer:
    def __init__(self, midi_file='output.mid'):
        self.midi_file = os.path.abspath(midi_file)

    def play(self):
        """Play the MIDI file."""

        if not os.path.exists(self.midi_file):
            raise FileNotFoundError(f"MIDI file not found: {self.midi_file}")

        print(f"Playing: {self.midi_file}\n")

        if sys.platform == 'win32':
            self._play_windows()
        elif sys.platform == 'darwin':
            self._play_mac()
        else:
            self._play_linux()

    def _play_windows(self):
        """Use Windows Media Player via PowerShell to play MIDI."""
        try:
            print("Using Windows Media Player...")
            # Open with default MIDI player (usually Windows Media Player)
            os.startfile(self.midi_file)
            print("Playback started in Windows Media Player.")
            print("Close the player when done.\n")

            # Wait for user to confirm done
            input("Press Enter here when playback is complete...")
            print("Playback complete!")

        except Exception as e:
            print(f"Windows playback failed: {e}")
            print("Try opening output.mid manually by double-clicking it.")

    def _play_mac(self):
        subprocess.run(['afplay', self.midi_file])
        print("Playback complete!")

    def _play_linux(self):
        subprocess.run(['timidity', self.midi_file])
        print("Playback complete!")


# ---------------------------------------------------------------------------
# Quick test
# ---------------------------------------------------------------------------
if __name__ == '__main__':
    renderer = Renderer('output.mid')
    renderer.play()
