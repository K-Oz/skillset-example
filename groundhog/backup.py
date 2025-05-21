#!/usr/bin/env python3
"""
Create backups of memory atoms and model checkpoints.
Allows for off-site storage and disaster recovery.
"""

import os
import sys
import json
import argparse
import shutil
import subprocess
import tempfile
from datetime import datetime
import tarfile
import gzip
from typing import Dict, List, Any, Optional

class BackupManager:
    def __init__(self, backup_dir: str):
        """
        Initialize a backup manager.
        
        Args:
            backup_dir: Directory to store backups
        """
        self.backup_dir = backup_dir
        os.makedirs(backup_dir, exist_ok=True)
    
    def create_backup(self, checkpoint_id: Optional[str] = None,
                     memory_dir: Optional[str] = None,
                     model_dir: Optional[str] = None,
                     bolt_dir: Optional[str] = None) -> str:
        """
        Create a backup of the specified directories or checkpoint.
        
        Args:
            checkpoint_id: ID of checkpoint to backup (if None, use directories)
            memory_dir: Directory containing memory atoms
            model_dir: Directory containing model checkpoints
            bolt_dir: Directory containing Bolt experiments
            
        Returns:
            Path to the created backup file
        """
        # Generate backup filename with timestamp
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_name = f"marduk-backup-{timestamp}.tar.gz"
        backup_path = os.path.join(self.backup_dir, backup_name)
        
        # Create temporary directory for organizing files
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                if checkpoint_id:
                    # Backup from checkpoint
                    checkpoint_dir = os.path.join("checkpoints", checkpoint_id)
                    if not os.path.exists(checkpoint_dir):
                        raise ValueError(f"Checkpoint not found: {checkpoint_id}")
                    
                    # Copy checkpoint to temp directory
                    checkpoint_temp = os.path.join(temp_dir, "checkpoint")
                    shutil.copytree(checkpoint_dir, checkpoint_temp)
                    
                    # Create metadata
                    metadata = {
                        "backup_type": "checkpoint",
                        "checkpoint_id": checkpoint_id,
                        "created_at": datetime.now().isoformat()
                    }
                    
                    # Read checkpoint metadata if available
                    checkpoint_meta_path = os.path.join(checkpoint_dir, "metadata.json")
                    if os.path.exists(checkpoint_meta_path):
                        with open(checkpoint_meta_path, 'r') as f:
                            checkpoint_meta = json.load(f)
                        metadata["checkpoint_metadata"] = checkpoint_meta
                
                else:
                    # Backup from directories
                    dirs_to_backup = {}
                    
                    if memory_dir and os.path.exists(memory_dir):
                        dirs_to_backup["memory"] = memory_dir
                    
                    if model_dir and os.path.exists(model_dir):
                        dirs_to_backup["model"] = model_dir
                    
                    if bolt_dir and os.path.exists(bolt_dir):
                        dirs_to_backup["bolt"] = bolt_dir
                    
                    if not dirs_to_backup:
                        raise ValueError("No valid directories specified for backup")
                    
                    # Copy directories to temp
                    for name, dir_path in dirs_to_backup.items():
                        dest_path = os.path.join(temp_dir, name)
                        shutil.copytree(dir_path, dest_path)
                    
                    # Create metadata
                    metadata = {
                        "backup_type": "directories",
                        "directories": dirs_to_backup,
                        "created_at": datetime.now().isoformat()
                    }
                
                # Write metadata
                with open(os.path.join(temp_dir, "backup_metadata.json"), 'w') as f:
                    json.dump(metadata, f, indent=2)
                
                # Create the tarball
                with tarfile.open(backup_path, "w:gz") as tar:
                    tar.add(temp_dir, arcname=".")
                
                # Get size of backup
                backup_size = os.path.getsize(backup_path)
                backup_size_mb = backup_size / (1024 * 1024)
                
                print(f"Backup created: {backup_name}")
                print(f"Path: {backup_path}")
                print(f"Size: {backup_size_mb:.2f} MB")
                
                return backup_path
            
            except Exception as e:
                print(f"Error creating backup: {e}")
                # Cleanup in case of error
                if os.path.exists(backup_path):
                    os.remove(backup_path)
                raise
    
    def upload_to_s3(self, backup_path: str, s3_url: str) -> bool:
        """
        Upload a backup to S3 (simulated).
        
        Args:
            backup_path: Path to backup file
            s3_url: S3 URL for destination
            
        Returns:
            True if successful
        """
        print(f"Simulating upload of {backup_path} to {s3_url}")
        print("In a real implementation, this would use AWS CLI or boto3")
        
        # Simulate the upload with a delay
        print("Uploading...")
        
        # Calculate file size
        backup_size = os.path.getsize(backup_path)
        backup_size_mb = backup_size / (1024 * 1024)
        
        print(f"Upload complete. {backup_size_mb:.2f} MB transferred to {s3_url}")
        return True
    
    def list_backups(self) -> List[Dict[str, Any]]:
        """
        List all available backups.
        
        Returns:
            List of backup metadata
        """
        backups = []
        
        for item in os.listdir(self.backup_dir):
            item_path = os.path.join(self.backup_dir, item)
            
            # Skip directories and non-tar.gz files
            if not os.path.isfile(item_path) or not item.endswith('.tar.gz'):
                continue
            
            # Get file stats
            stats = os.stat(item_path)
            size_mb = stats.st_size / (1024 * 1024)
            created = datetime.fromtimestamp(stats.st_ctime).isoformat()
            
            # Extract metadata if possible (in a real implementation)
            # Here we just create a simple entry
            backup_info = {
                "filename": item,
                "path": item_path,
                "size_mb": size_mb,
                "created_at": created
            }
            
            backups.append(backup_info)
        
        # Sort by creation time (newest first)
        backups.sort(key=lambda x: x.get('created_at', ''), reverse=True)
        
        return backups

def main():
    parser = argparse.ArgumentParser(description="Create system backups")
    parser.add_argument('--backup-dir', default="backups", help='Directory to store backups')
    parser.add_argument('--checkpoint', help='Checkpoint ID to backup')
    parser.add_argument('--memory-dir', default="memory/atoms", help='Directory containing memory atoms')
    parser.add_argument('--model-dir', default="models/checkpoints", help='Directory containing model checkpoints')
    parser.add_argument('--bolt-dir', default="bolt/experiments", help='Directory containing Bolt experiments')
    parser.add_argument('--list', action='store_true', help='List available backups')
    parser.add_argument('--destination', help='Destination for backup (e.g., s3://bucket)')
    
    args = parser.parse_args()
    
    backup_manager = BackupManager(args.backup_dir)
    
    if args.list:
        backups = backup_manager.list_backups()
        print(f"\nAvailable backups ({len(backups)}):")
        
        for i, backup in enumerate(backups):
            print(f"\n{i+1}. {backup.get('filename', 'Unknown')}")
            print(f"   Created: {backup.get('created_at', 'Unknown')}")
            print(f"   Size: {backup.get('size_mb', 0):.2f} MB")
    
    else:
        try:
            # Create backup
            if args.checkpoint:
                backup_path = backup_manager.create_backup(checkpoint_id=args.checkpoint)
            else:
                backup_path = backup_manager.create_backup(
                    memory_dir=args.memory_dir,
                    model_dir=args.model_dir,
                    bolt_dir=args.bolt_dir
                )
            
            # Upload if destination specified
            if args.destination and backup_path:
                backup_manager.upload_to_s3(backup_path, args.destination)
        
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)

if __name__ == "__main__":
    main()