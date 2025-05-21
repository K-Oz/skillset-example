#!/usr/bin/env python3
"""
Create checkpoints of the Cognitive Tokamak system state.
Ensures continuity across system restarts.
"""

import os
import sys
import json
import argparse
import shutil
import hashlib
from datetime import datetime
import subprocess
from typing import Dict, List, Any, Optional

class CognitiveCheckpoint:
    def __init__(self, checkpoint_dir: str):
        """
        Initialize a checkpoint manager.
        
        Args:
            checkpoint_dir: Directory to store checkpoints
        """
        self.checkpoint_dir = checkpoint_dir
        os.makedirs(checkpoint_dir, exist_ok=True)
    
    def create_checkpoint(self, name: str, memory_dir: str, model_dir: str, 
                         bolt_dir: str) -> str:
        """
        Create a checkpoint of the current system state.
        
        Args:
            name: Name for the checkpoint
            memory_dir: Directory containing memory atoms
            model_dir: Directory containing model checkpoints
            bolt_dir: Directory containing Bolt experiments
            
        Returns:
            Path to the created checkpoint
        """
        # Generate checkpoint ID with timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        checkpoint_id = f"{name}_{timestamp}"
        checkpoint_path = os.path.join(self.checkpoint_dir, checkpoint_id)
        
        try:
            # Create checkpoint directory
            os.makedirs(checkpoint_path, exist_ok=True)
            
            # Create subdirectories
            os.makedirs(os.path.join(checkpoint_path, "memory"), exist_ok=True)
            os.makedirs(os.path.join(checkpoint_path, "model"), exist_ok=True)
            os.makedirs(os.path.join(checkpoint_path, "bolt"), exist_ok=True)
            
            # Copy memory atoms (only JSON files)
            mem_files_copied = 0
            for root, _, files in os.walk(memory_dir):
                for file in files:
                    if file.endswith('.json'):
                        src = os.path.join(root, file)
                        # Get relative path within memory_dir
                        rel_path = os.path.relpath(root, memory_dir)
                        dst_dir = os.path.join(checkpoint_path, "memory", rel_path)
                        os.makedirs(dst_dir, exist_ok=True)
                        dst = os.path.join(dst_dir, file)
                        shutil.copy2(src, dst)
                        mem_files_copied += 1
            
            # Copy model checkpoint config (but not weights)
            model_files_copied = 0
            for root, _, files in os.walk(model_dir):
                for file in files:
                    if file.endswith('.json'):
                        src = os.path.join(root, file)
                        # Get relative path within model_dir
                        rel_path = os.path.relpath(root, model_dir)
                        dst_dir = os.path.join(checkpoint_path, "model", rel_path)
                        os.makedirs(dst_dir, exist_ok=True)
                        dst = os.path.join(dst_dir, file)
                        shutil.copy2(src, dst)
                        model_files_copied += 1
            
            # Copy Bolt experiments
            bolt_files_copied = 0
            for root, _, files in os.walk(bolt_dir):
                for file in files:
                    if file.endswith(('.toml', '.yaml', '.json')):
                        src = os.path.join(root, file)
                        # Get relative path within bolt_dir
                        rel_path = os.path.relpath(root, bolt_dir)
                        dst_dir = os.path.join(checkpoint_path, "bolt", rel_path)
                        os.makedirs(dst_dir, exist_ok=True)
                        dst = os.path.join(dst_dir, file)
                        shutil.copy2(src, dst)
                        bolt_files_copied += 1
            
            # Create checkpoint metadata
            metadata = {
                "checkpoint_id": checkpoint_id,
                "name": name,
                "created_at": datetime.now().isoformat(),
                "stats": {
                    "memory_files": mem_files_copied,
                    "model_files": model_files_copied,
                    "bolt_files": bolt_files_copied
                },
                "directories": {
                    "memory": memory_dir,
                    "model": model_dir,
                    "bolt": bolt_dir
                }
            }
            
            # Write metadata
            with open(os.path.join(checkpoint_path, "metadata.json"), 'w') as f:
                json.dump(metadata, f, indent=2)
            
            print(f"Checkpoint created: {checkpoint_id}")
            print(f"Path: {checkpoint_path}")
            print(f"Files copied: memory={mem_files_copied}, model={model_files_copied}, bolt={bolt_files_copied}")
            
            # Create symlink to latest checkpoint with this name
            latest_link = os.path.join(self.checkpoint_dir, f"{name}_latest")
            if os.path.exists(latest_link) or os.path.islink(latest_link):
                os.remove(latest_link)
            os.symlink(checkpoint_path, latest_link)
            print(f"Latest link updated: {latest_link}")
            
            return checkpoint_path
        
        except Exception as e:
            print(f"Error creating checkpoint: {e}")
            # Cleanup in case of error
            if os.path.exists(checkpoint_path):
                shutil.rmtree(checkpoint_path)
            raise
    
    def list_checkpoints(self) -> List[Dict[str, Any]]:
        """
        List all available checkpoints.
        
        Returns:
            List of checkpoint metadata
        """
        checkpoints = []
        
        for item in os.listdir(self.checkpoint_dir):
            item_path = os.path.join(self.checkpoint_dir, item)
            
            # Skip symlinks and non-directories
            if not os.path.isdir(item_path) or os.path.islink(item_path):
                continue
            
            # Check for metadata file
            metadata_path = os.path.join(item_path, "metadata.json")
            if os.path.exists(metadata_path):
                try:
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    checkpoints.append(metadata)
                except Exception as e:
                    print(f"Error reading metadata for {item}: {e}")
        
        # Sort by creation time (newest first)
        checkpoints.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return checkpoints

def main():
    parser = argparse.ArgumentParser(description="Create system checkpoints")
    parser.add_argument('--name', default="checkpoint", help='Name for the checkpoint')
    parser.add_argument('--checkpoint-dir', default="checkpoints", help='Directory to store checkpoints')
    parser.add_argument('--memory-dir', default="memory/atoms", help='Directory containing memory atoms')
    parser.add_argument('--model-dir', default="models/checkpoints", help='Directory containing model checkpoints')
    parser.add_argument('--bolt-dir', default="bolt/experiments", help='Directory containing Bolt experiments')
    parser.add_argument('--list', action='store_true', help='List available checkpoints')
    
    args = parser.parse_args()
    
    checkpoint_manager = CognitiveCheckpoint(args.checkpoint_dir)
    
    if args.list:
        checkpoints = checkpoint_manager.list_checkpoints()
        print(f"\nAvailable checkpoints ({len(checkpoints)}):")
        
        for i, checkpoint in enumerate(checkpoints):
            print(f"\n{i+1}. {checkpoint.get('checkpoint_id', 'Unknown')}")
            print(f"   Name: {checkpoint.get('name', 'Unknown')}")
            print(f"   Created: {checkpoint.get('created_at', 'Unknown')}")
            stats = checkpoint.get('stats', {})
            print(f"   Files: memory={stats.get('memory_files', 0)}, model={stats.get('model_files', 0)}, bolt={stats.get('bolt_files', 0)}")
    else:
        try:
            # Ensure directories exist
            for dir_path in [args.memory_dir, args.model_dir, args.bolt_dir]:
                if not os.path.exists(dir_path):
                    print(f"Warning: Directory does not exist: {dir_path}")
                    os.makedirs(dir_path, exist_ok=True)
            
            # Create checkpoint
            checkpoint_manager.create_checkpoint(
                args.name, args.memory_dir, args.model_dir, args.bolt_dir
            )
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()