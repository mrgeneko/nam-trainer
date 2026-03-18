# NAM Trainer

A batch processing GUI for neural-amp-modeler with queue management, progress monitoring, and customizable output filenames.

## Project Structure

```
nam_trainer/
├── neural-amp-modeler/     # Git submodule - upstream NAM library (kept unmodified)
│   └── nam/               # Original NAM training code
│       └── train/
│           ├── core.py    # Core training logic (API)
│           └── full.py   # CLI training entry point
│
├── nam_trainer/            # Custom GUI code (overrides submodule)
│   └── gui/
│       └── _resources/
│           ├── config.py        # Settings persistence
│           ├── queue.py        # Training queue system
│           └── queue_window.py # Queue UI window
│
└── test_queue.py          # Launcher for queue window
```

## Design Overview

### Keeping Upstream Clean

The `neural-amp-modeler` submodule is kept unmodified to simplify syncing with upstream updates. All custom GUI code lives in `nam_trainer/gui/_resources/`.

The launcher (`test_queue.py`) imports from the local files:
```python
sys.path.insert(0, str(Path(__file__).parent / "nam_trainer" / "gui" / "_resources"))
from queue import TrainingQueue
from queue_window import QueueWindow
```

This means:
- Submodule can be updated with `git submodule update --remote` without conflicts
- Custom changes don't affect the upstream library
- Local files are standalone and self-contained

### Two-Layer Architecture

1. **NAM Library** (`neural-amp-modeler/`): The upstream neural-amp-modeler library. This is a git submodule that can be updated independently.

2. **Custom GUI** (`nam_trainer/`): Local modifications that override/extend the submodule imports. This includes:
   - Queue management system
   - Queue window UI
   - Settings persistence
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
| `{size}` | Architecture size (standard, lite, feather, nano) |
| `{date}` | Date (YYYY_MM_DD) |
| `{time}` | Time (HH_MM_SS) |
| `{creator}` | Modeled by field |
| `{type}` | Gear type (head, combo, cab, pedal, etc.) |
| `{guid}` | Batch GUID for grouping related jobs (formatted as `__ID_{guid}__`) |
| `{model}` | Model name |

Example: `__ID_{guid}__{model}_{type}_{size}_{date}` → `__ID_a1b2c3d4__MyAmp_cab_standard_2026_03_17`

## Features

- **Batch job creation**: Add multiple jobs via single input+multiple outputs
- **Job reordering**: Move jobs up/down in queue
- **Progress monitoring**: Epoch progress and best ESR shown in Status column
- **Time estimation**: Remaining time based on epoch progress
- **Custom metadata**: Model name, creator, gear type, tone type, etc.
- **Settings persistence**: Remembers default values across sessions

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

- `neural-amp-modeler/nam/train/full.py`: CLI entry point
- `neural-amp-modeler/nam/train/core.py`: Core training API
- `nam_trainer/gui/_resources/queue.py`: Queue management system
- `nam_trainer/gui/_resources/queue_window.py`: Queue UI window
- `nam_trainer/gui/_resources/config.py`: Settings persistence
