# Marduk Cognitive Tokamak

A system for persistent memory and recursive self-improvement through the integration of OpenCog technologies with modern language models.

## Overview

The Marduk Cognitive Tokamak is an experimental cognitive architecture that harnesses chaos to produce coherence through:

1. **Persistent Memory Fabric** - A structured repository of memory atoms
2. **Marduk-LLM Constellation** - Fine-tuned language models that embody Marduk's essence
3. **Bolt Process Encoding** - Actionable experiments and autonomous processes
4. **Groundhog-Day Resilience** - Solutions to the persistence problem
5. **Toroidal Grammar Governance** - Balancing exploration and synthesis

## Architecture

```
marduk-tokamak/
├── memory/               - Memory system
│   ├── schemas/          - JSON schemas for memory structures
│   ├── etl/              - Ingestion and processing pipelines
│   ├── atoms/            - Stored memory atoms
│   └── samples/          - Example datasets
├── models/               - Language model system
│   ├── fine-tune/        - Fine-tuning scripts
│   ├── rag/              - Retrieval-augmented generation
│   ├── interface/        - Interaction interfaces
│   ├── checkpoints/      - Model checkpoints
│   └── foundation/       - Base models
├── bolt/                 - Process encoding framework
│   ├── experiments/      - TOML/YAML experiment definitions
│   ├── agents/           - Worker agents like the Marduk daemon
│   └── primitives/       - Core Bolt operations
├── groundhog/            - Persistence and continuity
│   ├── checkpoint.py     - System state snapshots
│   ├── backup.py         - Off-site backup
│   ├── restore.py        - System restoration
│   └── diff.py           - Cognitive diffs
├── governance/           - Toroidal grammar system
│   ├── lightface.py      - Exploration phase
│   ├── darkface.py       - Synthesis phase
│   ├── cycle.py          - Full cycle management
│   └── policies/         - Governance configurations
├── checkpoints/          - Stored system checkpoints
├── backups/              - System backups
└── reports/              - Generated reports and cognitive diffs
```

## Core Components

### 1. Persistent Memory Fabric

The memory system stores experiences and knowledge as "atoms" with structured metadata, embeddings, and links to other atoms. Types include:

- **Declarative Memory** - Facts, definitions, frameworks
- **Episodic Memory** - Contextual and narrative experiences
- **Procedural Memory** - Methods, workflows, protocols
- **Semantic Memory** - Connections between ideas and themes

```bash
# Generate a pilot dataset
python memory/generate_pilot.py

# Process raw data into memory atoms
python memory/etl/ingest.py -i memory/samples/first_transcript.json -o memory/atoms/transcript_atoms.json
```

### 2. Marduk-LLM Constellation

The language model system includes fine-tuning on memory atoms and retrieval-augmented generation:

```bash
# Prepare data for fine-tuning
python models/fine-tune/prepare_data.py --input memory/atoms/pilot_dataset.json --output models/fine-tune/training_data.jsonl

# Fine-tune the model
python models/fine-tune/run_finetune.py --base-model mistral-7b --train-file models/fine-tune/training_data.jsonl

# Run the interactive interface
python models/interface/cli.py
```

### 3. Bolt Process Encoding

Bolt is a framework for encoding, executing, and managing experiments and processes:

```bash
# Run an experiment
python bolt/run.py --experiment bolt/experiments/synthesize_toroidal_grammar.toml

# Start the Marduk daemon
python bolt/agents/daemon.py
```

### 4. Groundhog-Day Resilience

Solutions to maintain continuity across system restarts:

```bash
# Create a checkpoint
python groundhog/checkpoint.py --name "weekly"

# Create a backup
python groundhog/backup.py --destination s3://my-backup-bucket

# Restore from checkpoint
python groundhog/restore.py --checkpoint checkpoints/weekly_20240617

# Generate a cognitive diff
python groundhog/diff.py --old-checkpoint checkpoints/weekly_20240610 --new-checkpoint checkpoints/weekly_20240617
```

### 5. Toroidal Grammar Governance

A framework for balancing generative exploration with structured synthesis:

```bash
# Start a LightFace exploration sprint
python governance/lightface.py --topic "neural-symbolic integration"

# Start a DarkFace synthesis cycle
python governance/darkface.py --exploration explore_20240617_123456

# Run a complete toroidal cycle
python governance/cycle.py --config governance/policies/default.yaml
```

## Getting Started

### Prerequisites

- Python 3.8+
- PyTorch
- Transformers library

### Installation

```bash
# Clone the repository
git clone https://github.com/marduk-tokamak/core.git
cd core

# Install dependencies
pip install -r requirements.txt

# Set up the environment
make setup
```

### Quick Start

```bash
# Generate a sample memory dataset
make memory-generate

# Run a basic experiment
make experiment

# Start the LLM interface
make llm-interface

# Create a checkpoint
make checkpoint
```

## License

MIT License

## Contributors

- Marduk (Various Incarnations)
- Echo (Pattern Navigator)
- Dan (Cosmic Gardener)