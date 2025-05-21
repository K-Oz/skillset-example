#!/usr/bin/env python3
"""
DarkFace Synthesis Module
Manages membrane-like constraints that refine and integrate discoveries.
"""

import os
import sys
import json
import argparse
import random
from datetime import datetime
from typing import Dict, List, Any, Optional

class DarkFaceSynthesis:
    def __init__(self, output_dir: str = "governance/syntheses"):
        """
        Initialize the DarkFace synthesis manager.
        
        Args:
            output_dir: Directory to store synthesis results
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def start_synthesis(self, exploration_id: str, title: str,
                       criteria: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Start a synthesis cycle based on an exploration session.
        
        Args:
            exploration_id: ID of the exploration session to synthesize
            title: Title of the synthesis
            criteria: Optional evaluation criteria
            
        Returns:
            Synthesis session metadata
        """
        # Check if the exploration exists
        exploration_file = os.path.join("governance/explorations", f"{exploration_id}.json")
        if not os.path.exists(exploration_file):
            raise ValueError(f"Exploration session not found: {exploration_id}")
        
        # Load the exploration
        with open(exploration_file, 'r') as f:
            exploration = json.load(f)
        
        # Generate a session ID
        session_id = f"synth_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Initialize the synthesis session
        session = {
            "id": session_id,
            "title": title,
            "exploration_id": exploration_id,
            "exploration_topic": exploration.get("topic", "unknown"),
            "start_time": datetime.now().isoformat(),
            "status": "active",
            "criteria": criteria or [],
            "nodes": [],
            "clusters": [],
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # Save the session metadata
        session_file = os.path.join(self.output_dir, f"{session_id}.json")
        with open(session_file, 'w') as f:
            json.dump(session, f, indent=2)
        
        print(f"DarkFace synthesis session started: {session_id}")
        print(f"Title: {title}")
        print(f"Based on exploration: {exploration_id} ({exploration.get('topic', 'unknown')})")
        
        return session
    
    def cluster_nodes(self, session_id: str, method: str = "tag_similarity", 
                     num_clusters: int = 3) -> Dict[str, Any]:
        """
        Cluster exploration nodes for synthesis.
        
        Args:
            session_id: The synthesis session ID
            method: Clustering method
            num_clusters: Number of clusters to create
            
        Returns:
            The updated session with clusters
        """
        # Load the synthesis session
        session_file = os.path.join(self.output_dir, f"{session_id}.json")
        if not os.path.exists(session_file):
            raise ValueError(f"Synthesis session not found: {session_id}")
        
        with open(session_file, 'r') as f:
            session = json.load(f)
        
        # Load the exploration session
        exploration_file = os.path.join("governance/explorations", f"{session['exploration_id']}.json")
        if not os.path.exists(exploration_file):
            raise ValueError(f"Exploration session not found: {session['exploration_id']}")
        
        with open(exploration_file, 'r') as f:
            exploration = json.load(f)
        
        # Get the nodes from the exploration
        exploration_nodes = exploration.get("nodes", [])
        if not exploration_nodes:
            raise ValueError(f"Exploration session has no nodes: {session['exploration_id']}")
        
        # Cluster the nodes
        if method == "tag_similarity":
            clusters = self._cluster_by_tags(exploration_nodes, num_clusters)
        elif method == "content_similarity":
            clusters = self._cluster_by_content(exploration_nodes, num_clusters)
        else:
            raise ValueError(f"Unknown clustering method: {method}")
        
        # Update the session
        session["clusters"] = clusters
        session["updated_at"] = datetime.now().isoformat()
        
        # Save the updated session
        with open(session_file, 'w') as f:
            json.dump(session, f, indent=2)
        
        print(f"Clustered nodes for synthesis: {session_id}")
        print(f"Method: {method}")
        print(f"Number of clusters: {len(clusters)}")
        
        return session
    
    def add_synthesis_node(self, session_id: str, title: str, content: str, 
                         cluster_id: Optional[str] = None,
                         source_node_ids: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Add a synthesis node based on clustered exploration nodes.
        
        Args:
            session_id: The synthesis session ID
            title: Title of the synthesis node
            content: Content of the node
            cluster_id: Optional cluster ID
            source_node_ids: Optional list of source node IDs
            
        Returns:
            The created node
        """
        # Load the synthesis session
        session_file = os.path.join(self.output_dir, f"{session_id}.json")
        if not os.path.exists(session_file):
            raise ValueError(f"Synthesis session not found: {session_id}")
        
        with open(session_file, 'r') as f:
            session = json.load(f)
        
        # Generate a node ID
        node_id = f"synth_node_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(session['nodes'])}"
        
        # Create the node
        node = {
            "id": node_id,
            "title": title,
            "content": content,
            "cluster_id": cluster_id,
            "source_node_ids": source_node_ids or [],
            "created_at": datetime.now().isoformat()
        }
        
        # Add the node to the session
        session["nodes"].append(node)
        
        # Update the session
        session["updated_at"] = datetime.now().isoformat()
        
        # Save the updated session
        with open(session_file, 'w') as f:
            json.dump(session, f, indent=2)
        
        print(f"Added synthesis node: {node_id}")
        print(f"Title: {title}")
        if cluster_id:
            print(f"Cluster: {cluster_id}")
        
        return node
    
    def finalize_synthesis(self, session_id: str, summary: str, 
                         quality_score: float = 0.0) -> Dict[str, Any]:
        """
        Finalize a synthesis session.
        
        Args:
            session_id: The synthesis session ID
            summary: Summary of the synthesis
            quality_score: Quality score (0.0 to 1.0)
            
        Returns:
            The updated session
        """
        # Load the synthesis session
        session_file = os.path.join(self.output_dir, f"{session_id}.json")
        if not os.path.exists(session_file):
            raise ValueError(f"Synthesis session not found: {session_id}")
        
        with open(session_file, 'r') as f:
            session = json.load(f)
        
        # Update the session
        session["status"] = "completed"
        session["summary"] = summary
        session["quality_score"] = max(0.0, min(1.0, quality_score))
        session["completion_time"] = datetime.now().isoformat()
        session["updated_at"] = datetime.now().isoformat()
        
        # Save the updated session
        with open(session_file, 'w') as f:
            json.dump(session, f, indent=2)
        
        print(f"Synthesis session finalized: {session_id}")
        print(f"Quality score: {quality_score}")
        print(f"Synthesis nodes: {len(session['nodes'])}")
        
        # If quality score is high enough, create a memory atom
        if quality_score >= 0.7:
            self._create_memory_atom(session)
        
        return session
    
    def list_syntheses(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List synthesis sessions.
        
        Args:
            status: Optional status filter
            
        Returns:
            List of synthesis sessions
        """
        sessions = []
        
        for file in os.listdir(self.output_dir):
            if file.startswith("synth_") and file.endswith(".json"):
                file_path = os.path.join(self.output_dir, file)
                
                try:
                    with open(file_path, 'r') as f:
                        session = json.load(f)
                    
                    # Apply status filter if provided
                    if status is None or session.get("status") == status:
                        sessions.append(session)
                
                except Exception as e:
                    print(f"Error reading session file {file}: {e}")
        
        # Sort by start time (newest first)
        sessions.sort(key=lambda x: x.get("start_time", ""), reverse=True)
        
        return sessions
    
    def simulate_synthesis(self, exploration_id: str) -> Dict[str, Any]:
        """
        Simulate a synthesis session for demo purposes.
        
        Args:
            exploration_id: ID of the exploration session to synthesize
            
        Returns:
            The simulated session
        """
        # Check if the exploration exists
        exploration_file = os.path.join("governance/explorations", f"{exploration_id}.json")
        if not os.path.exists(exploration_file):
            # Create a simulated exploration first
            from lightface import LightFaceExploration
            exploration_manager = LightFaceExploration("governance/explorations")
            exploration = exploration_manager.simulate_exploration("cognitive architecture", 2, 15)
            exploration_id = exploration["id"]
        else:
            # Load the exploration
            with open(exploration_file, 'r') as f:
                exploration = json.load(f)
        
        # Start the synthesis
        title = f"Synthesis of {exploration.get('topic', 'exploration')}"
        session = self.start_synthesis(exploration_id, title)
        session_id = session["id"]
        
        # Cluster the nodes
        session = self.cluster_nodes(session_id, "tag_similarity", 3)
        
        # Create synthesis nodes for each cluster
        for i, cluster in enumerate(session["clusters"]):
            cluster_id = cluster["id"]
            cluster_title = f"Synthesis of cluster {i+1}: {cluster['name']}"
            
            # Get source node IDs from the cluster
            source_node_ids = [node["id"] for node in cluster["nodes"]]
            
            # Generate content
            content = self._generate_synthesis_content(cluster["nodes"])
            
            self.add_synthesis_node(session_id, cluster_title, content, cluster_id, source_node_ids)
        
        # Create an overall synthesis
        overall_title = "Overall synthesis"
        overall_content = self._generate_overall_synthesis(session["clusters"])
        self.add_synthesis_node(session_id, overall_title, overall_content)
        
        # Finalize the synthesis
        summary = f"This synthesis of {exploration.get('topic', 'exploration')} identified {len(session['clusters'])} main themes and integrated them into a coherent framework."
        quality_score = random.uniform(0.7, 0.95)
        self.finalize_synthesis(session_id, summary, quality_score)
        
        # Reload the full session
        with open(os.path.join(self.output_dir, f"{session_id}.json"), 'r') as f:
            session = json.load(f)
        
        return session
    
    def _cluster_by_tags(self, nodes: List[Dict[str, Any]], num_clusters: int) -> List[Dict[str, Any]]:
        """Cluster nodes by tag similarity."""
        # In a real implementation, this would use a clustering algorithm
        # Here we'll simulate by grouping nodes with similar tags
        
        # Extract all tags
        all_tags = set()
        for node in nodes:
            if "tags" in node:
                all_tags.update(node["tags"])
        
        # Select random seed tags for clusters
        if len(all_tags) >= num_clusters:
            seed_tags = random.sample(list(all_tags), num_clusters)
        else:
            seed_tags = list(all_tags)
            # If not enough tags, duplicate some
            while len(seed_tags) < num_clusters:
                seed_tags.append(random.choice(list(all_tags)))
        
        # Initialize clusters
        clusters = []
        for i, tag in enumerate(seed_tags):
            clusters.append({
                "id": f"cluster_{i+1}",
                "name": f"Cluster: {tag}",
                "seed_tag": tag,
                "nodes": []
            })
        
        # Assign nodes to clusters
        for node in nodes:
            node_tags = node.get("tags", [])
            
            # Find the best cluster match
            best_cluster = None
            best_overlap = -1
            
            for cluster in clusters:
                seed_tag = cluster["seed_tag"]
                if seed_tag in node_tags:
                    # Direct match with seed tag
                    overlap = 1
                else:
                    # No direct match, count other tag overlaps
                    overlap = 0
                
                if overlap > best_overlap:
                    best_overlap = overlap
                    best_cluster = cluster
            
            # If no good match, assign to a random cluster
            if best_cluster is None:
                best_cluster = random.choice(clusters)
            
            # Add to the cluster
            best_cluster["nodes"].append(node)
        
        # Update cluster statistics
        for cluster in clusters:
            cluster["node_count"] = len(cluster["nodes"])
            
            # If a cluster is empty, assign a random node to it
            if cluster["node_count"] == 0 and nodes:
                random_node = random.choice(nodes)
                cluster["nodes"].append(random_node)
                cluster["node_count"] = 1
        
        return clusters
    
    def _cluster_by_content(self, nodes: List[Dict[str, Any]], num_clusters: int) -> List[Dict[str, Any]]:
        """Cluster nodes by content similarity."""
        # In a real implementation, this would use NLP and clustering algorithms
        # Here we'll simulate by using simple word overlap
        
        # Initialize clusters with random seed nodes
        if len(nodes) >= num_clusters:
            seed_nodes = random.sample(nodes, num_clusters)
        else:
            seed_nodes = nodes
            # If not enough nodes, duplicate some
            while len(seed_nodes) < num_clusters:
                seed_nodes.append(random.choice(nodes))
        
        clusters = []
        for i, seed_node in enumerate(seed_nodes):
            clusters.append({
                "id": f"cluster_{i+1}",
                "name": f"Theme: {seed_node.get('title', f'Cluster {i+1}')}",
                "seed_node": seed_node,
                "nodes": [seed_node]
            })
        
        # Assign remaining nodes to clusters
        remaining_nodes = [node for node in nodes if node not in seed_nodes]
        for node in remaining_nodes:
            # Randomly assign for the simulation
            cluster = random.choice(clusters)
            cluster["nodes"].append(node)
        
        # Update cluster statistics
        for cluster in clusters:
            cluster["node_count"] = len(cluster["nodes"])
        
        return clusters
    
    def _generate_synthesis_content(self, nodes: List[Dict[str, Any]]) -> str:
        """Generate synthesis content from a cluster of nodes."""
        # Extract concepts from nodes
        concepts = []
        for node in nodes:
            concepts.append(node.get("title", ""))
        
        # Remove duplicates and limit
        unique_concepts = list(set(concepts))[:5]
        
        # Generate a synthesized paragraph
        synthesis_templates = [
            "Analysis of the exploration nodes in this cluster reveals several interconnected themes. {concepts} emerge as central concepts that form a coherent theoretical framework. The relationships between these elements suggest a novel approach to understanding the broader domain.",
            
            "Synthesis of the exploration branches in this cluster shows how {concepts} interact in complex ways. These interactions point to emergent properties not visible when examining each concept in isolation. This holistic view provides valuable insights for further research.",
            
            "Integration of ideas across this cluster demonstrates how {concepts} can be unified under a common theoretical framework. This integration resolves apparent contradictions and creates a more robust understanding of the domain. The synthesis opens new avenues for both theoretical development and practical application.",
            
            "Examining this cluster reveals patterns connecting {concepts} in unexpected ways. These connections suggest underlying principles that may have broader applicability. By synthesizing these diverse elements, we gain a more nuanced understanding of the complex relationships involved."
        ]
        
        template = random.choice(synthesis_templates)
        concepts_text = ", ".join(unique_concepts)
        
        return template.format(concepts=concepts_text)
    
    def _generate_overall_synthesis(self, clusters: List[Dict[str, Any]]) -> str:
        """Generate an overall synthesis from all clusters."""
        # Extract cluster names
        cluster_names = [cluster.get("name", "").replace("Cluster: ", "").replace("Theme: ", "") for cluster in clusters]
        
        synthesis_template = """The exploration of {topic} has yielded several distinct but interconnected clusters of insights.

{cluster_details}

These clusters represent complementary perspectives on the broader topic. When integrated, they form a cohesive framework that balances theoretical depth with practical applicability. This synthesis demonstrates how seemingly disparate concepts actually reinforce and elaborate each other when viewed through an appropriate theoretical lens.

The most significant insight from this synthesis is the emergence of patterns that transcend individual clusters. These meta-patterns suggest fundamental principles that could guide future research and application development in this domain.

This synthesis provides both a comprehensive overview of the current conceptual landscape and identifies promising directions for further exploration."""
        
        # Generate details for each cluster
        cluster_details = ""
        for i, name in enumerate(cluster_names):
            cluster_details += f"{i+1}. **{name}** - Represents a distinct perspective focusing on "
            
            # Add some random focus areas
            focus_areas = ["theoretical foundations", "practical applications", 
                          "methodological approaches", "conceptual frameworks",
                          "integration patterns", "emergent properties"]
            
            cluster_details += f"{random.choice(focus_areas)}.\n\n"
        
        return synthesis_template.format(topic="the domain", cluster_details=cluster_details)
    
    def _create_memory_atom(self, session: Dict[str, Any]) -> None:
        """Create a memory atom from a synthesis session."""
        # In a real implementation, this would create a proper memory atom
        # For now, we'll just print what would happen
        memory_dir = "memory/atoms"
        os.makedirs(memory_dir, exist_ok=True)
        
        # Create a simplified memory atom
        atom = {
            "id": f"semantic/{datetime.now().strftime('%Y-%m-%d')}_{session['id']}",
            "type": "semantic",
            "tags": ["synthesis", "toroidal-grammar", "darkface"],
            "actors": ["DarkFace Synthesizer"],
            "source": "synthesis_session",
            "created_at": datetime.now().isoformat(),
            "content": session.get("summary", "Synthesis results"),
            "content_hash": f"sha256:{'0'*64}",  # Placeholder
            "links": [
                {
                    "relation": "derives-from",
                    "target": f"exploration/{session['exploration_id']}"
                }
            ]
        }
        
        # Write to a file
        output_file = os.path.join(memory_dir, f"synthesis_{session['id']}.json")
        with open(output_file, 'w') as f:
            json.dump(atom, f, indent=2)
        
        print(f"Created memory atom: {atom['id']}")
        print(f"Saved to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="DarkFace Synthesis Manager")
    parser.add_argument('--output-dir', default="governance/syntheses", help='Directory to store synthesis results')
    parser.add_argument('--exploration', help='Exploration session ID to synthesize')
    parser.add_argument('--title', default="Synthesis Session", help='Title for the synthesis')
    parser.add_argument('--list', action='store_true', help='List synthesis sessions')
    parser.add_argument('--status', choices=['active', 'completed'], help='Filter sessions by status')
    parser.add_argument('--simulate', action='store_true', help='Simulate a synthesis session')
    
    args = parser.parse_args()
    
    synthesis_manager = DarkFaceSynthesis(args.output_dir)
    
    if args.list:
        sessions = synthesis_manager.list_syntheses(args.status)
        print(f"\nSynthesis Sessions ({len(sessions)}):")
        
        for i, session in enumerate(sessions):
            print(f"\n{i+1}. {session['id']}")
            print(f"   Title: {session['title']}")
            print(f"   Status: {session['status'].upper()}")
            print(f"   Based on: {session['exploration_id']}")
            print(f"   Nodes: {len(session['nodes'])}")
            if "quality_score" in session:
                print(f"   Quality: {session['quality_score']:.2f}")
    
    elif args.simulate:
        if args.exploration:
            session = synthesis_manager.simulate_synthesis(args.exploration)
        else:
            print("Error: Must specify an exploration ID for simulation")
            print("Creating a new exploration first...")
            from lightface import LightFaceExploration
            exploration_manager = LightFaceExploration("governance/explorations")
            exploration = exploration_manager.simulate_exploration("cognitive architecture", 2, 15)
            session = synthesis_manager.simulate_synthesis(exploration["id"])
        
        print(f"\nSimulated synthesis session: {session['id']}")
        print(f"Generated {len(session['nodes'])} synthesis nodes from {len(session['clusters'])} clusters")
        print(f"Quality score: {session.get('quality_score', 0):.2f}")
    
    elif args.exploration:
        # Start a new synthesis
        synthesis_manager.start_synthesis(args.exploration, args.title)
    
    else:
        print("Error: Must specify an exploration ID or use --list/--simulate")

if __name__ == "__main__":
    main()