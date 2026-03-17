# NAM Trainer

A batch processing GUI for neural-amp-modeler with queue management, progress monitoring, and customizable output filenames.

## Project Structure

```
nam_trainer/
├── neural-amp-modeler/     # Git submodule - upstream NAM library
│   └── nam/               # Original NAM training code
│       └── train/
│           ├── core.py    # Core training logic (API)
│           └── full.py    # CLI training entry point
│
├── nam_trainer/            # Custom GUI code (your edits)
│   └── gui/
│       ├── __init__.py   # Main GUI window
│       └── _resources/
│           ├── queue.py        # Training queue system
│           └── queue_window.py # Queue UI window
│
└── test_queue.py          # Quick launcher for queue window
```

## Design Overview

### Two-Layer Architecture

1. **NAM Library** (`neural-amp-modeler/`): The upstream neural-amp-modeler library. This is a git submodule that can be updated independently.

2. **Custom GUI** (`nam_trainer/`): Your modifications to add batch processing capabilities. This includes:
   - Queue management system
   - Queue window UI
   - Custom output filename templates

### Queue System

The queue system (`queue.py`) manages multiple training jobs:

- **TrainingJob**: Dataclass representing a single job with input/output paths, architecture, metadata, and progress info
- **TrainingQueue**: Manages the queue of jobs, runs them in a background thread
- **Progress tracking**: Monitors subprocess output and checkpoint directories for epoch progress

### Job Execution

Jobs run as subprocesses calling `nam-full` (the CLI tool). Each job gets:
- A unique job-specific directory (`job_<job_id>/`) for isolated checkpoints
- Config files written to a temp directory
- Output monitoring via stdout parsing

### Custom Output Filenames

Output filenames can be customized using tokens:

| Token | Description |
|-------|-------------|
| `{input}` | Input file base name |
| `{arch}` | Architecture (standard, lite, feather, nano) |
| `{date}` | Date (YYYY-MM-DD) |
| `{time}` | Time (HH-MM-SS) |
| `{creator}` | Modeled by field |
| `{gear_type}` | Gear type (head, combo, cab, pedal, etc.) |
| `{guid}` | Batch GUID for grouping related jobs |

Example: `{creator}_{gear_type}_{date}_{guid}` → `Gene_cab_2026-03-17_a1b2c3d4`

## Features

- **Batch job creation**: Add multiple jobs via single input+multiple outputs, or CSV import
- **Job reordering**: Move jobs up/down in queue
- **Pause/Resume**: Pause queue processing between jobs
- **Progress monitoring**: Epoch progress shown in Status column
- **Time estimation**: Remaining time based on epoch progress
- **Custom metadata**: Model name, creator, gear type, etc.

## Running

```bash
# From project root
cd /Users/gene/work/nam_trainer
/opt/homebrew/opt/python@3.12/bin/python3.12 test_queue.py
```

Or use the original NAM GUI which includes queue access:
```bash
nam
# Click "Add to Queue" button
```

## Updating NAM Library

The `neural-amp-modeler` is a git submodule. To update:

```bash
cd neural-amp-modeler
git pull origin main
cd ..
git add neural-amp-modeler
git commit -m "Update NAM to latest"
```

## Key Files

- `neural-amp-modeler/nam/train/full.py`: CLI entry point (modified to add epoch progress output)
- `neural-amp-modeler/nam/train/core.py`: Core training API
- `nam_trainer/gui/_resources/queue.py`: Queue management system
- `nam_trainer/gui/_resources/queue_window.py`: Queue UI window
