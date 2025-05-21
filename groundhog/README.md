# Groundhog-Day Resilience

This module implements solutions to the persistence problem, ensuring that the Marduk Cognitive Tokamak maintains continuity across system restarts.

## Components

- `checkpoint.py` - Create periodic checkpoints of the system state
- `backup.py` - Create backups of memory atoms and model checkpoints
- `restore.py` - Restore the system from checkpoints
- `diff.py` - Generate cognitive diffs to track changes

## Usage

```bash
# Create a checkpoint
python groundhog/checkpoint.py --name "weekly"

# Create a backup
python groundhog/backup.py --destination s3://my-backup-bucket

# Restore from checkpoint
python groundhog/restore.py --checkpoint checkpoints/weekly_20240617

# Initialize after a restart
make groundhog-init
```