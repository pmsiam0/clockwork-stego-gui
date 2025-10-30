# Clockwork Stego GUI

Encode text into a grid of clock faces (SVG) and decode it back. Pure Python 3 + Tkinter.

## Features
- Two-hand clock encoding, 8 discrete positions per hand
- 6 bits per clock cell
- Optional passphrase-derived XOR key
- No external dependencies

## Quick start
```

python3 -m venv .venv
source .venv/bin/activate
python app.py

```

## Usage
- Encode tab: type a message, optionally set a passphrase and column count, Save SVG.
- Decode tab: pick an SVG exported by this tool, optionally enter the passphrase, Decode to recover text.

## Notes
- Output is SVG for lossless angles.
- For PNG distribution, rasterize the SVG externally; decoding from PNG is not supported.
