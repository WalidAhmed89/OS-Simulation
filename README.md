# OS Simulator

> A desktop simulation of core operating system concepts with an interactive GUI.

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-informational?style=flat-square)
![License](https://img.shields.io/badge/Purpose-Educational-lightgrey?style=flat-square)

---

## Overview

OS Simulator is an interactive desktop application that demonstrates core operating system concepts — process scheduling and memory allocation — through a real-time graphical interface. Built with Python and Tkinter, it allows users to create processes, observe scheduling decisions, and visualize memory usage step by step.

---

## Features

### Process Management
- Create and terminate processes dynamically
- Round Robin scheduling with a configurable time quantum
- Step-by-step auto execution mode
- Interactive process table with live state updates

**Process States:**

| State    | Description                          |
|----------|--------------------------------------|
| Ready    | Process is queued, waiting for CPU   |
| Running  | Process is currently using the CPU   |
| Waiting  | Process is blocked (e.g., on I/O)   |
| Finished | Process completed and removed        |

### Memory Management
- Dynamic memory allocation and deallocation
- First-Fit allocation strategy
- Free block merging to reduce fragmentation
- Real-time visual memory map

### GUI
- Built entirely with Tkinter (no external dependencies)
- Color-coded process state indicators
- Real-time simulation updates

---

## How It Works

### Round Robin Scheduling

Each process is assigned a fixed CPU time slice (quantum). If a process does not finish within its quantum, it is moved to the back of the Ready queue. This continues until the process completes and is removed from the system.

```
[Ready Queue] → Dequeue → Run for 1 quantum
                              ↓
                    Finished? → Remove from system
                    Not done? → Re-enqueue at tail
```

### First-Fit Memory Allocation

When a process requests memory, the allocator scans the free block list from the beginning and assigns the first block large enough to satisfy the request. On deallocation, adjacent free blocks are merged to minimize fragmentation over time.

---

## Project Structure

```
OS-Simulator/
├── main.py                  # Entry point
├── gui.py                   # Tkinter interface
├── process_management.py    # Scheduler and process states
├── memory_manager.py        # Allocation and free block merging
└── README.md
```

---

## Getting Started

**Requirements:** Python 3.x — Tkinter is included in the standard library, no additional packages needed.

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/OS-Simulator.git

# 2. Navigate to the project directory
cd OS-Simulator

# 3. Run the simulator
python main.py
```

---

## Team

| Name               | Module                  |
|--------------------|-------------------------|
| Walid Ahmed        | Process Management      |
| Ahmed Abd El Hamid | Memory Management       |
| Adham Al Amir      | File System & Security  |
| Ahmed              | File System & Security  |
| Zeyad Mohamed      | I/O Management          |
| Hazem              | I/O Management          |
| Habiba Hamdy       | UI & UX                 |

---

## Planned Improvements

- Additional scheduling algorithms: Priority Scheduling, Shortest Job First (SJF)
- Scheduling statistics: waiting time, turnaround time, CPU utilization
- Unified integration of all subsystems into a single cohesive simulation
- Enhanced UI with animations, progress bars, and a richer memory map

---

## Notes

This project is developed for educational purposes as part of an Operating Systems course. It demonstrates core OS concepts in a simplified, visual simulation environment.
