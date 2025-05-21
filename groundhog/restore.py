#!/usr/bin/env python3
"""
Restore the system from checkpoints or backups.
Ensures continuity after a system restart.
"""

import os
import sys
import json
import argparse
import shutil
import tarfile
import tempfile
from datetime import datetime
from typing import Dict, List, Any, Optional

class RestoreManager:
    def __init__(self):
        """Initialize the restore manager."""
        pass
    
    def restore_from_checkpoint(self, checkpoint_path: str, 
                               memory_dir: str, model_dir: str, bolt_dir: str,
                               force: bool = False) -> bool:
        """
        Restore the system from a checkpoint.
        
        Args:
            checkpoint_path: Path to the checkpoint
            memory_dir: Target directory for memory atoms
            model_dir: Target directory for model checkpoints
            bolt_dir: Target directory for Bolt experiments
            force: Whether to overwrite existing files
            
        Returns:
            True if successful
        """
        if not os.path.exists(checkpoint_path):
            raise ValueError(f"Checkpoint not found: {checkpoint_path}")
        
        # Check if this is a valid checkpoint
        metadata_path = os.path.join(checkpoint_path, "metadata.json")
        if not os.path.exists(metadata_path):
            raise ValueError(f"Invalid checkpoint: metadata.json not found")
        
        # Load metadata
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        print(f"Restoring from checkpoint: {metadata.get('checkpoint_id', 'Unknown')}")
        print(f"Created at: {metadata.get('created_at', 'Unknown')}")
        
        # Check if target directories exist and are non-empty
        for dir_name, dir_path in [("Memory", memory_dir), ("Model", model_dir), ("Bolt", bolt_dir)]:
            if os.path.exists(dir_path) and os.listdir(dir_path) and not force:
                print(f"Warning: {dir_name} directory is not empty: {dir_path}")
                print("Use --force to overwrite")
                return False
        
        # Create target directories if they don't exist
        os.makedirs(memory_dir, exist_ok=True)
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(bolt_dir, exist_ok=True)
        
        try:
            # Restore memory atoms
            checkpoint_memory = os.path.join(checkpoint_path, "memory")
            if os.path.exists(checkpoint_memory):
                if force and os.path.exists(memory_dir):
                    # Remove existing files
                    for item in os.listdir(memory_dir):
                        item_path = os.path.join(memory_dir, item)
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                
                # Copy files
                self._copy_directory_contents(checkpoint_memory, memory_dir)
                print(f"Restored memory atoms to {memory_dir}")
            
            # Restore model checkpoints
            checkpoint_model = os.path.join(checkpoint_path, "model")
            if os.path.exists(checkpoint_model):
                if force and os.path.exists(model_dir):
                    # Remove existing files
                    for item in os.listdir(model_dir):
                        item_path = os.path.join(model_dir, item)
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                
                # Copy files
                self._copy_directory_contents(checkpoint_model, model_dir)
                print(f"Restored model checkpoints to {model_dir}")
            
            # Restore Bolt experiments
            checkpoint_bolt = os.path.join(checkpoint_path, "bolt")
            if os.path.exists(checkpoint_bolt):
                if force and os.path.exists(bolt_dir):
                    # Remove existing files
                    for item in os.listdir(bolt_dir):
                        item_path = os.path.join(bolt_dir, item)
                        if os.path.isfile(item_path):
                            os.remove(item_path)
                        elif os.path.isdir(item_path):
                            shutil.rmtree(item_path)
                
                # Copy files
                self._copy_directory_contents(checkpoint_bolt, bolt_dir)
                print(f"Restored Bolt experiments to {bolt_dir}")
            
            print("Restore from checkpoint completed successfully")
            return True
        
        except Exception as e:
            print(f"Error restoring from checkpoint: {e}")
            raise
    
    def restore_from_backup(self, backup_path: str,
                           memory_dir: str, model_dir: str, bolt_dir: str,
                           force: bool = False) -> bool:
        """
        Restore the system from a backup file.
        
        Args:
            backup_path: Path to the backup file
            memory_dir: Target directory for memory atoms
            model_dir: Target directory for model checkpoints
            bolt_dir: Target directory for Bolt experiments
            force: Whether to overwrite existing files
            
        Returns:
            True if successful
        """
        if not os.path.exists(backup_path):
            raise ValueError(f"Backup file not found: {backup_path}")
        
        # Check if this is a valid backup file
        if not backup_path.endswith('.tar.gz'):
            raise ValueError(f"Invalid backup file: must be a .tar.gz file")
        
        # Check if target directories exist and are non-empty
        for dir_name, dir_path in [("Memory", memory_dir), ("Model", model_dir), ("Bolt", bolt_dir)]:
            if os.path.exists(dir_path) and os.listdir(dir_path) and not force:
                print(f"Warning: {dir_name} directory is not empty: {dir_path}")
                print("Use --force to overwrite")
                return False
        
        # Create target directories if they don't exist
        os.makedirs(memory_dir, exist_ok=True)
        os.makedirs(model_dir, exist_ok=True)
        os.makedirs(bolt_dir, exist_ok=True)
        
        # Extract to a temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                # Extract the backup
                with tarfile.open(backup_path, "r:gz") as tar:
                    tar.extractall(path=temp_dir)
                
                # Check for metadata
                metadata_path = os.path.join(temp_dir, "backup_metadata.json")
                if os.path.exists(metadata_path):
                    with open(metadata_path, 'r') as f:
                        metadata = json.load(f)
                    print(f"Restoring from backup created at: {metadata.get('created_at', 'Unknown')}")
                    print(f"Backup type: {metadata.get('backup_type', 'Unknown')}")
                else:
                    print("Warning: No backup metadata found")
                
                # Check for backup contents
                backup_memory = os.path.join(temp_dir, "memory")
                backup_model = os.path.join(temp_dir, "model")
                backup_bolt = os.path.join(temp_dir, "bolt")
                
                # If this is a checkpoint backup, look in the checkpoint directory
                checkpoint_dir = os.path.join(temp_dir, "checkpoint")
                if os.path.exists(checkpoint_dir):
                    backup_memory = os.path.join(checkpoint_dir, "memory")
                    backup_model = os.path.join(checkpoint_dir, "model")
                    backup_bolt = os.path.join(checkpoint_dir, "bolt")
                
                # Restore memory atoms
                if os.path.exists(backup_memory):
                    if force and os.path.exists(memory_dir):
                        # Remove existing files
                        for item in os.listdir(memory_dir):
                            item_path = os.path.join(memory_dir, item)
                            if os.path.isfile(item_path):
                                os.remove(item_path)
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path)
                    
                    # Copy files
                    self._copy_directory_contents(backup_memory, memory_dir)
                    print(f"Restored memory atoms to {memory_dir}")
                
                # Restore model checkpoints
                if os.path.exists(backup_model):
                    if force and os.path.exists(model_dir):
                        # Remove existing files
                        for item in os.listdir(model_dir):
                            item_path = os.path.join(model_dir, item)
                            if os.path.isfile(item_path):
                                os.remove(item_path)
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path)
                    
                    # Copy files
                    self._copy_directory_contents(backup_model, model_dir)
                    print(f"Restored model checkpoints to {model_dir}")
                
                # Restore Bolt experiments
                if os.path.exists(backup_bolt):
                    if force and os.path.exists(bolt_dir):
                        # Remove existing files
                        for item in os.listdir(bolt_dir):
                            item_path = os.path.join(bolt_dir, item)
                            if os.path.isfile(item_path):
                                os.remove(item_path)
                            elif os.path.isdir(item_path):
                                shutil.rmtree(item_path)
                    
                    # Copy files
                    self._copy_directory_contents(backup_bolt, bolt_dir)
                    print(f"Restored Bolt experiments to {bolt_dir}")
                
                print("Restore from backup completed successfully")
                return True
            
            except Exception as e:
                print(f"Error restoring from backup: {e}")
                raise
    
    def _copy_directory_contents(self, src_dir: str, dest_dir: str) -> None:
        """
        Copy contents of a directory to another directory, preserving structure.
        
        Args:
            src_dir: Source directory
            dest_dir: Destination directory
        """
        for item in os.listdir(src_dir):
            src_path = os.path.join(src_dir, item)
            dest_path = os.path.join(dest_dir, item)
            
            if os.path.isfile(src_path):
                # Copy file
                shutil.copy2(src_path, dest_path)
            elif os.path.isdir(src_path):
                # Create directory if it doesn't exist
                os.makedirs(dest_path, exist_ok=True)
                # Recursively copy contents
                self._copy_directory_contents(src_path, dest_path)

