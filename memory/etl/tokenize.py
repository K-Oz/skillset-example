#!/usr/bin/env python3
"""
Tokenize and clean raw text for memory atom processing.
Part of the ETL pipeline for Marduk's Cognitive Tokamak.
"""

import re
import json
import hashlib
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional

def clean_text(text: str) -> str:
    """Basic text cleaning operations."""
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    # Normalize quotes
    text = text.replace('"', '"').replace('"', '"')
    return text.strip()

def tokenize_document(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Process a raw document into a structured format ready for classification."""
    if 'content' not in doc:
        raise ValueError("Document must contain 'content' field")
    
    # Clean the content
    cleaned_content = clean_text(doc['content'])
    
    # Generate content hash
    content_hash = f"sha256:{hashlib.sha256(cleaned_content.encode()).hexdigest()}"
    
    # Generate basic tokens (simplified for now)
    tokens = cleaned_content.split()
    
    return {
        "original": doc,
        "cleaned_content": cleaned_content,
        "content_hash": content_hash,
        "token_count": len(tokens),
        "timestamp": datetime.now().isoformat(),
        "processed": True
    }

def process_batch(input_file: str, output_file: str) -> None:
    """Process a batch of documents from input file and write to output file."""
    with open(input_file, 'r') as f:
        documents = json.load(f)
    
    processed_docs = [tokenize_document(doc) for doc in documents]
    
    with open(output_file, 'w') as f:
        json.dump(processed_docs, f, indent=2)
    
    print(f"Processed {len(processed_docs)} documents.")
    print(f"Output written to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Tokenize and clean text documents")
    parser.add_argument('-i', '--input', required=True, help='Input JSON file with raw documents')
    parser.add_argument('-o', '--output', required=True, help='Output file for processed documents')
    
    args = parser.parse_args()
    process_batch(args.input, args.output)

if __name__ == "__main__":
    main()