#!/bin/bash
# ETL Pipeline Runner

set -e

# Directory setup
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"
MEMORY_DIR="$ROOT_DIR/memory"
DATA_DIR="$MEMORY_DIR/samples"
OUTPUT_DIR="$MEMORY_DIR/atoms"

# Ensure directories exist
mkdir -p "$OUTPUT_DIR"

# Log function
log() {
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1"
}

# Process a single file
process_file() {
  local input_file="$1"
  local filename=$(basename "$input_file")
  local name="${filename%.*}"
  
  log "Processing file: $filename"
  
  # Step 1: Tokenize
  local tokenized_file="$OUTPUT_DIR/temp_${name}_tokenized.json"
  log "  Tokenizing..."
  python "$SCRIPT_DIR/tokenize.py" -i "$input_file" -o "$tokenized_file"
  
  # Step 2: Classify
  local classified_file="$OUTPUT_DIR/temp_${name}_classified.json"
  log "  Classifying..."
  python "$SCRIPT_DIR/classify.py" -i "$tokenized_file" -o "$classified_file"
  
  # Step 3: Embed
  local output_file="$OUTPUT_DIR/${name}_atoms.json"
  log "  Adding embeddings..."
  python "$SCRIPT_DIR/embed.py" -i "$classified_file" -o "$output_file"
  
  # Clean up temporary files
  rm "$tokenized_file" "$classified_file"
  
  log "Completed processing: $filename -> $output_file"
}

# Process all files in data directory
process_all() {
  log "Starting ETL pipeline for all files in $DATA_DIR"
  
  for file in "$DATA_DIR"/*.json; do
    if [ -f "$file" ]; then
      process_file "$file"
    fi
  done
  
  log "ETL pipeline completed successfully"
}

# Process specific file
process_specific() {
  local input_file="$1"
  
  if [ ! -f "$input_file" ]; then
    log "Error: File not found: $input_file"
    exit 1
  fi
  
  process_file "$input_file"
}

# Main execution
if [ $# -eq 0 ]; then
  # No arguments, process all files
  process_all
else
  # Process specific file
  process_specific "$1"
fi