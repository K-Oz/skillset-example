#!/usr/bin/env python3
"""
Memory Atom Retriever for RAG systems.
Efficiently retrieves relevant memory atoms for a given query.
"""

import os
import json
import argparse
import numpy as np
from typing import Dict, List, Any, Union, Tuple
import random  # For the demo simulation

class MemoryAtomRetriever:
    def __init__(self, atom_store_path: str, embedding_model: str = "text-embedding-ada-002"):
        """
        Initialize the retriever with a path to the memory atom store.
        
        Args:
            atom_store_path: Path to the directory containing memory atoms
            embedding_model: Name of the embedding model to use
        """
        self.atom_store_path = atom_store_path
        self.embedding_model = embedding_model
        self.atoms = []
        self.atom_embeddings = []
        
        # Load atoms (in a real implementation, this would be more efficient)
        self._load_atoms()
    
    def _load_atoms(self) -> None:
        """Load memory atoms from the store."""
        if not os.path.exists(self.atom_store_path):
            print(f"Atom store not found: {self.atom_store_path}")
            return
        
        try:
            # Load all JSON files in the directory
            atom_files = [f for f in os.listdir(self.atom_store_path) if f.endswith('.json')]
            
            for file_name in atom_files:
                file_path = os.path.join(self.atom_store_path, file_name)
                with open(file_path, 'r') as f:
                    atoms = json.load(f)
                    
                    # If the file contains a list of atoms
                    if isinstance(atoms, list):
                        for atom in atoms:
                            if 'embeddings' in atom and 'vector' in atom['embeddings']:
                                self.atoms.append(atom)
                                self.embedding = atom['embeddings']['vector']
                                self.atom_embeddings.append(atom['embeddings']['vector'])
                    # If the file contains a single atom
                    elif isinstance(atoms, dict) and 'embeddings' in atoms:
                        self.atoms.append(atoms)
                        self.atom_embeddings.append(atoms['embeddings']['vector'])
            
            print(f"Loaded {len(self.atoms)} memory atoms with embeddings")
        
        except Exception as e:
            print(f"Error loading atoms: {e}")
    
    def _compute_query_embedding(self, query: str) -> List[float]:
        """
        Compute embedding for a query.
        In a real implementation, this would call an embedding model API.
        """
        # Simulated embedding generation
        embedding_dim = 1536  # Default for text-embedding-ada-002
        return list(np.random.normal(0, 0.1, embedding_dim).astype(float))
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Search for memory atoms relevant to the query.
        
        Args:
            query: The search query
            top_k: Number of results to return
            
        Returns:
            List of memory atoms with similarity scores
        """
        if not self.atoms:
            print("No atoms loaded, cannot search")
            return []
        
        # In a real implementation, this would:
        # 1. Convert the query to an embedding
        # 2. Compute cosine similarity with all atom embeddings
        # 3. Return the top-k most similar atoms
        
        # For this demo, we'll simulate the search
        query_embedding = self._compute_query_embedding(query)
        
        # Simulate similarity scores (random for demo)
        results = []
        for atom in self.atoms:
            # In a real implementation, compute actual cosine similarity
            similarity = random.uniform(0.5, 1.0)
            
            # Add to results with similarity score
            atom_copy = atom.copy()
            atom_copy['similarity'] = similarity
            results.append(atom_copy)
        
        # Sort by similarity (descending)
        results.sort(key=lambda x: x['similarity'], reverse=True)
        
        # Return top-k results
        return results[:top_k]
    
    def filter_by_tags(self, tags: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Filter memory atoms by tags.
        
        Args:
            tags: List of tags to filter by
            top_k: Number of results to return
            
        Returns:
            List of memory atoms matching the tags
        """
        if not self.atoms:
            print("No atoms loaded, cannot filter")
            return []
        
        # Filter atoms by tags
        matching_atoms = []
        for atom in self.atoms:
            atom_tags = atom.get('tags', [])
            # Check if any of the requested tags match
            if any(tag in atom_tags for tag in tags):
                # Calculate a relevance score based on tag overlap
                overlap = sum(1 for tag in tags if tag in atom_tags)
                relevance = overlap / len(tags) if tags else 0
                
                # Add to results with relevance score
                atom_copy = atom.copy()
                atom_copy['relevance'] = relevance
                matching_atoms.append(atom_copy)
        
        # Sort by relevance (descending)
        matching_atoms.sort(key=lambda x: x['relevance'], reverse=True)
        
        # Return top-k results
        return matching_atoms[:top_k]
    
    def filter_by_type(self, memory_type: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Filter memory atoms by type.
        
        Args:
            memory_type: Type of memory atoms to filter by (declarative, episodic, procedural, semantic)
            top_k: Number of results to return
            
        Returns:
            List of memory atoms of the specified type
        """
        if not self.atoms:
            print("No atoms loaded, cannot filter")
            return []
        
        # Filter atoms by type
        matching_atoms = [atom for atom in self.atoms if atom.get('type') == memory_type]
        
        # Sort by created_at (most recent first)
        matching_atoms.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        # Return top-k results
        return matching_atoms[:top_k]
        
def main():
    parser = argparse.ArgumentParser(description="Search memory atoms")
    parser.add_argument('--atom-store', required=True, help='Path to memory atom store')
    parser.add_argument('--query', help='Search query')
    parser.add_argument('--tags', help='Comma-separated list of tags to filter by')
    parser.add_argument('--type', help='Memory type to filter by')
    parser.add_argument('--top-k', type=int, default=5, help='Number of results to return')
    
    args = parser.parse_args()
    retriever = MemoryAtomRetriever(args.atom_store)
    
    if args.query:
        results = retriever.search(args.query, args.top_k)
        print(f"\nTop {len(results)} results for query '{args.query}':")
        for i, result in enumerate(results):
            print(f"\n{i+1}. {result.get('id', 'Unknown ID')} (similarity: {result.get('similarity', 0):.4f})")
            print(f"   Type: {result.get('type', 'unknown')}")
            print(f"   Tags: {', '.join(result.get('tags', []))}")
            print(f"   Content: {result.get('content', '')[:100]}...")
    
    elif args.tags:
        tags = [tag.strip() for tag in args.tags.split(',')]
        results = retriever.filter_by_tags(tags, args.top_k)
        print(f"\nTop {len(results)} results for tags '{args.tags}':")
        for i, result in enumerate(results):
            print(f"\n{i+1}. {result.get('id', 'Unknown ID')} (relevance: {result.get('relevance', 0):.4f})")
            print(f"   Type: {result.get('type', 'unknown')}")
            print(f"   Tags: {', '.join(result.get('tags', []))}")
            print(f"   Content: {result.get('content', '')[:100]}...")
    
    elif args.type:
        results = retriever.filter_by_type(args.type, args.top_k)
        print(f"\nTop {len(results)} results for type '{args.type}':")
        for i, result in enumerate(results):
            print(f"\n{i+1}. {result.get('id', 'Unknown ID')}")
            print(f"   Tags: {', '.join(result.get('tags', []))}")
            print(f"   Created: {result.get('created_at', 'unknown')}")
            print(f"   Content: {result.get('content', '')[:100]}...")
    
    else:
        print("Please provide a query, tags, or type to search for")

if __name__ == "__main__":
    main()