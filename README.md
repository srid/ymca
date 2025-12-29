# YMCA Schedule

Extract and view YMCA Saint-Roch schedule data.

## Setup

```bash
nix develop
```

## Usage

```bash
# Extract schedule from HTML to JSON
just extract schedules/2026-q1-group-swim.html > schedules/2026-q1-group-swim.json

# Validate JSON files
just validate

# View schedule in browser (http://localhost:8000)
just serve
```

## Files

- `schedules/*.html` — Source schedule HTML (saved from YMCA website)
- `schedules/*.json` — Extracted schedule data (filename matches HTML)
- `scripts/parse_schedule.py` — HTML to JSON parser
- `index.html` — Browser viewer with activity/period filters

## JSON Schema

```json
{
  "meta": {
    "season": "Winter 2026",
    "start_date": "2026-01-05",
    "end_date": "2026-03-22"
  },
  "events": {
    "Monday": [
      {
        "activity": "Lane Swim",
        "start": "07:00",
        "end": "08:55",
        "lanes": 5
      },
      {
        "activity": "Pilates",
        "start": "17:00",
        "end": "18:00",
        "location": "Studio 2-3",
        "instructor": "Gabrielle",
        "intensity": "moderate"
      }
    ]
  }
}
```
