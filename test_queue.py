#!/usr/bin/env python3
"""
Simple launcher for the queue window
"""

import sys
from pathlib import Path

# Add the parent directory to the path so we can import from nam_trainer
sys.path.insert(0, str(Path(__file__).parent.parent / "neural-amp-modeler"))

# Import the queue window from our modified files
from nam.train.gui._resources.queue import TrainingQueue
from nam.train.gui._resources.queue_window import QueueWindow

import tkinter as tk

def main():
    root = tk.Tk()
    root.withdraw()  # Hide the main window, we'll just show the queue window
    
    queue = TrainingQueue()
    queue_window = QueueWindow(root, queue)
    
    print("Queue window opened. Close the window to exit.")
    root.mainloop()

if __name__ == "__main__":
    main()
