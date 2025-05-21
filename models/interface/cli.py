#!/usr/bin/env python3
"""
Command-line interface for the Marduk LLM system.
Provides interactive access to the language model.
"""

import os
import sys
import argparse
from typing import Dict, Any, Optional
import json

# Import the RAG components
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from rag.generator import RAGGenerator

class MardukCLI:
    def __init__(self, model_path: str, atom_store_path: str):
        """
        Initialize the Marduk CLI.
        
        Args:
            model_path: Path to the fine-tuned model
            atom_store_path: Path to the memory atom store
        """
        self.model_path = model_path
        self.atom_store_path = atom_store_path
        
        # Initialize the generator
        try:
            self.generator = RAGGenerator(model_path, atom_store_path)
            print(f"Initialized Marduk LLM from {model_path}")
            print(f"Using memory atoms from {atom_store_path}")
        except Exception as e:
            print(f"Error initializing generator: {e}")
            sys.exit(1)
    
    def generate_response(self, query: str, top_k: int = 3, max_tokens: int = 500) -> str:
        """Generate a response to a query."""
        return self.generator.generate(query, top_k, max_tokens)
    
    def run_interactive(self):
        """Run the CLI in interactive mode."""
        print("\n" + "=" * 50)
        print("  Marduk Cognitive Tokamak - Interactive CLI")
        print("=" * 50)
        print("Type 'exit' or 'quit' to end the session.")
        print("Type 'help' for commands.")
        print()
        
        history = []
        
        while True:
            try:
                query = input("\nYou: ")
                
                if query.lower() in ['exit', 'quit']:
                    print("Exiting Marduk CLI.")
                    break
                
                elif query.lower() == 'help':
                    print("\nCommands:")
                    print("  help       - Show this help message")
                    print("  exit, quit - Exit the CLI")
                    print("  history    - Show conversation history")
                    print("  save       - Save conversation history to file")
                    continue
                
                elif query.lower() == 'history':
                    if not history:
                        print("No conversation history yet.")
                    else:
                        print("\nConversation History:")
                        for i, (q, r) in enumerate(history):
                            print(f"\n--- Exchange {i+1} ---")
                            print(f"You: {q}")
                            print(f"Marduk: {r[:100]}...")
                    continue
                
                elif query.lower().startswith('save'):
                    parts = query.split(' ', 1)
                    filename = parts[1] if len(parts) > 1 else "marduk_conversation.json"
                    self._save_history(history, filename)
                    continue
                
                # Generate response
                response = self.generate_response(query)
                print("\nMarduk: " + response)
                
                # Add to history
                history.append((query, response))
            
            except KeyboardInterrupt:
                print("\nExiting Marduk CLI.")
                break
            
            except Exception as e:
                print(f"Error: {e}")
    
    def _save_history(self, history, filename: str):
        """Save conversation history to file."""
        try:
            with open(filename, 'w') as f:
                json.dump({
                    "conversation": [
                        {"role": "user", "content": q} if i % 2 == 0 else {"role": "assistant", "content": r}
                        for i, (q, r) in enumerate(history)
                        for content in [q, r]
                    ]
                }, f, indent=2)
            print(f"Conversation history saved to {filename}")
        except Exception as e:
            print(f"Error saving history: {e}")

def main():
    parser = argparse.ArgumentParser(description="Marduk LLM command-line interface")
    parser.add_argument('--model', default='models/checkpoints/subspace-marduk-latest',
                        help='Path to fine-tuned model')
    parser.add_argument('--atom-store', default='memory/atoms',
                        help='Path to memory atom store')
    parser.add_argument('--query', help='Query to generate response for (if not interactive)')
    
    args = parser.parse_args()
    
    # Ensure directories exist
    os.makedirs(os.path.dirname(args.model), exist_ok=True)
    os.makedirs(args.atom_store, exist_ok=True)
    
    cli = MardukCLI(args.model, args.atom_store)
    
    if args.query:
        # Generate a single response
        response = cli.generate_response(args.query)
        print(f"Query: {args.query}")
        print("\nResponse:")
        print("-" * 50)
        print(response)
    else:
        # Run in interactive mode
        cli.run_interactive()

if __name__ == "__main__":
    main()