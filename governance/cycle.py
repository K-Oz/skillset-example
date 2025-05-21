#!/usr/bin/env python3
"""
Toroidal Grammar Cycle Manager
Manages the alternation between LightFace exploration and DarkFace synthesis.
"""

import os
import sys
import json
import yaml
import argparse
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import random

from lightface import LightFaceExploration
from darkface import DarkFaceSynthesis

class ToroidalCycle:
    def __init__(self, config_path: str, output_dir: str = "governance/cycles"):
        """
        Initialize the toroidal cycle manager.
        
        Args:
            config_path: Path to the configuration file
            output_dir: Directory to store cycle results
        """
        self.config_path = config_path
        self.output_dir = output_dir
        
        # Load the configuration
        self.config = self._load_config()
        
        # Initialize the explorers and synthesizers
        self.explorer = LightFaceExploration("governance/explorations")
        self.synthesizer = DarkFaceSynthesis("governance/syntheses")
        
        # Create the output directory
        os.makedirs(output_dir, exist_ok=True)
    
    def _load_config(self) -> Dict[str, Any]:
        """Load the configuration from a YAML file."""
        if not os.path.exists(self.config_path):
            raise ValueError(f"Configuration file not found: {self.config_path}")
        
        with open(self.config_path, 'r') as f:
            config = yaml.safe_load(f)
        
        return config
    
    def start_cycle(self, cycle_name: Optional[str] = None) -> Dict[str, Any]:
        """
        Start a new toroidal cycle.
        
        Args:
            cycle_name: Optional name for the cycle
            
        Returns:
            Cycle metadata
        """
        # Generate a cycle ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        cycle_id = f"cycle_{timestamp}"
        
        # Get cycle name
        if cycle_name is None:
            cycle_name = self.config.get("default_cycle_name", "Toroidal Cycle")
        
        # Initialize the cycle
        cycle = {
            "id": cycle_id,
            "name": cycle_name,
            "config_name": os.path.basename(self.config_path),
            "start_time": datetime.now().isoformat(),
            "status": "active",
            "phases": [],
            "current_phase": "init",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Save the cycle metadata
        cycle_file = os.path.join(self.output_dir, f"{cycle_id}.json")
        with open(cycle_file, 'w') as f:
            json.dump(cycle, f, indent=2)
        
        print(f"Toroidal cycle started: {cycle_id}")
        print(f"Name: {cycle_name}")
        print(f"Configuration: {os.path.basename(self.config_path)}")
        
        return cycle
    
    def execute_lightface_phase(self, cycle_id: str) -> Dict[str, Any]:
        """
        Execute a LightFace exploration phase.
        
        Args:
            cycle_id: The cycle ID
            
        Returns:
            The updated cycle with the exploration phase
        """
        # Load the cycle
        cycle_file = os.path.join(self.output_dir, f"{cycle_id}.json")
        if not os.path.exists(cycle_file):
            raise ValueError(f"Cycle not found: {cycle_id}")
        
        with open(cycle_file, 'r') as f:
            cycle = json.load(f)
        
        # Check if the cycle is active
        if cycle["status"] != "active":
            raise ValueError(f"Cycle is not active: {cycle_id}")
        
        # Get exploration configuration
        exploration_config = self.config.get("lightface", {})
        topic = exploration_config.get("topic", "cognitive architecture")
        duration = exploration_config.get("duration", 2)
        
        # Start the exploration
        exploration = self.explorer.start_exploration(topic, duration)
        
        # Add the phase to the cycle
        phase = {
            "type": "lightface",
            "exploration_id": exploration["id"],
            "topic": topic,
            "start_time": datetime.now().isoformat(),
            "status": "active",
            "end_time": (datetime.now() + timedelta(days=duration)).isoformat()
        }
        
        cycle["phases"].append(phase)
        cycle["current_phase"] = "lightface"
        cycle["updated_at"] = datetime.now().isoformat()
        
        # Save the updated cycle
        with open(cycle_file, 'w') as f:
            json.dump(cycle, f, indent=2)
        
        print(f"Started LightFace phase for cycle: {cycle_id}")
        print(f"Exploration ID: {exploration['id']}")
        print(f"Topic: {topic}")
        print(f"Duration: {duration} days")
        
        return cycle
    
    def execute_darkface_phase(self, cycle_id: str, exploration_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Execute a DarkFace synthesis phase.
        
        Args:
            cycle_id: The cycle ID
            exploration_id: Optional exploration ID to synthesize
            
        Returns:
            The updated cycle with the synthesis phase
        """
        # Load the cycle
        cycle_file = os.path.join(self.output_dir, f"{cycle_id}.json")
        if not os.path.exists(cycle_file):
            raise ValueError(f"Cycle not found: {cycle_id}")
        
        with open(cycle_file, 'r') as f:
            cycle = json.load(f)
        
        # Check if the cycle is active
        if cycle["status"] != "active":
            raise ValueError(f"Cycle is not active: {cycle_id}")
        
        # Find the exploration to synthesize
        if exploration_id is None:
            # Get the most recent LightFace phase
            lightface_phases = [p for p in cycle["phases"] if p["type"] == "lightface"]
            if not lightface_phases:
                raise ValueError(f"No LightFace phase found in cycle: {cycle_id}")
            
            exploration_id = lightface_phases[-1]["exploration_id"]
        
        # Get synthesis configuration
        synthesis_config = self.config.get("darkface", {})
        title = synthesis_config.get("title", f"Synthesis of {cycle['name']}")
        
        # Start the synthesis
        synthesis = self.synthesizer.start_synthesis(exploration_id, title)
        
        # Add the phase to the cycle
        phase = {
            "type": "darkface",
            "synthesis_id": synthesis["id"],
            "exploration_id": exploration_id,
            "title": title,
            "start_time": datetime.now().isoformat(),
            "status": "active"
        }
        
        cycle["phases"].append(phase)
        cycle["current_phase"] = "darkface"
        cycle["updated_at"] = datetime.now().isoformat()
        
        # Save the updated cycle
        with open(cycle_file, 'w') as f:
            json.dump(cycle, f, indent=2)
        
        print(f"Started DarkFace phase for cycle: {cycle_id}")
        print(f"Synthesis ID: {synthesis['id']}")
        print(f"Based on exploration: {exploration_id}")
        
        return cycle
    
    def complete_phase(self, cycle_id: str) -> Dict[str, Any]:
        """
        Complete the current phase of a cycle.
        
        Args:
            cycle_id: The cycle ID
            
        Returns:
            The updated cycle
        """
        # Load the cycle
        cycle_file = os.path.join(self.output_dir, f"{cycle_id}.json")
        if not os.path.exists(cycle_file):
            raise ValueError(f"Cycle not found: {cycle_id}")
        
        with open(cycle_file, 'r') as f:
            cycle = json.load(f)
        
        # Check if the cycle is active
        if cycle["status"] != "active":
            raise ValueError(f"Cycle is not active: {cycle_id}")
        
        # Get the current phase
        if not cycle["phases"]:
            raise ValueError(f"No active phase in cycle: {cycle_id}")
        
        current_phase = cycle["phases"][-1]
        
        if current_phase["status"] != "active":
            raise ValueError(f"Current phase is not active: {current_phase['type']}")
        
        # Complete the phase based on its type
        if current_phase["type"] == "lightface":
            # Complete the exploration
            exploration_id = current_phase["exploration_id"]
            self.explorer.end_exploration(exploration_id)
            
            current_phase["status"] = "completed"
            current_phase["completion_time"] = datetime.now().isoformat()
            
            # Add some simulated results
            current_phase["results"] = {
                "nodes_created": random.randint(10, 30),
                "branches_created": random.randint(5, 20),
                "unique_tags": random.randint(8, 15)
            }
        
        elif current_phase["type"] == "darkface":
            # Complete the synthesis
            synthesis_id = current_phase["synthesis_id"]
            
            # First, cluster the nodes
            self.synthesizer.cluster_nodes(synthesis_id, "tag_similarity", 3)
            
            # Add some synthesis nodes (simplified for demo)
            for i in range(3):
                title = f"Synthesis theme {i+1}"
                content = f"This synthesis theme explores various aspects of the exploration..."
                self.synthesizer.add_synthesis_node(synthesis_id, title, content)
            
            # Finalize the synthesis
            summary = "The synthesis identified several key themes and integrated them into a cohesive framework."
            quality_score = random.uniform(0.7, 0.95)
            self.synthesizer.finalize_synthesis(synthesis_id, summary, quality_score)
            
            current_phase["status"] = "completed"
            current_phase["completion_time"] = datetime.now().isoformat()
            
            # Add some simulated results
            current_phase["results"] = {
                "clusters_created": 3,
                "nodes_created": 4,  # 3 themes + 1 overall
                "quality_score": quality_score
            }
        
        # Update the cycle
        cycle["current_phase"] = "complete"
        cycle["updated_at"] = datetime.now().isoformat()
        
        # Save the updated cycle
        with open(cycle_file, 'w') as f:
            json.dump(cycle, f, indent=2)
        
        print(f"Completed {current_phase['type']} phase for cycle: {cycle_id}")
        
        return cycle
    
    def complete_cycle(self, cycle_id: str, summary: Optional[str] = None) -> Dict[str, Any]:
        """
        Complete a toroidal cycle.
        
        Args:
            cycle_id: The cycle ID
            summary: Optional summary of the cycle
            
        Returns:
            The updated cycle
        """
        # Load the cycle
        cycle_file = os.path.join(self.output_dir, f"{cycle_id}.json")
        if not os.path.exists(cycle_file):
            raise ValueError(f"Cycle not found: {cycle_id}")
        
        with open(cycle_file, 'r') as f:
            cycle = json.load(f)
        
        # Check if the cycle is active
        if cycle["status"] != "active":
            raise ValueError(f"Cycle is not active: {cycle_id}")
        
        # Complete any active phase
        if cycle["current_phase"] not in ["init", "complete"]:
            self.complete_phase(cycle_id)
            
            # Reload the cycle after completing the phase
            with open(cycle_file, 'r') as f:
                cycle = json.load(f)
        
        # Generate a summary if not provided
        if summary is None:
            summary = self._generate_cycle_summary(cycle)
        
        # Update the cycle
        cycle["status"] = "completed"
        cycle["summary"] = summary
        cycle["completion_time"] = datetime.now().isoformat()
        cycle["updated_at"] = datetime.now().isoformat()
        
        # Save the updated cycle
        with open(cycle_file, 'w') as f:
            json.dump(cycle, f, indent=2)
        
        print(f"Completed cycle: {cycle_id}")
        print(f"Phases completed: {len(cycle['phases'])}")
        
        return cycle
    
    def list_cycles(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List toroidal cycles.
        
        Args:
            status: Optional status filter
            
        Returns:
            List of cycles
        """
        cycles = []
        
        for file in os.listdir(self.output_dir):
            if file.startswith("cycle_") and file.endswith(".json"):
                file_path = os.path.join(self.output_dir, file)
                
                try:
                    with open(file_path, 'r') as f:
                        cycle = json.load(f)
                    
                    # Apply status filter if provided
                    if status is None or cycle.get("status") == status:
                        cycles.append(cycle)
                
                except Exception as e:
                    print(f"Error reading cycle file {file}: {e}")
        
        # Sort by start time (newest first)
        cycles.sort(key=lambda x: x.get("start_time", ""), reverse=True)
        
        return cycles
    
    def simulate_cycle(self, name: Optional[str] = None) -> Dict[str, Any]:
        """
        Simulate a complete toroidal cycle for demo purposes.
        
        Args:
            name: Optional name for the cycle
            
        Returns:
            The completed cycle
        """
        # Start the cycle
        if name is None:
            name = f"Simulated Cycle {datetime.now().strftime('%Y-%m-%d')}"
        
        cycle = self.start_cycle(name)
        cycle_id = cycle["id"]
        
        # Execute LightFace phase
        cycle = self.execute_lightface_phase(cycle_id)
        
        # Simulate exploration activity
        exploration_id = cycle["phases"][-1]["exploration_id"]
        self.explorer.simulate_exploration("cognitive architecture", 2, 15)
        
        # Complete LightFace phase
        cycle = self.complete_phase(cycle_id)
        
        # Execute DarkFace phase
        cycle = self.execute_darkface_phase(cycle_id, exploration_id)
        
        # Complete DarkFace phase
        cycle = self.complete_phase(cycle_id)
        
        # Complete the cycle
        cycle = self.complete_cycle(cycle_id)
        
        return cycle
    
    def _generate_cycle_summary(self, cycle: Dict[str, Any]) -> str:
        """Generate a summary for a completed cycle."""
        lightface_phases = [p for p in cycle["phases"] if p["type"] == "lightface"]
        darkface_phases = [p for p in cycle["phases"] if p["type"] == "darkface"]
        
        template = """# Toroidal Cycle: {name}

## Overview
This cycle explored {topics} through a structured process of exploration (LightFace) and synthesis (DarkFace). The cycle ran from {start_date} to {end_date}.

## Exploration Phase
The LightFace exploration phase generated {exploration_nodes} nodes across {exploration_branches} branches, exploring various aspects of {main_topic}. Key themes that emerged included:
- Theoretical frameworks for understanding the domain
- Practical applications and implementation strategies
- Integration patterns with existing systems
- Emergent properties and unexpected connections

## Synthesis Phase
The DarkFace synthesis phase distilled the exploration into {synthesis_clusters} main clusters, generating {synthesis_nodes} synthesis nodes. The synthesis achieved a quality score of {quality_score:.2f}, indicating a {quality_text} level of coherence and insight.

## Outcomes
This cycle produced several valuable outcomes:
1. A coherent framework for understanding {main_topic}
2. New connections between previously separate concepts
3. Identification of promising research directions
4. Practical guidelines for implementation

## Next Steps
Based on the results of this cycle, recommended next steps include:
- Deeper exploration of the most promising themes
- Practical testing of the synthesized framework
- Integration with existing knowledge bases
- Initiation of a new cycle focusing on emergent questions
"""
        
        # Extract data for the summary
        topics = []
        for phase in lightface_phases:
            if "topic" in phase:
                topics.append(phase["topic"])
        
        topics_text = ", ".join(topics) if topics else "various domains"
        
        main_topic = topics[0] if topics else "the domain"
        
        start_date = cycle.get("start_time", "").split("T")[0]
        end_date = cycle.get("completion_time", "").split("T")[0]
        
        # Get exploration stats
        total_exploration_nodes = 0
        total_exploration_branches = 0
        
        for phase in lightface_phases:
            if "results" in phase:
                results = phase["results"]
                total_exploration_nodes += results.get("nodes_created", 0)
                total_exploration_branches += results.get("branches_created", 0)
        
        # Get synthesis stats
        total_synthesis_clusters = 0
        total_synthesis_nodes = 0
        avg_quality_score = 0.0
        
        for phase in darkface_phases:
            if "results" in phase:
                results = phase["results"]
                total_synthesis_clusters += results.get("clusters_created", 0)
                total_synthesis_nodes += results.get("nodes_created", 0)
                avg_quality_score += results.get("quality_score", 0.0)
        
        if darkface_phases:
            avg_quality_score /= len(darkface_phases)
        
        # Quality text based on score
        if avg_quality_score >= 0.9:
            quality_text = "excellent"
        elif avg_quality_score >= 0.8:
            quality_text = "very high"
        elif avg_quality_score >= 0.7:
            quality_text = "high"
        elif avg_quality_score >= 0.6:
            quality_text = "good"
        else:
            quality_text = "moderate"
        
        # Fill in the template
        summary = template.format(
            name=cycle.get("name", "Unnamed"),
            topics=topics_text,
            start_date=start_date,
            end_date=end_date,
            main_topic=main_topic,
            exploration_nodes=total_exploration_nodes,
            exploration_branches=total_exploration_branches,
            synthesis_clusters=total_synthesis_clusters,
            synthesis_nodes=total_synthesis_nodes,
            quality_score=avg_quality_score,
            quality_text=quality_text
        )
        
        return summary

def main():
    parser = argparse.ArgumentParser(description="Toroidal Grammar Cycle Manager")
    parser.add_argument('--config', default="governance/policies/default.yaml", help='Path to configuration file')
    parser.add_argument('--output-dir', default="governance/cycles", help='Directory to store cycle results')
    parser.add_argument('--start', action='store_true', help='Start a new cycle')
    parser.add_argument('--name', help='Name for the cycle')
    parser.add_argument('--lightface', help='Execute LightFace phase for cycle ID')
    parser.add_argument('--darkface', help='Execute DarkFace phase for cycle ID')
    parser.add_argument('--complete-phase', help='Complete the current phase for cycle ID')
    parser.add_argument('--complete-cycle', help='Complete the cycle for cycle ID')
    parser.add_argument('--list', action='store_true', help='List cycles')
    parser.add_argument('--status', choices=['active', 'completed'], help='Filter cycles by status')
    parser.add_argument('--simulate', action='store_true', help='Simulate a complete cycle')
    
    args = parser.parse_args()
    
    # Ensure the policy directory exists
    policy_dir = os.path.dirname(args.config)
    os.makedirs(policy_dir, exist_ok=True)
    
    # Create a default config if it doesn't exist
    if not os.path.exists(args.config):
        default_config = {
            "name": "Default Toroidal Grammar Policy",
            "description": "Default policy for balancing exploration and synthesis",
            "version": "1.0.0",
            "default_cycle_name": "Toroidal Cycle",
            "lightface": {
                "topic": "cognitive architecture",
                "duration": 2,
                "constraints": []
            },
            "darkface": {
                "title": "Synthesis Session",
                "criteria": []
            },
            "cycle": {
                "auto_advance": False,
                "phases": ["lightface", "darkface"]
            }
        }
        
        with open(args.config, 'w') as f:
            yaml.dump(default_config, f, default_flow_style=False)
        
        print(f"Created default configuration: {args.config}")
    
    cycle_manager = ToroidalCycle(args.config, args.output_dir)
    
    if args.list:
        cycles = cycle_manager.list_cycles(args.status)
        print(f"\nToroidal Cycles ({len(cycles)}):")
        
        for i, cycle in enumerate(cycles):
            print(f"\n{i+1}. {cycle['id']}")
            print(f"   Name: {cycle['name']}")
            print(f"   Status: {cycle['status'].upper()}")
            print(f"   Started: {cycle['start_time'].split('T')[0]}")
            print(f"   Phases: {len(cycle['phases'])}")
            print(f"   Current: {cycle['current_phase']}")
    
    elif args.simulate:
        cycle = cycle_manager.simulate_cycle(args.name)
        print(f"\nSimulated cycle: {cycle['id']}")
        print(f"Completed {len(cycle['phases'])} phases")
        print(f"Summary length: {len(cycle.get('summary', ''))}")
    
    elif args.start:
        cycle_manager.start_cycle(args.name)
    
    elif args.lightface:
        cycle_manager.execute_lightface_phase(args.lightface)
    
    elif args.darkface:
        cycle_manager.execute_darkface_phase(args.darkface)
    
    elif args.complete_phase:
        cycle_manager.complete_phase(args.complete_phase)
    
    elif args.complete_cycle:
        cycle_manager.complete_cycle(args.complete_cycle)
    
    else:
        print("Error: No action specified")

if __name__ == "__main__":
    main()