#!/usr/bin/env python3
"""
LightFace Exploration Module
Manages generative, tree-like branching into uncharted domains.
"""

import os
import sys
import json
import argparse
import random
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

class LightFaceExploration:
    def __init__(self, output_dir: str = "governance/explorations"):
        """
        Initialize the LightFace exploration manager.
        
        Args:
            output_dir: Directory to store exploration results
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def start_exploration(self, topic: str, duration: int = 2, 
                        constraints: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Start an exploration sprint.
        
        Args:
            topic: The topic to explore
            duration: Duration of the sprint in days
            constraints: Optional constraints or guidelines
            
        Returns:
            Exploration session metadata
        """
        # Generate a session ID
        session_id = f"explore_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize the exploration session
        session = {
            "id": session_id,
            "topic": topic,
            "start_time": datetime.now().isoformat(),
            "end_time": (datetime.now() + timedelta(days=duration)).isoformat(),
            "duration_days": duration,
            "constraints": constraints or [],
            "status": "active",
            "branches": [],
            "nodes": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Save the session metadata
        session_file = os.path.join(self.output_dir, f"{session_id}.json")
        with open(session_file, 'w') as f:
            json.dump(session, f, indent=2)
        
        print(f"LightFace exploration session started: {session_id}")
        print(f"Topic: {topic}")
        print(f"Duration: {duration} days")
        print(f"End date: {session['end_time'].split('T')[0]}")
        
        return session
    
    def add_exploration_node(self, session_id: str, title: str, content: str, 
                           tags: List[str], parent_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Add a node to the exploration tree.
        
        Args:
            session_id: The exploration session ID
            title: Title of the exploration node
            content: Content of the node
            tags: Tags for the node
            parent_id: Optional parent node ID
            
        Returns:
            The created node
        """
        # Load the session
        session_file = os.path.join(self.output_dir, f"{session_id}.json")
        if not os.path.exists(session_file):
            raise ValueError(f"Exploration session not found: {session_id}")
        
        with open(session_file, 'r') as f:
            session = json.load(f)
        
        # Check if session is still active
        end_time = datetime.fromisoformat(session["end_time"])
        if datetime.now() > end_time and session["status"] == "active":
            session["status"] = "completed"
        
        if session["status"] != "active":
            raise ValueError(f"Exploration session is not active: {session_id}")
        
        # Generate a node ID
        node_id = f"node_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(session['nodes'])}"
        
        # Create the node
        node = {
            "id": node_id,
            "title": title,
            "content": content,
            "tags": tags,
            "created_at": datetime.now().isoformat(),
            "parent_id": parent_id
        }
        
        # Add the node to the session
        session["nodes"].append(node)
        
        # If this is a branch from another node, add it to branches
        if parent_id:
            branch = {
                "from": parent_id,
                "to": node_id,
                "created_at": datetime.now().isoformat()
            }
            session["branches"].append(branch)
        
        # Update the session
        session["updated_at"] = datetime.now().isoformat()
        
        # Save the updated session
        with open(session_file, 'w') as f:
            json.dump(session, f, indent=2)
        
        print(f"Added exploration node: {node_id}")
        print(f"Title: {title}")
        if parent_id:
            print(f"Branched from: {parent_id}")
        
        return node
    
    def end_exploration(self, session_id: str) -> Dict[str, Any]:
        """
        End an exploration session.
        
        Args:
            session_id: The exploration session ID
            
        Returns:
            The updated session
        """
        # Load the session
        session_file = os.path.join(self.output_dir, f"{session_id}.json")
        if not os.path.exists(session_file):
            raise ValueError(f"Exploration session not found: {session_id}")
        
        with open(session_file, 'r') as f:
            session = json.load(f)
        
        # Mark the session as completed
        session["status"] = "completed"
        session["updated_at"] = datetime.now().isoformat()
        
        # Save the updated session
        with open(session_file, 'w') as f:
            json.dump(session, f, indent=2)
        
        print(f"Exploration session ended: {session_id}")
        print(f"Nodes created: {len(session['nodes'])}")
        print(f"Branches created: {len(session['branches'])}")
        
        return session
    
    def list_explorations(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List exploration sessions.
        
        Args:
            status: Optional status filter
            
        Returns:
            List of exploration sessions
        """
        sessions = []
        
        for file in os.listdir(self.output_dir):
            if file.startswith("explore_") and file.endswith(".json"):
                file_path = os.path.join(self.output_dir, file)
                
                try:
                    with open(file_path, 'r') as f:
                        session = json.load(f)
                    
                    # Check if the session is active but should be marked completed
                    if session["status"] == "active":
                        end_time = datetime.fromisoformat(session["end_time"])
                        if datetime.now() > end_time:
                            session["status"] = "completed"
                            session["updated_at"] = datetime.now().isoformat()
                            
                            # Save the updated session
                            with open(file_path, 'w') as f:
                                json.dump(session, f, indent=2)
                    
                    # Apply status filter if provided
                    if status is None or session["status"] == status:
                        sessions.append(session)
                
                except Exception as e:
                    print(f"Error reading session file {file}: {e}")
        
        # Sort by start time (newest first)
        sessions.sort(key=lambda x: x.get("start_time", ""), reverse=True)
        
        return sessions
    
    def simulate_exploration(self, topic: str, duration: int = 2, 
                           node_count: int = 10) -> Dict[str, Any]:
        """
        Simulate an exploration session for demo purposes.
        
        Args:
            topic: The topic to explore
            duration: Duration of the sprint in days
            node_count: Number of nodes to generate
            
        Returns:
            The simulated session
        """
        # Start the exploration
        session = self.start_exploration(topic, duration)
        session_id = session["id"]
        
        # Generate some seed topics related to the main topic
        seed_topics = self._generate_related_topics(topic, 3)
        
        # Create root nodes for each seed topic
        root_nodes = []
        for seed_topic in seed_topics:
            content = self._generate_content_for_topic(seed_topic)
            tags = self._generate_tags_for_topic(seed_topic)
            
            node = self.add_exploration_node(session_id, seed_topic, content, tags)
            root_nodes.append(node)
        
        # Generate branching nodes
        remaining_nodes = node_count - len(root_nodes)
        for _ in range(remaining_nodes):
            # Randomly select a parent node
            parent = random.choice(session["nodes"])
            parent_id = parent["id"]
            
            # Generate a child topic
            child_topic = self._generate_related_topics(parent["title"], 1)[0]
            content = self._generate_content_for_topic(child_topic)
            tags = self._generate_tags_for_topic(child_topic)
            
            self.add_exploration_node(session_id, child_topic, content, tags, parent_id)
        
        # Reload the full session
        with open(os.path.join(self.output_dir, f"{session_id}.json"), 'r') as f:
            session = json.load(f)
        
        return session
    
    def _generate_related_topics(self, topic: str, count: int) -> List[str]:
        """Generate related topics for simulation."""
        base_topics = [
            "neural networks", "symbolic reasoning", "cognitive architecture",
            "memory systems", "attention mechanisms", "recursive processing",
            "hypergraph representations", "language models", "evolutionary algorithms",
            "probabilistic inference", "embodied cognition", "meta-learning"
        ]
        
        # Mix the base topic with new topics
        related = []
        for _ in range(count):
            base = random.choice(base_topics)
            if random.random() < 0.7:
                related.append(f"{topic} and {base}")
            else:
                related.append(f"{base} for {topic}")
        
        return related
    
    def _generate_content_for_topic(self, topic: str) -> str:
        """Generate sample content for a topic."""
        content_templates = [
            "The concept of {topic} represents an interesting area of exploration. It has connections to several key domains and could yield significant insights.",
            "Investigating {topic} could lead to breakthroughs in understanding cognitive processes. The main challenge is integrating different theoretical frameworks.",
            "When considering {topic}, we should examine both the theoretical foundations and practical applications. This dual perspective enriches our understanding.",
            "{topic} presents a fascinating case study in the evolution of ideas. By tracing its development, we can gain insights into broader patterns of knowledge formation.",
            "The intersection of {topic} with existing paradigms creates tension points that drive innovation. These creative conflicts are essential for progress."
        ]
        
        template = random.choice(content_templates)
        return template.format(topic=topic)
    
    def _generate_tags_for_topic(self, topic: str) -> List[str]:
        """Generate tags for a topic."""
        # Extract words from the topic
        words = topic.lower().replace('-', ' ').split()
        
        # Add some general tags
        general_tags = [
            "exploration", "cognitive", "research", "theory", "application",
            "framework", "model", "system", "architecture", "integration"
        ]
        
        # Combine specific and general tags
        tags = words + random.sample(general_tags, min(3, len(general_tags)))
        
        # Deduplicate and limit to 5 tags
        unique_tags = list(set(tags))
        return unique_tags[:5]

def main():
    parser = argparse.ArgumentParser(description="LightFace Exploration Manager")
    parser.add_argument('--output-dir', default="governance/explorations", help='Directory to store exploration results')
    parser.add_argument('--topic', default="cognitive architecture", help='Topic to explore')
    parser.add_argument('--duration', type=int, default=2, help='Duration in days')
    parser.add_argument('--list', action='store_true', help='List exploration sessions')
    parser.add_argument('--status', choices=['active', 'completed'], help='Filter sessions by status')
    parser.add_argument('--simulate', action='store_true', help='Simulate an exploration session')
    parser.add_argument('--node-count', type=int, default=10, help='Number of nodes for simulation')
    
    args = parser.parse_args()
    
    exploration_manager = LightFaceExploration(args.output_dir)
    
    if args.list:
        sessions = exploration_manager.list_explorations(args.status)
        print(f"\nExploration Sessions ({len(sessions)}):")
        
        for i, session in enumerate(sessions):
            status_text = session["status"].upper()
            if status_text == "ACTIVE":
                end_time = datetime.fromisoformat(session["end_time"])
                days_left = (end_time - datetime.now()).days
                if days_left > 0:
                    status_text += f" ({days_left} days left)"
                else:
                    hours_left = (end_time - datetime.now()).total_seconds() / 3600
                    if hours_left > 0:
                        status_text += f" ({int(hours_left)} hours left)"
            
            print(f"\n{i+1}. {session['id']}")
            print(f"   Topic: {session['topic']}")
            print(f"   Status: {status_text}")
            print(f"   Started: {session['start_time'].split('T')[0]}")
            print(f"   Nodes: {len(session['nodes'])}")
    
    elif args.simulate:
        session = exploration_manager.simulate_exploration(args.topic, args.duration, args.node_count)
        print(f"\nSimulated exploration session: {session['id']}")
        print(f"Generated {len(session['nodes'])} exploration nodes")
        print(f"Created {len(session['branches'])} branches")
    
    else:
        # Start a new exploration
        exploration_manager.start_exploration(args.topic, args.duration)

if __name__ == "__main__":
    main()