def main():
    parser = argparse.ArgumentParser(description="Restore system from checkpoint or backup")
    parser.add_argument('--checkpoint', help='Path to checkpoint directory')
    parser.add_argument('--backup', help='Path to backup file')
    parser.add_argument('--memory-dir', default="memory/atoms", help='Target directory for memory atoms')
    parser.add_argument('--model-dir', default="models/checkpoints", help='Target directory for model checkpoints')
    parser.add_argument('--bolt-dir', default="bolt/experiments", help='Target directory for Bolt experiments')
    parser.add_argument('--force', action='store_true', help='Force overwrite of existing files')
    
    args = parser.parse_args()
    
    if not args.checkpoint and not args.backup:
        print("Error: Must specify either --checkpoint or --backup")
        return
    
    if args.checkpoint and args.backup:
        print("Error: Cannot specify both --checkpoint and --backup")
        return
    
    restore_manager = RestoreManager()
    
    try:
        if args.checkpoint:
            restore_manager.restore_from_checkpoint(
                args.checkpoint, args.memory_dir, args.model_dir, args.bolt_dir, args.force
            )
        else:
            restore_manager.restore_from_backup(
                args.backup, args.memory_dir, args.model_dir, args.bolt_dir, args.force
            )
    
    except Exception as e:
        print(f"Error during restore: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()