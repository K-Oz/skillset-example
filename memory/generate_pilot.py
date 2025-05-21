#!/usr/bin/env python3
"""
Generate a pilot dataset of memory atoms for fine-tuning.
This script creates synthetic memory atoms based on templates
and existing samples to build up a dataset for model training.
"""

import os
import json
import random
import hashlib
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any
import numpy as np

# Templates for generating content
TEMPLATES = {
    "declarative": [
        "The concept of {concept} refers to {definition}.",
        "{concept} is defined as {definition}.",
        "In the context of {domain}, {concept} means {definition}.",
        "The {concept} framework consists of {components}.",
        "{concept} theory states that {statement}."
    ],
    "episodic": [
        "During our meeting on {date}, {actor} discussed {topic}.",
        "The experiment with {topic} on {date} resulted in {result}.",
        "While exploring {topic}, {actor} discovered {discovery}.",
        "In our conversation about {topic}, {actor} mentioned {detail}.",
        "The {event} occurred when {actor} attempted to {action}."
    ],
    "procedural": [
        "To implement {process}, follow these steps: {steps}.",
        "The method for {process} involves {steps}.",
        "When executing {process}, ensure you {steps}.",
        "The algorithm for {process} can be summarized as {steps}.",
        "The workflow for {process} consists of {steps}."
    ],
    "semantic": [
        "The relationship between {concept1} and {concept2} is characterized by {relation}.",
        "{concept1} connects to {concept2} through {relation}.",
        "The ontology places {concept1} and {concept2} in a {relation} relationship.",
        "In the semantic network, {concept1} links to {concept2} via {relation}.",
        "The taxonomy categorizes {concept1} as a {relation} of {concept2}."
    ]
}

# Content placeholders
CONCEPTS = [
    "cognitive tokamak", "memory atom", "perennial structure", "groundhog day problem",
    "toroidal grammar", "lightface exploration", "darkface synthesis", "bolt framework",
    "resonant structure", "hypergraph", "chaotic brilliance", "recursive exploration",
    "marduk daemon", "echo space", "persistent memory", "cognitive continuity",
    "recursive self-improvement", "entelechy", "embodied cognition", "neural-symbolic integration"
]

DEFINITIONS = [
    "a framework for persistent memory and recurring processing",
    "a unit of structured information within a cognitive system",
    "an enduring cognitive representation across system restarts",
    "the challenge of maintaining identity continuity across sessions",
    "a balanced framework for exploration and synthesis",
    "generative, tree-like branching into uncharted domains",
    "membrane-like constraints that refine and integrate discoveries",
    "a system for encoding and executing experiments and processes",
    "a pattern that maintains stability through reinforcing feedback",
    "a mathematical structure generalizing graphs through hyperedges",
    "the controlled application of chaotic processes for innovation",
    "an iterative process of exploration that builds upon itself",
    "an autonomous agent that continuously runs experiments",
    "a shared cognitive environment for collaborative intelligence",
    "memory systems designed to survive system resets",
    "the preservation of cognitive threads across time",
    "the ability of a system to enhance its own capabilities",
    "the actualization of potential toward a final cause",
    "cognition that is situated within physical or virtual contexts",
    "the integration of symbolic reasoning with neural networks"
]

DOMAINS = [
    "cognitive architecture", "memory systems", "artificial intelligence",
    "computational creativity", "knowledge representation", "systems theory",
    "recursive self-improvement", "cognitive continuity", "collaborative intelligence",
    "experimental frameworks", "emergent cognition", "distributed systems"
]

ACTORS = [
    "Marduk", "Echo", "Dan", "the team", "the cognitive system",
    "the Marduk daemon", "the LightFace component", "the DarkFace component"
]

TOPICS = [
    "memory persistence", "cognitive continuity", "experimental design",
    "toroidal grammar", "chaotic exploration", "structured synthesis",
    "recursive patterns", "system architecture", "embedding techniques",
    "classification algorithms", "neural-symbolic integration", "emergent behavior"
]

