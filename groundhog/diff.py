#!/usr/bin/env python3
"""
Generate cognitive diffs to track changes in the system.
Creates weekly reports to visualize system evolution.
"""

import os
import sys
import json
import argparse
from datetime import datetime, timedelta
import difflib
from typing import Dict, List, Any, Optional, Tuple

class CognitiveDiff:
    def __init__(self, output_dir: str):
        """
        Initialize the cognitive diff generator.
        
        Args:
            output_dir: Directory to store diff reports
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def compare_checkpoints(self, old_checkpoint: str, new_checkpoint: str) -> Dict[str, Any]:
        """
        Compare two checkpoints and generate a diff report.
        
        Args:
            old_checkpoint: Path to older checkpoint
            new_checkpoint: Path to newer checkpoint
            
        Returns:
            Diff report
        """
        if not os.path.exists(old_checkpoint):
            raise ValueError(f"Old checkpoint not found: {old_checkpoint}")
        
        if not os.path.exists(new_checkpoint):
            raise ValueError(f"New checkpoint not found: {new_checkpoint}")
        
        # Get checkpoint metadata
        old_meta_path = os.path.join(old_checkpoint, "metadata.json")
        new_meta_path = os.path.join(new_checkpoint, "metadata.json")
        
        if not os.path.exists(old_meta_path) or not os.path.exists(new_meta_path):
            raise ValueError("Invalid checkpoints: metadata.json not found")
        
        with open(old_meta_path, 'r') as f:
            old_meta = json.load(f)
        
        with open(new_meta_path, 'r') as f:
            new_meta = json.load(f)
        
        # Create diff report
        report = {
            "old_checkpoint": {
                "id": old_meta.get("checkpoint_id", "unknown"),
                "created_at": old_meta.get("created_at", "unknown")
            },
            "new_checkpoint": {
                "id": new_meta.get("checkpoint_id", "unknown"),
                "created_at": new_meta.get("created_at", "unknown")
            },
            "generated_at": datetime.now().isoformat(),
            "diffs": {
                "memory": self._diff_directory(
                    os.path.join(old_checkpoint, "memory"),
                    os.path.join(new_checkpoint, "memory")
                ),
                "model": self._diff_directory(
                    os.path.join(old_checkpoint, "model"),
                    os.path.join(new_checkpoint, "model")
                ),
                "bolt": self._diff_directory(
                    os.path.join(old_checkpoint, "bolt"),
                    os.path.join(new_checkpoint, "bolt")
                )
            },
            "stats": {}
        }
        
        # Compute statistics
        memory_diff = report["diffs"]["memory"]
        model_diff = report["diffs"]["model"]
        bolt_diff = report["diffs"]["bolt"]
        
        stats = {
            "memory": {
                "added": len(memory_diff.get("added", [])),
                "removed": len(memory_diff.get("removed", [])),
                "modified": len(memory_diff.get("modified", [])),
                "unchanged": len(memory_diff.get("unchanged", []))
            },
            "model": {
                "added": len(model_diff.get("added", [])),
                "removed": len(model_diff.get("removed", [])),
                "modified": len(model_diff.get("modified", [])),
                "unchanged": len(model_diff.get("unchanged", []))
            },
            "bolt": {
                "added": len(bolt_diff.get("added", [])),
                "removed": len(bolt_diff.get("removed", [])),
                "modified": len(bolt_diff.get("modified", [])),
                "unchanged": len(bolt_diff.get("unchanged", []))
            }
        }
        
        report["stats"] = stats
        
        return report
    
    def _diff_directory(self, old_dir: str, new_dir: str) -> Dict[str, List[str]]:
        """
        Compare two directories and generate a diff.
        
        Args:
            old_dir: Path to older directory
            new_dir: Path to newer directory
            
        Returns:
            Diff information
        """
        if not os.path.exists(old_dir):
            return {
                "added": self._get_all_files(new_dir),
                "removed": [],
                "modified": [],
                "unchanged": []
            }
        
        if not os.path.exists(new_dir):
            return {
                "added": [],
                "removed": self._get_all_files(old_dir),
                "modified": [],
                "unchanged": []
            }
        
        # Get all files in each directory
        old_files = self._get_all_files(old_dir)
        new_files = self._get_all_files(new_dir)
        
        # Find added and removed files
        old_rel_paths = set(self._get_relative_path(old_dir, f) for f in old_files)
        new_rel_paths = set(self._get_relative_path(new_dir, f) for f in new_files)
        
        added = [os.path.join(new_dir, f) for f in new_rel_paths - old_rel_paths]
        removed = [os.path.join(old_dir, f) for f in old_rel_paths - new_rel_paths]
        
        # Check for modified files
        common_paths = old_rel_paths.intersection(new_rel_paths)
        modified = []
        unchanged = []
        
        for rel_path in common_paths:
            old_file = os.path.join(old_dir, rel_path)
            new_file = os.path.join(new_dir, rel_path)
            
            if os.path.isfile(old_file) and os.path.isfile(new_file):
                if self._files_differ(old_file, new_file):
                    modified.append(new_file)
                else:
                    unchanged.append(new_file)
        
        return {
            "added": added,
            "removed": removed,
            "modified": modified,
            "unchanged": unchanged
        }
    
    def _get_all_files(self, directory: str) -> List[str]:
        """Get all files in a directory recursively."""
        all_files = []
        
        if not os.path.exists(directory):
            return all_files
        
        for root, _, files in os.walk(directory):
            for file in files:
                all_files.append(os.path.join(root, file))
        
        return all_files
    
    def _get_relative_path(self, base_dir: str, file_path: str) -> str:
        """Get path relative to base directory."""
        return os.path.relpath(file_path, base_dir)
    
    def _files_differ(self, file1: str, file2: str) -> bool:
        """Check if two files have different content."""
        try:
            with open(file1, 'rb') as f1, open(file2, 'rb') as f2:
                return f1.read() != f2.read()
        except Exception:
            # If there's an error reading, assume they're different
            return True
    
    def generate_report(self, diff_report: Dict[str, Any], output_file: Optional[str] = None) -> str:
        """
        Generate a human-readable report from a diff report.
        
        Args:
            diff_report: Diff report data
            output_file: Optional output file path
            
        Returns:
            Path to the generated report
        """
        if output_file is None:
            timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
            output_file = os.path.join(self.output_dir, f"cognitive-diff-{timestamp}.md")
        
        old_id = diff_report["old_checkpoint"]["id"]
        new_id = diff_report["new_checkpoint"]["id"]
        old_date = diff_report["old_checkpoint"]["created_at"].split("T")[0]
        new_date = diff_report["new_checkpoint"]["created_at"].split("T")[0]
        
        # Create the report
        with open(output_file, 'w') as f:
            f.write(f"# Cognitive Diff Report\n\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"Comparing checkpoints:\n")
            f.write(f"- From: {old_id} ({old_date})\n")
            f.write(f"- To: {new_id} ({new_date})\n\n")
            
            f.write(f"## Summary\n\n")
            
            # Add summary table
            f.write("| Component | Added | Removed | Modified | Unchanged |\n")
            f.write("|-----------|-------|---------|----------|----------|\n")
            
            stats = diff_report["stats"]
            for component in ["memory", "model", "bolt"]:
                comp_stats = stats[component]
                f.write(f"| {component.capitalize()} | {comp_stats['added']} | {comp_stats['removed']} | {comp_stats['modified']} | {comp_stats['unchanged']} |\n")
            
            # Add component details
            for component in ["memory", "model", "bolt"]:
                f.write(f"\n## {component.capitalize()} Changes\n\n")
                
                comp_diff = diff_report["diffs"][component]
                
                if comp_diff["added"]:
                    f.write(f"### Added ({len(comp_diff['added'])})\n\n")
                    for path in comp_diff["added"][:10]:  # Limit to 10 for readability
                        rel_path = self._get_relative_path(os.path.join(new_id, component), path)
                        f.write(f"- `{rel_path}`\n")
                    if len(comp_diff["added"]) > 10:
                        f.write(f"- ... and {len(comp_diff['added']) - 10} more\n")
                
                if comp_diff["removed"]:
                    f.write(f"\n### Removed ({len(comp_diff['removed'])})\n\n")
                    for path in comp_diff["removed"][:10]:  # Limit to 10 for readability
                        rel_path = self._get_relative_path(os.path.join(old_id, component), path)
                        f.write(f"- `{rel_path}`\n")
                    if len(comp_diff["removed"]) > 10:
                        f.write(f"- ... and {len(comp_diff['removed']) - 10} more\n")
                
                if comp_diff["modified"]:
                    f.write(f"\n### Modified ({len(comp_diff['modified'])})\n\n")
                    for path in comp_diff["modified"][:10]:  # Limit to 10 for readability
                        rel_path = self._get_relative_path(os.path.join(new_id, component), path)
                        f.write(f"- `{rel_path}`\n")
                    if len(comp_diff["modified"]) > 10:
                        f.write(f"- ... and {len(comp_diff['modified']) - 10} more\n")
            
            # Add cognitive analysis section
            f.write(f"\n## Cognitive Analysis\n\n")
            f.write("The following patterns and trends have been identified based on the changes:\n\n")
            
            # Generate a simple analysis based on the stats
            memory_stats = stats["memory"]
            memory_total_changes = memory_stats["added"] + memory_stats["removed"] + memory_stats["modified"]
            
            if memory_total_changes > 0:
                f.write("### Memory Evolution\n\n")
                if memory_stats["added"] > memory_stats["removed"]:
                    f.write("- **Growth Pattern**: The memory system is expanding with new atoms being added.\n")
                elif memory_stats["added"] < memory_stats["removed"]:
                    f.write("- **Pruning Pattern**: The memory system is being refined by removing redundant or outdated atoms.\n")
                if memory_stats["modified"] > 0:
                    f.write("- **Refinement Pattern**: Existing memories are being refined and updated.\n")
            
            bolt_stats = stats["bolt"]
            bolt_total_changes = bolt_stats["added"] + bolt_stats["removed"] + bolt_stats["modified"]
            
            if bolt_total_changes > 0:
                f.write("\n### Process Evolution\n\n")
                if bolt_stats["added"] > 0:
                    f.write("- **Capability Expansion**: New experiments and processes are being defined.\n")
                if bolt_stats["modified"] > 0:
                    f.write("- **Process Optimization**: Existing experiments are being refined and improved.\n")
            
            # Add a note about overall trajectory
            f.write("\n### System Trajectory\n\n")
            total_changes = memory_total_changes + bolt_total_changes + sum(stats["model"].values())
            
            if total_changes > 0:
                f.write("The system is actively evolving with significant changes across multiple components. ")
                
                if memory_stats["added"] > 0 and bolt_stats["added"] > 0:
                    f.write("There is a balanced growth in both memory and processes, suggesting healthy cognitive development.")
                elif memory_stats["added"] > bolt_stats["added"]:
                    f.write("The focus appears to be on knowledge acquisition rather than process refinement.")
                else:
                    f.write("The emphasis is on process improvement rather than expanding the knowledge base.")
            else:
                f.write("The system is in a stable state with minimal changes since the last checkpoint.")
        
        print(f"Report generated: {output_file}")
        return output_file

def main():
    parser = argparse.ArgumentParser(description="Generate cognitive diff reports")
    parser.add_argument('--old-checkpoint', required=True, help='Path to older checkpoint')
    parser.add_argument('--new-checkpoint', required=True, help='Path to newer checkpoint')
    parser.add_argument('--output-dir', default="reports", help='Directory for diff reports')
    parser.add_argument('--output-file', help='Output file path (optional)')
    
    args = parser.parse_args()
    
    diff_generator = CognitiveDiff(args.output_dir)
    
    try:
        diff_report = diff_generator.compare_checkpoints(args.old_checkpoint, args.new_checkpoint)
        diff_generator.generate_report(diff_report, args.output_file)
    
    except Exception as e:
        print(f"Error generating diff report: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()