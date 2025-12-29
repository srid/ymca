# YMCA Schedule

Extract and view YMCA Saint-Roch schedule data.

## Setup

```bash
nix develop
```

## Usage

```bash
# Extract text from a PDF
just extract schedules/2026-q1-group-swim.pdf

# Validate JSON files
just validate

# View schedule in browser (http://localhost:8000)
just serve
```

## Files

- `schedules/*.pdf` — Source schedule PDFs
- `schedules/*.json` — Extracted schedule data (filename matches PDF)
- `index.html` — Browser viewer for sanity-checking JSON
