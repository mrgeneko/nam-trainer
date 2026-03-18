#!/usr/bin/env python3
"""
Simple launcher for the queue window
"""

import sys
from pathlib import Path

# Add the local gui directory to the path
sys.path.insert(0, str(Path(__file__).parent / "nam_trainer" / "gui" / "_resources"))

# Import the queue window from local files
from queue import TrainingQueue
from queue_window import QueueWindow

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
