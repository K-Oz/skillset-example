#!/usr/bin/env python3
"""
Memory System Monitor
Tracks the health and status of the memory atom store.
"""

import os
import sys
import json
import argparse
import time
import datetime
from typing import Dict, List, Any
import matplotlib.pyplot as plt
import numpy as np

class MemoryMonitor:
    def __init__(self, memory_dir: str, output_dir: str = "reports"):
        """Initialize the memory monitor."""
        self.memory_dir = memory_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def scan_memory_store(self) -> Dict[str, Any]:
        """Scan the memory store and collect statistics."""
        stats = {
            "total_atoms": 0,
            "by_type": {},
            "by_tag": {},
            "by_actor": {},
            "avg_links_per_atom": 0,
            "file_sizes": {},
            "timestamps": [],
        }
        
        total_links = 0
        
        # Walk through memory directory
        for root, _, files in os.walk(self.memory_dir):
            for file in files:
                if not file.endswith('.json'):
                    continue
                
                filepath = os.path.join(root, file)
                file_size = os.path.getsize(filepath)
                stats["file_sizes"][filepath] = file_size
                
                try:
                    with open(filepath, 'r') as f:
                        data = json.load(f)
                    
                    # Handle both single atoms and lists of atoms
                    atoms = data if isinstance(data, list) else [data]
                    
                    for atom in atoms:
                        stats["total_atoms"] += 1
                        
                        # Count by type
                        atom_type = atom.get("type", "unknown")
                        stats["by_type"][atom_type] = stats["by_type"].get(atom_type, 0) + 1
                        
                        # Count by tag
                        for tag in atom.get("tags", []):
                            stats["by_tag"][tag] = stats["by_tag"].get(tag, 0) + 1
                        
                        # Count by actor
                        for actor in atom.get("actors", []):
                            stats["by_actor"][actor] = stats["by_actor"].get(actor, 0) + 1
                        
                        # Count links
                        links = atom.get("links", [])
                        total_links += len(links)
                        
                        # Record timestamp
                        if "created_at" in atom:
                            try:
                                timestamp = atom["created_at"]
                                if isinstance(timestamp, str):
                                    # Try to parse ISO format
                                    dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                    stats["timestamps"].append(dt.timestamp())
                            except Exception:
                                pass
                
                except Exception as e:
                    print(f"Error processing {filepath}: {e}")
        
        # Calculate average links per atom
        if stats["total_atoms"] > 0:
            stats["avg_links_per_atom"] = total_links / stats["total_atoms"]
        
        # Add summary data
        stats["summary"] = {
            "total_size_bytes": sum(stats["file_sizes"].values()),
            "total_files": len(stats["file_sizes"]),
            "types_count": len(stats["by_type"]),
            "tags_count": len(stats["by_tag"]),
            "actors_count": len(stats["by_actor"]),
            "oldest_timestamp": min(stats["timestamps"]) if stats["timestamps"] else None,
            "newest_timestamp": max(stats["timestamps"]) if stats["timestamps"] else None,
        }
        
        return stats
    
    def generate_report(self, stats: Dict[str, Any]) -> str:
        """Generate a markdown report from memory statistics."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        report_file = os.path.join(self.output_dir, f"memory_report_{int(time.time())}.md")
        
        with open(report_file, 'w') as f:
            f.write(f"# Memory System Report\n\n")
            f.write(f"Generated: {timestamp}\n\n")
            
            # Summary section
            f.write("## Summary\n\n")
            f.write(f"- **Total Memory Atoms**: {stats['total_atoms']}\n")
            f.write(f"- **Total Storage Size**: {stats['summary']['total_size_bytes'] / 1024:.2f} KB\n")
            f.write(f"- **Memory Types**: {stats['summary']['types_count']}\n")
            f.write(f"- **Unique Tags**: {stats['summary']['tags_count']}\n")
            f.write(f"- **Unique Actors**: {stats['summary']['actors_count']}\n")
            f.write(f"- **Average Links per Atom**: {stats['avg_links_per_atom']:.2f}\n")
            
            if stats["summary"]["oldest_timestamp"]:
                oldest = datetime.datetime.fromtimestamp(stats["summary"]["oldest_timestamp"])
                newest = datetime.datetime.fromtimestamp(stats["summary"]["newest_timestamp"])
                f.write(f"- **Date Range**: {oldest.strftime('%Y-%m-%d')} to {newest.strftime('%Y-%m-%d')}\n")
            
            # Type distribution
            f.write("\n## Memory Type Distribution\n\n")
            f.write("| Type | Count | Percentage |\n")
            f.write("|------|-------|------------|\n")
            
            for mem_type, count in sorted(stats["by_type"].items(), key=lambda x: x[1], reverse=True):
                percentage = (count / stats["total_atoms"]) * 100
                f.write(f"| {mem_type} | {count} | {percentage:.2f}% |\n")
            
            # Top tags
            f.write("\n## Top 20 Tags\n\n")
            f.write("| Tag | Count |\n")
            f.write("|-----|-------|\n")
            
            top_tags = sorted(stats["by_tag"].items(), key=lambda x: x[1], reverse=True)[:20]
            for tag, count in top_tags:
                f.write(f"| {tag} | {count} |\n")
            
            # Top actors
            f.write("\n## Top Actors\n\n")
            f.write("| Actor | Count |\n")
            f.write("|-------|-------|\n")
            
            top_actors = sorted(stats["by_actor"].items(), key=lambda x: x[1], reverse=True)[:10]
            for actor, count in top_actors:
                f.write(f"| {actor} | {count} |\n")
            
            # Time distribution
            if stats["timestamps"]:
                f.write("\n## Growth Over Time\n\n")
                f.write("The memory system has grown over time, with periodic spikes in memory creation.\n")
                f.write("See the accompanying charts for visualizations of memory growth patterns.\n")
        
        print(f"Report generated: {report_file}")
        return report_file
    
    def generate_charts(self, stats: Dict[str, Any]):
        """Generate charts visualizing memory statistics."""
        if not stats["timestamps"]:
            print("No timestamp data available for charts")
            return []
        
        # Time-based growth chart
        timestamps = sorted(stats["timestamps"])
        dates = [datetime.datetime.fromtimestamp(ts) for ts in timestamps]
        
        # Count atoms by week
        weeks = {}
        for date in dates:
            week_key = date.strftime("%Y-%U")
            weeks[week_key] = weeks.get(week_key, 0) + 1
        
        # Sort by week
        sorted_weeks = sorted(weeks.items())
        week_labels = [f"Week {i+1}" for i in range(len(sorted_weeks))]
        week_counts = [count for _, count in sorted_weeks]
        
        # Create time chart
        plt.figure(figsize=(12, 6))
        plt.bar(week_labels, week_counts, color='blue')
        plt.title('Memory Atoms Created per Week')
        plt.xlabel('Week')
        plt.ylabel('Number of Atoms')
        plt.xticks(rotation=45)
        plt.tight_layout()
        
        time_chart_file = os.path.join(self.output_dir, f"memory_growth_{int(time.time())}.png")
        plt.savefig(time_chart_file)
        
        # Create type distribution pie chart
        plt.figure(figsize=(10, 10))
        types = list(stats["by_type"].keys())
        counts = list(stats["by_type"].values())
        
        plt.pie(counts, labels=types, autopct='%1.1f%%', startangle=90)
        plt.axis('equal')
        plt.title('Memory Atom Type Distribution')
        
        type_chart_file = os.path.join(self.output_dir, f"memory_types_{int(time.time())}.png")
        plt.savefig(type_chart_file)
        
        return [time_chart_file, type_chart_file]
    
    def run_analysis(self):
        """Run a full analysis and generate reports."""
        print(f"Analyzing memory store at {self.memory_dir}...")
        
        # Scan the memory store
        stats = self.scan_memory_store()
        print(f"Found {stats['total_atoms']} memory atoms")
        
        # Generate report
        report_file = self.generate_report(stats)
        
        # Generate charts
        chart_files = self.generate_charts(stats)
        
        return {
            "report": report_file,
            "charts": chart_files,
            "stats": stats
        }

def main():
    parser = argparse.ArgumentParser(description="Monitor memory atom store")
    parser.add_argument('--memory-dir', default="memory/atoms", help='Path to memory atom directory')
    parser.add_argument('--output-dir', default="reports", help='Path to output reports')
    
    args = parser.parse_args()
    
    monitor = MemoryMonitor(args.memory_dir, args.output_dir)
    results = monitor.run_analysis()
    
    print(f"Analysis complete. Report saved to {results['report']}")
    for chart in results['charts']:
        print(f"Chart saved to {chart}")

if __name__ == "__main__":
    main()