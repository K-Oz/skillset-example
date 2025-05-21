#!/usr/bin/env python3
"""
Full ETL pipeline for Marduk's Cognitive Tokamak memory system.
Processes raw data into memory atoms with embeddings.
"""

import os
import json
import argparse
import hashlib
from datetime import datetime
from typing import Dict, List, Any, Optional

# Import the individual ETL components
from tokenize import tokenize_document
from classify import classify_text, extract_tags, extract_actors
from embed import generate_embedding

def process_document(raw_doc: Dict[str, Any], model_name: str = "text-embedding-ada-002") -> Dict[str, Any]:
    """
    Process a single document through the entire ETL pipeline.
    
    Args:
        raw_doc: Raw document with at least a 'content' field
        model_name: Name of the embedding model to use
        
    Returns:
        Memory atom with all components processed
    """
    # Step 1: Tokenize and clean
    tokenized = tokenize_document(raw_doc)
    
    # Step 2: Classify
    memory_type, confidence = classify_text(tokenized)
    
    # Generate a basic ID 
    date_str = datetime.now().strftime("%Y-%m-%d")
    content_hash_short = tokenized['content_hash'].split(':')[1][:8]
    atom_id = f"{memory_type}/{date_str}_{content_hash_short}"
    
    # Extract tags and actors
    tags = extract_tags(tokenized['cleaned_content'])
    actors = extract_actors(tokenized['cleaned_content'])
    
    # Step 3: Generate embeddings
    embedding_vector = generate_embedding(tokenized['cleaned_content'], model_name)
    
    # Create the complete memory atom
    atom = {
        "id": atom_id,
        "type": memory_type,
        "tags": tags,
        "confidence": confidence,
        "actors": actors,
        "source": raw_doc.get("source", "unknown"),
        "created_at": datetime.now().isoformat(),
        "content": tokenized['cleaned_content'],
        "content_hash": tokenized['content_hash'],
        "embeddings": {
            "model": model_name,
            "vector": embedding_vector
        },
        "links": [],  # Links would be added in a later stage
        "metadata": {
            "token_count": tokenized['token_count'],
            "processing_timestamp": datetime.now().isoformat()
        }
    }
    
    return atom

def process_batch(input_file: str, output_file: str, model_name: str) -> None:
    """
    Process a batch of raw documents through the entire ETL pipeline.
    
    Args:
        input_file: Path to input JSON file with raw documents
        output_file: Path to output file for processed memory atoms
        model_name: Name of the embedding model to use
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Load raw documents
    with open(input_file, 'r') as f:
        raw_docs = json.load(f)
    
    # Process each document
    memory_atoms = []
    for raw_doc in raw_docs:
        try:
            atom = process_document(raw_doc, model_name)
            memory_atoms.append(atom)
        except Exception as e:
            print(f"Error processing document: {e}")
            continue
    
    # Write processed atoms to output file
    with open(output_file, 'w') as f:
        json.dump(memory_atoms, f, indent=2)
    
    print(f"Processed {len(memory_atoms)} documents into memory atoms.")
    print(f"Output written to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Full ETL pipeline for memory atoms")
    parser.add_argument('-i', '--input', required=True, help='Input JSON file with raw documents')
    parser.add_argument('-o', '--output', required=True, help='Output file for processed memory atoms')
    parser.add_argument('-m', '--model', default="text-embedding-ada-002", 
                        help='Embedding model to use (default: text-embedding-ada-002)')
    
    args = parser.parse_args()
    process_batch(args.input, args.output, args.model)

if __name__ == "__main__":
    main()