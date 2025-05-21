#!/usr/bin/env python3
"""
Prepare memory atoms for language model fine-tuning.
Converts memory atoms into training examples for fine-tuning.
"""

import os
import json
import argparse
from typing import Dict, List, Any, Union
import random

def memory_atom_to_training_example(atom: Dict[str, Any]) -> Dict[str, str]:
    """
    Convert a memory atom to a training example for language model fine-tuning.
    
    Creates input-output pairs that teach the model to:
    1. Generate content based on metadata
    2. Classify content into memory types
    3. Extract tags and actors
    4. Answer questions about the memory
    """
    # Extract atom properties
    atom_id = atom.get('id', '')
    atom_type = atom.get('type', '')
    content = atom.get('content', '')
    tags = atom.get('tags', [])
    actors = atom.get('actors', [])
    
    # Choose a random training task for this atom
    task_type = random.choice([
        'generation', 'classification', 'tag_extraction', 
        'actor_extraction', 'question_answering'
    ])
    
    if task_type == 'generation':
        # Task: Generate content based on type and tags
        prompt = f"Create a {atom_type} memory about {', '.join(tags[:3])}."
        completion = content
        
    elif task_type == 'classification':
        # Task: Classify content into memory type
        prompt = f"Classify the following content into a memory type (declarative, episodic, procedural, or semantic):\n\n{content}"
        completion = f"This is a {atom_type} memory."
        
    elif task_type == 'tag_extraction':
        # Task: Extract tags from content
        prompt = f"Extract relevant tags from the following content:\n\n{content}"
        completion = f"Tags: {', '.join(tags)}"
        
    elif task_type == 'actor_extraction':
        # Task: Extract actors from content
        prompt = f"Identify the actors mentioned in the following content:\n\n{content}"
        completion = f"Actors: {', '.join(actors) if actors else 'No specific actors mentioned'}"
        
    else:  # question_answering
        # Task: Answer a question about the memory
        # Choose a random question type
        question_type = random.choice([
            'summary', 'key_concept', 'relation', 'timeline'
        ])
        
        if question_type == 'summary':
            prompt = f"Summarize the following memory in one sentence:\n\n{content}"
            completion = f"This memory describes {' '.join(content.split()[:10])}..."
            
        elif question_type == 'key_concept':
            concepts = [tag.replace('-', ' ') for tag in tags]
            prompt = f"What are the key concepts in this memory?\n\n{content}"
            completion = f"The key concepts are: {', '.join(concepts)}"
            
        elif question_type == 'relation':
            prompt = f"How does this memory relate to the concept of '{random.choice(tags).replace('-', ' ')}'?\n\n{content}"
            completion = f"This memory relates to {random.choice(tags).replace('-', ' ')} by describing aspects of {atom_type} knowledge."
            
        else:  # timeline
            prompt = f"When did the events in this memory occur?\n\n{content}"
            # Extract date if available
            if 'created_at' in atom:
                date = atom['created_at'].split('T')[0]
                completion = f"This memory is from {date}."
            else:
                completion = "The specific timing is not clearly indicated in this memory."
    
    return {
        "prompt": prompt,
        "completion": completion,
        "atom_id": atom_id,  # Include for reference
        "task_type": task_type  # Include for analysis
    }

def convert_atoms_to_training_data(input_file: str, output_file: str) -> None:
    """
    Convert memory atoms to fine-tuning examples.
    
    Args:
        input_file: Path to input JSON file with memory atoms
        output_file: Path to output JSONL file for fine-tuning data
    """
    # Ensure output directory exists
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Load memory atoms
    with open(input_file, 'r') as f:
        atoms = json.load(f)
    
    print(f"Loaded {len(atoms)} memory atoms")
    
    # Convert to training examples
    training_examples = []
    for atom in atoms:
        # Create multiple training examples from each atom
        num_examples = random.randint(1, 3)  # 1-3 examples per atom
        for _ in range(num_examples):
            example = memory_atom_to_training_example(atom)
            training_examples.append(example)
    
    print(f"Generated {len(training_examples)} training examples")
    
    # Write as JSONL (each line is a JSON object)
    with open(output_file, 'w') as f:
        for example in training_examples:
            f.write(json.dumps(example) + '\n')
    
    print(f"Training data written to {output_file}")
    
    # Report task type distribution
    task_counts = {}
    for example in training_examples:
        task_type = example["task_type"]
        task_counts[task_type] = task_counts.get(task_type, 0) + 1
    
    print("\nTask distribution:")
    for task, count in task_counts.items():
        print(f"  {task}: {count} examples ({count/len(training_examples)*100:.1f}%)")

def main():
    parser = argparse.ArgumentParser(description="Prepare memory atoms for fine-tuning")
    parser.add_argument('--input', required=True, help='Input JSON file with memory atoms')
    parser.add_argument('--output', required=True, help='Output JSONL file for fine-tuning data')
    
    args = parser.parse_args()
    convert_atoms_to_training_data(args.input, args.output)

if __name__ == "__main__":
    main()