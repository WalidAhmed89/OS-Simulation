# Frosted OS Simulator
> A desktop simulation of core operating system concepts with an interactive GUI.

![Python](https://img.shields.io/badge/Python-3.x-blue?style=flat-square)
![Tkinter](https://img.shields.io/badge/GUI-Tkinter-informational?style=flat-square)
![License](https://img.shields.io/badge/Purpose-Educational-lightgrey?style=flat-square)

---

## Overview

Frosted OS is an interactive desktop application that demonstrates core operating system concepts — process scheduling, memory allocation, file system management, and I/O device handling — through a real-time graphical interface. Built with Python and Tkinter, it allows users to create processes, observe scheduling decisions, navigate a virtual file system, and manage simulated I/O devices.

---

## Features

### Process Management
- Create and terminate processes dynamically
- Round Robin scheduling with a configurable time quantum
- Step-by-step auto execution mode
- Interactive process table with live state updates
- Role-based process permissions (ADMIN / GUEST)
- Shared process state via `processes.json` enabling cross-module communication
- Process spawning on login — each authenticated user session spawns a dedicated process

**Process States:**
| State    | Description                          |
|----------|--------------------------------------|
| Ready    | Process is queued, waiting for CPU   |
| Running  | Process is currently using the CPU   |
| Waiting  | Process is blocked (e.g., on I/O)   |
| Finished | Process completed and removed        |

**State Transitions:**
```
Login → Spawn Process (Ready)
             ↓
       Scheduler picks it → Running
             ↓
       Quantum expires → Back to Ready
             ↓
       Burst complete → Finished → Removed
```

### Memory Management
- Dynamic memory allocation and deallocation
- First-Fit allocation strategy
- Free block merging to reduce fragmentation
- Real-time visual memory map
- Memory-full dialog when allocation limit is reached

### File System
- Virtual file system backed by `fs.json` for persistent state
- Full Linux-style CLI terminal (cd, ls, mkdir, touch, rm, cat, write, pwd, help)
- Collapsible Explorer tree view for visual navigation
- File/folder create, delete, read, and write operations
- Terminal CLI protection — prevents running commands while a process is active

### I/O Device Management
- Simulated I/O device lifecycle management
- Device state tracking integrated with process states
- GUEST-locked device controls (admin-only operations)

### Authentication & Roles
- Login system with user role assignment (ADMIN / GUEST)
- Login button state managed during authentication to prevent double-submit
- Role-based UI — GUEST users see locked feature cards
- Session spawns a process entry on successful login

### GUI
- Built entirely with Tkinter (no external dependencies)
- Color-coded process state indicators
- Real-time simulation updates
- Task Manager with selection preservation during live refresh
- Unified home screen routing all subsystem modules

---

## Architecture

### Inter-Module Communication
Python subprocesses cannot share in-memory state directly. Frosted OS solves this using a **JSON-backed shared state layer**:

- `processes.json` — shared process registry; read and written by all modules via `process_api.py`
- `fs.json` — virtual filesystem state; managed by `filesystem_core.py`

This allows the Process, Memory, File System, and I/O modules to stay synchronized without a shared runtime.

### Module Overview
```
FrostedOS/
├── main.py                  # Entry point
├── login.py                 # Authentication, role assignment, process spawning
├── home.py                  # Main dashboard, module routing, Task Manager
├── Process.py               # Scheduler, Round Robin, process lifecycle
├── process_api.py           # JSON-backed shared state API (processes.json)
├── memory_manager.py        # First-Fit allocator, free block merging
├── DeviceManagement.py      # I/O device simulation
├── file_page.py             # File System GUI (Explorer + Terminal)
├── filesystem_core.py       # Virtual FS logic, fs.json persistence
├── processes.json           # Runtime shared process state
└── fs.json                  # Persistent virtual filesystem state
```

---

## How It Works

### Round Robin Scheduling
Each process is assigned a fixed CPU time slice (quantum). If a process does not finish within its quantum, it is moved to the back of the Ready queue. This continues until the process completes.

```
[Ready Queue] → Dequeue → Run for 1 quantum
                              ↓
                    Finished? → Remove from system
                    Not done? → Re-enqueue at tail
```

### First-Fit Memory Allocation
When a process requests memory, the allocator scans the free block list from the beginning and assigns the first block large enough to satisfy the request. On deallocation, adjacent free blocks are merged to minimize fragmentation.

### Virtual File System
The file system is represented as a nested JSON tree (`fs.json`). `filesystem_core.py` exposes operations (create, delete, read, write, navigate) used by both the terminal CLI and the Explorer GUI tree view.

---

## Getting Started

**Requirements:** Python 3.x — Tkinter is included in the standard library, no additional packages needed.

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/FrostedOS.git

# 2. Navigate to the project directory
cd FrostedOS

# 3. Run the simulator
python main.py
```

> **Note for Windows users:** Python is case-insensitive on Windows but the import system is not always consistent. Ensure filenames match their import statements exactly (e.g., `filesystem_core.py`, not `FilesSystem_core.py`).

---

## Team

| Name               | Module                  |
|--------------------|-------------------------|
| Walid Ahmed        | Process Management      |
| Ahmed Abd El Hamid | Memory Management       |
| Adham Al Amir      | File System & Security  |
| Ahmed              | File System & Security  |
| Zeyad Mohamed      | I/O Management          |
| Habiba Hamdy       | UI & UX                 |

---

## Planned Improvements
- Additional scheduling algorithms: Priority Scheduling, Shortest Job First (SJF)
- Scheduling statistics: waiting time, turnaround time, CPU utilization
- Enhanced UI with animations, progress bars, and a richer memory map

---

## Notes
This project is developed for educational purposes as part of an Operating Systems course. It demonstrates core OS concepts in a simplified, visual simulation environment.
