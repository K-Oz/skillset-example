# Bolt Process Encoding Framework

Bolt is a framework for encoding, executing, and managing experiments and processes within the Marduk Cognitive Tokamak.

## Structure

- `experiments/` - YAML/TOML descriptors for experiments
- `agents/` - Reusable worker blueprints
- `primitives/` - Core Bolt operations

## Usage

To run an experiment:

```bash
python bolt/run.py --experiment experiments/synthesize_toroidal_grammar.toml
```

## Experiment Definition

Experiments are defined in TOML files with the following structure:

```toml
name = "experiment_name"
description = "Description of the experiment"
memory_tags = ["tag1", "tag2"]
steps = [
  { op = "operation_name", param1 = "value1", param2 = "value2" }
]
```

## Available Operations

- `search` - Search for memory atoms
- `cluster` - Cluster atoms by similarity
- `summarize` - Generate summaries of atom clusters
- `publish` - Publish results to a channel