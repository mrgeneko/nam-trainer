# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Is

NAM Trainer is a batch processing GUI for the [neural-amp-modeler](https://github.com/sdatkinson/neural-amp-modeler) library. It lets users queue multiple neural amp model training jobs, configure metadata and output filenames per job, and run them sequentially while monitoring progress.

## Commands

```bash
# Run the app
python test_queue.py

# Run tests
pytest

# Run a single test file
pytest tests/test_training_queue.py

# Build standalone executable (requires pyinstaller)
pyinstaller nam_trainer.spec
```

## Architecture

The project has two layers:

1. **Upstream NAM library** (`neural-amp-modeler/` git submodule) — kept completely unmodified so it can be synced with upstream. `sys.path` manipulation ensures local modules are found first.

2. **Custom GUI layer** (`nam_trainer/gui/_resources/`) — the training queue system, UI, and config persistence built on top of NAM.

### Core modules

- `test_queue.py` — entry point; creates the root Tk window and opens the queue window
- `nam_trainer/gui/_resources/training_queue.py` — `TrainingJob` dataclass and `TrainingQueue` executor. Jobs run as subprocesses calling `nam-full` CLI (not the Python API). Stdout is parsed for epoch/ESR progress. Pause/resume/stop use process signals via a single worker thread.
- `nam_trainer/gui/_resources/queue_window.py` — tkinter `QueueWindow` with job treeview, Add Job dialog, and real-time polling for progress updates.
- `nam_trainer/gui/_resources/config.py` — JSON config at `~/.config/nam_trainer/settings.json`. Stores defaults for paths, architecture, epochs, ESR threshold, output template, and metadata.
- `nam_trainer/gui/__init__.py` — upstream NAM GUI modified to add an "Add to Queue" button.

### Output filename templating

Jobs use token replacement for output filenames:

| Token | Value |
|-------|-------|
| `{input}` | Input wav basename |
| `{size}` | Architecture size or "slimmable" for A2 |
| `{date}` | `YYYY_MM_DD` |
| `{time}` | `HH_MM_SS` |
| `{creator}` | "Modeled by" field |
| `{type}` | Gear type (cab, head, combo, …) |
| `{guid}` | Batch GUID with `__ID_` prefix |
| `{model}` | Model name field |

Default template: `__ID_{guid}__{model}_{type}_{size}_{date}`

### Threading model

- One worker thread runs the job loop with `pause_event`, `stop_event` flags.
- GUI updates (treeview, progress) are done on the main thread via polling, not callbacks.
- Job subprocesses are terminated via `process.terminate()` / `process.kill()` on stop/cancel.

## Key Design Decisions

- **Subprocess over Python API**: Training runs as `nam-full` subprocess calls for process isolation and clean pause/resume/stop without threading hazards.
- **Unmodified submodule**: All NAM customizations are external to the submodule directory, making upstream syncs trivial.
- **No ORM / database**: Job state lives in memory as a list of `TrainingJob` dataclasses. Only user preferences are persisted (config.json).