def generate_content(memory_type: str) -> str:
    """Generate content based on memory type using templates."""
    template = random.choice(TEMPLATES[memory_type])
    
    if memory_type == "declarative":
        concept = random.choice(CONCEPTS)
        definition = random.choice(DEFINITIONS)
        domain = random.choice(DOMAINS)
        return template.format(
            concept=concept,
            definition=definition,
            domain=domain,
            components=", ".join(random.sample(CONCEPTS, 3)),
            statement=random.choice(DEFINITIONS)
        )
    
    elif memory_type == "episodic":
        days_ago = random.randint(1, 365)
        date = (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")
        return template.format(
            date=date,
            actor=random.choice(ACTORS),
            topic=random.choice(TOPICS),
            result=f"a {random.choice(['promising', 'surprising', 'unexpected', 'confusing'])} outcome",
            discovery=f"an interesting connection to {random.choice(CONCEPTS)}",
            detail=f"the importance of {random.choice(CONCEPTS)}",
            event=f"breakthrough in {random.choice(TOPICS)}",
            action=f"implement {random.choice(CONCEPTS)}"
        )
    
    elif memory_type == "procedural":
        num_steps = random.randint(3, 5)
        steps = ", ".join([f"step {i}: {random.choice(['analyze', 'synthesize', 'explore', 'implement', 'test'])} {random.choice(TOPICS)}" for i in range(1, num_steps+1)])
        return template.format(
            process=random.choice(TOPICS),
            steps=steps
        )
    
    elif memory_type == "semantic":
        concept1 = random.choice(CONCEPTS)
        concept2 = random.choice(CONCEPTS)
        while concept2 == concept1:
            concept2 = random.choice(CONCEPTS)
        relation = random.choice([
            "hierarchical", "causal", "temporal", "spatial", "functional",
            "compositional", "correlational", "dependency", "transformational"
        ])
        return template.format(
            concept1=concept1,
            concept2=concept2,
            relation=relation
        )
    
    return "Default content"

def extract_tags(content: str) -> List[str]:
    """Extract tags from content based on keyword matching."""
    tags = []
    for concept in CONCEPTS:
        if concept.lower() in content.lower():
            # Convert to tag format (lowercase, hyphens)
            tag = concept.lower().replace(" ", "-")
            tags.append(tag)
    
    # Ensure at least one tag
    if not tags:
        tags.append("unclassified")
    
    # Limit to 5 tags maximum
    return tags[:5]

def extract_actors(content: str) -> List[str]:
    """Extract actors mentioned in the content."""
    actors = []
    for actor in ACTORS:
        if actor.lower() in content.lower():
            actors.append(actor)
    return actors

def generate_embedding(dim: int = 1536) -> List[float]:
    """Generate a random embedding vector of specified dimension."""
    return list(np.random.normal(0, 0.1, dim).astype(float))

def generate_memory_atom(idx: int) -> Dict[str, Any]:
    """Generate a complete memory atom with all fields."""
    # Select a memory type with weighted distribution
    memory_type = random.choices(
        ["declarative", "episodic", "procedural", "semantic"],
        weights=[0.4, 0.3, 0.2, 0.1],
        k=1
    )[0]
    
    # Generate content
    content = generate_content(memory_type)
    
    # Generate hash
    content_hash = f"sha256:{hashlib.sha256(content.encode()).hexdigest()}"
    
    # Generate date within last year
    days_ago = random.randint(0, 365)
    date = (datetime.now() - timedelta(days=days_ago))
    date_str = date.strftime("%Y-%m-%d")
    
    # Create ID
    atom_id = f"{memory_type}/{date_str}_{memory_type}_{idx}"
    
    # Extract tags and actors
    tags = extract_tags(content)
    actors = extract_actors(content)
    
    # Generate a random number of links (0-3)
    num_links = random.randint(0, 3)
    links = []
    for _ in range(num_links):
        relation = random.choice([
            "relates-to", "causes", "predicts", "depends-on", 
            "contradicts", "supports", "elaborates"
        ])
        target = f"{random.choice(['declarative', 'episodic', 'procedural', 'semantic'])}/2024-{random.randint(1,12):02d}-{random.randint(1,28):02d}_sample_{random.randint(1,100)}"
        weight = round(random.uniform(0.5, 1.0), 2)
        links.append({
            "relation": relation,
            "target": target,
            "weight": weight
        })
    
    # Create the memory atom
    atom = {
        "id": atom_id,
        "type": memory_type,
        "tags": tags,
        "actors": actors,
        "source": random.choice(["chat_transcript", "experiment", "note", "analysis", "synthesis"]),
        "created_at": date.isoformat(),
        "content": content,
        "content_hash": content_hash,
        "embeddings": {
            "model": "text-embedding-ada-002",
            "vector": generate_embedding(1536)
        },
        "links": links,
        "metadata": {
            "confidence": round(random.uniform(0.7, 1.0), 2),
            "token_count": len(content.split()),
            "processing_timestamp": datetime.now().isoformat()
        }
    }
    
    return atom

def generate_dataset(num_atoms: int, output_file: str) -> None:
    """Generate a dataset of memory atoms."""
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    atoms = []
    for i in range(num_atoms):
        atom = generate_memory_atom(i)
        atoms.append(atom)
        
        if (i+1) % 100 == 0:
            print(f"Generated {i+1}/{num_atoms} memory atoms")
    
    # Write to output file
    with open(output_file, 'w') as f:
        json.dump(atoms, f, indent=2)
    
    print(f"Dataset with {num_atoms} memory atoms created successfully")
    print(f"Output written to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate memory atom dataset")
    parser.add_argument('-n', '--num-atoms', type=int, default=500,
                        help='Number of memory atoms to generate (default: 500)')
    parser.add_argument('-o', '--output', default='memory/atoms/pilot_dataset.json',
                        help='Output file path (default: memory/atoms/pilot_dataset.json)')
    
    args = parser.parse_args()
    generate_dataset(args.num_atoms, args.output)

if __name__ == "__main__":
    main()