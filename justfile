# YMCA Schedule Management Tasks
# Run `just` or `just --list` to see available commands

# Default recipe: show help
default:
    @just --list

# Extract text from a schedule PDF
# Usage: just extract schedules/2026-q1-group-swim.pdf
extract pdf:
    extract-pdf {{pdf}}

# Validate all JSON files in schedules/
validate:
    @echo "Validating JSON files..."
    @for f in schedules/*.json; do \
        if [ -f "$f" ]; then \
            echo "  Checking $f"; \
            jq empty "$f" && echo "    ✓ Valid" || echo "    ✗ Invalid"; \
        fi \
    done

# Pretty-print a JSON schedule file
show json:
    jq '.' {{json}}

# Start a local server to view schedules in browser
# Open http://localhost:8000 after running
serve:
    @echo "Starting server at http://localhost:8000"
    python3 -m http.server 8000
