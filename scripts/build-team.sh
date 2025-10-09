#!/bin/bash

# PokéAI Team Builder Script

set -e

# Configuration
FORMAT=${1:-"gen9ou"}
OUTPUT_DIR="data/teams"
OUTPUT_FILE="$OUTPUT_DIR/latest.json"

echo "Building team for format: $FORMAT"

# Create output directory
mkdir -p "$OUTPUT_DIR"

# Build team using CLI
python services/teambuilder/cli_build.py \
    --format "$FORMAT" \
    --out "$OUTPUT_FILE" \
    --include-tera \
    --role-hints "sweeper" "wall" "hazard_setter"

if [ $? -eq 0 ]; then
    echo "Team built successfully!"
    echo "Output: $OUTPUT_FILE"
    
    # Show team summary
    if command -v jq &> /dev/null; then
        echo ""
        echo "Team Summary:"
        jq -r '.team.pokemon[] | "\(.species) @ \(.item // "No Item") (\(.ability))"' "$OUTPUT_FILE"
    fi
else
    echo "Failed to build team"
    exit 1
fi
