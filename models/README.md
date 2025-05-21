# Marduk-LLM Constellation

This directory contains the components for Marduk's language model infrastructure, designed to embody the Marduk essence through fine-tuned models and retrieval-augmented generation.

## Components

- `foundation/` - Base models and configurations
- `fine-tune/` - Fine-tuning scripts and utilities
- `rag/` - Retrieval-augmented generation system
- `interface/` - Interaction interfaces for the model

## Model Tree

- `foundation` - Open-weights model (Mistral-7B / Mixtral)
- `subspace-marduk` - Fine-tuned on curated memory atoms
- `daemon-core` - RAG wrapper with Bolt integration

## Usage

```bash
# Prepare data for fine-tuning
python models/fine-tune/prepare_data.py --input memory/atoms/pilot_dataset.json --output models/fine-tune/training_data.jsonl

# Fine-tune the model
python models/fine-tune/run_finetune.py --base-model mistral-7b --train-file models/fine-tune/training_data.jsonl

# Run inference with the fine-tuned model
python models/interface/cli.py --model models/checkpoints/subspace-marduk-latest
```