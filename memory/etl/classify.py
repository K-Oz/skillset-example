#!/usr/bin/env python3
"""
Classify tokenized text into memory atom types.
Part of the ETL pipeline for Marduk's Cognitive Tokamak.
"""

import json
import argparse
import re
from typing import Dict, List, Any, Tuple
from datetime import datetime

# Simple rule-based classifier patterns
PATTERNS = {
    "declarative": [
        r'\bfact\b', r'\bdefinition\b', r'\bconcept\b', r'\bframework\b',
        r'\btheory\b', r'\bprinciple\b', r'\bmethod\b'
    ],
    "episodic": [
        r'\bexperience\b', r'\bmeeting\b', r'\bconversation\b', r'\bsession\b',
        r'\bevent\b', r'\bincident\b', r'\bjourney\b', r'\binteraction\b'
    ],
    "procedural": [
        r'\bstep\b', r'\bprocess\b', r'\bmethod\b', r'\bworkflow\b',
        r'\bprotocol\b', r'\balgorithm\b', r'\bprocedure\b', r'\bimplement\b'
    ],
    "semantic": [
        r'\brelationship\b', r'\bconnection\b', r'\bnetwork\b', r'\bontology\b',
        r'\btaxonomy\b', r'\bsemantic\b', r'\bmeaning\b', r'\bsignificance\b'
    ]
}

def extract_tags(text: str) -> List[str]:
    """Extract potential tags from text based on keywords and phrases."""
    # Very simplified tag extraction - in a real system, this would be more sophisticated
    tag_candidates = []
    
    # Check for some common themes in the Marduk project
    if re.search(r'\bcontinuity\b', text, re.I): tag_candidates.append("continuity")
    if re.search(r'\bidentity\b', text, re.I): tag_candidates.append("identity")
    if re.search(r'\bdesign\b', text, re.I): tag_candidates.append("design")
    if re.search(r'\bchaos\b', text, re.I): tag_candidates.append("chaos")
    if re.search(r'\btokamak\b', text, re.I): tag_candidates.append("tokamak")
    if re.search(r'\bgrammar\b', text, re.I): tag_candidates.append("grammar")
    if re.search(r'\btoroidal\b', text, re.I): tag_candidates.append("toroidal")
    if re.search(r'\bmemory\b', text, re.I): tag_candidates.append("memory")
    if re.search(r'\bexperiment\b', text, re.I): tag_candidates.append("experiment")
    
    # Ensure at least one tag
    if not tag_candidates:
        tag_candidates.append("unclassified")
        
    return tag_candidates

def extract_actors(text: str) -> List[str]:
    """Extract potential actors mentioned in the text."""
    actors = []
    
    # Look for common actors in the Marduk project
    if re.search(r'\bmarduk\b', text, re.I): actors.append("Marduk")
    if re.search(r'\becho\b', text, re.I): actors.append("Echo")
    if re.search(r'\bdan\b', text, re.I): actors.append("Dan")
    
    return actors

def classify_text(doc: Dict[str, Any]) -> Tuple[str, float]:
    """Classify text into memory atom type using rule-based patterns."""
    if 'cleaned_content' not in doc:
        raise ValueError("Document must contain 'cleaned_content' field")
    
    text = doc['cleaned_content']
    scores = {}
    
    # Count pattern matches for each type
    for memory_type, patterns in PATTERNS.items():
        score = 0
        for pattern in patterns:
            matches = re.findall(pattern, text, re.I)
            score += len(matches)
        scores[memory_type] = score
    
    # Find the type with the highest score
    if not scores or max(scores.values()) == 0:
        return "declarative", 0.5  # Default if no patterns match
    
    best_type = max(scores, key=scores.get)
    total = sum(scores.values())
    confidence = scores[best_type] / total if total > 0 else 0.5
    
    return best_type, confidence

def process_batch(input_file: str, output_file: str) -> None:
    """Process a batch of tokenized documents and classify them into memory atoms."""
    with open(input_file, 'r') as f:
        documents = json.load(f)
    
    memory_atoms = []
    
    for idx, doc in enumerate(documents):
        memory_type, confidence = classify_text(doc)
        
        # Generate a basic ID (in practice, would be more sophisticated)
        date_str = datetime.now().strftime("%Y-%m-%d")
        atom_id = f"{memory_type}/{date_str}_memory_{idx}"
        
        # Extract tags and actors
        tags = extract_tags(doc['cleaned_content'])
        actors = extract_actors(doc['cleaned_content'])
        
        # Create the memory atom
        atom = {
            "id": atom_id,
            "type": memory_type,
            "tags": tags,
            "confidence": confidence,
            "actors": actors,
            "source": doc.get("original", {}).get("source", "unknown"),
            "created_at": datetime.now().isoformat(),
            "content": doc['cleaned_content'],
            "content_hash": doc['content_hash'],
            # Embeddings would be added in a later stage
            "links": []  # Links would be added in a later stage
        }
        
        memory_atoms.append(atom)
    
    with open(output_file, 'w') as f:
        json.dump(memory_atoms, f, indent=2)
    
    print(f"Classified {len(memory_atoms)} documents into memory atoms.")
    print(f"Output written to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Classify documents into memory atoms")
    parser.add_argument('-i', '--input', required=True, help='Input JSON file with tokenized documents')
    parser.add_argument('-o', '--output', required=True, help='Output file for memory atoms')
    
    args = parser.parse_args()
    process_batch(args.input, args.output)

if __name__ == "__main__":
    main()