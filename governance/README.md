# Toroidal Grammar Governance

The Toroidal Grammar Governance system provides a framework for balancing exploration (LightFace) and synthesis (DarkFace) in the Marduk Cognitive Tokamak.

## Core Components

- **LightFace** - Generative, tree-like branching into uncharted domains
- **DarkFace** - Membrane-like constraints that refine and integrate discoveries

## Structure

- `governance/lightface.py` - Tools for exploration phases
- `governance/darkface.py` - Tools for synthesis phases
- `governance/cycle.py` - Manages the alternation between phases
- `governance/policies/` - Configuration files for governance policies

## Usage

```bash
# Start a LightFace exploration sprint
python governance/lightface.py --duration 2 --topic "neural-symbolic integration"

# Start a DarkFace synthesis cycle
python governance/darkface.py --input-file exploration_results.json

# Run a complete toroidal cycle
python governance/cycle.py --config governance/policies/default.yaml
```