# come-361-project
# CPU Scheduling Visualizer

This project simulates and visualizes various CPU scheduling algorithms as part of the Operating Systems course. Results can be viewed in the terminal or in a graphical interface with a Gantt chart.

## Requirements
- Python 3.10 or newer
- `colorama` (colored terminal output), `openpyxl` (Excel export), `matplotlib` (Gantt chart in the interface)
- Tkinter (comes with Python from python.org)

Install the dependencies:

`python3 -m pip install -r requirements.txt`

> **macOS note:** The Python that comes with Xcode has an old version of Tkinter, and the interface window opens blank. Install Python from [python.org](https://www.python.org/downloads/) and run the program with that version (e.g. `python3.15 gui.py`).

## Running the Program
Graphical interface:

`python3 gui.py`

Terminal version:

`python3 main.py`

Tests:

`python3 test_scheduler.py`

## Input Format (`input.txt`)
Each line describes one process: `PID Arrival Burst [Priority]`

```
1 0 8 2
2 1 4 1
```

The priority column is optional (default 0). A smaller number means a higher priority. Lines starting with `#` are ignored. Invalid lines (non-numeric values, missing columns, burst ≤ 0, negative arrival, duplicate PID) are skipped with a warning.

Processes can also be entered by hand, in the terminal menu or in the interface.

## Algorithms
1. FCFS (First-Come, First-Served)
2. SJF (Shortest Job First, non-preemptive)
3. SRTF (Shortest Remaining Time First, preemptive)
4. Priority Scheduling (non-preemptive)
5. Round Robin (time quantum is entered by the user)
6. Compare all algorithms in a single table

Ties are broken by arrival time, then by PID.

## Features
- Waiting time and turnaround time for each process, with averages
- CPU utilization, total time and number of context switches
- Gantt chart with idle time (IDLE) and context switch (CS) blocks
- Optional context switch delay
- Comparison table that highlights the algorithm with the lowest average waiting time
- Results can be appended to `rapor.xlsx` (saved next to `main.py`) and opened in Excel or Numbers. If `openpyxl` is missing, a `rapor.csv` is written instead.

## Project Structure
| File | Content |
|---|---|
| `main.py` | Terminal menu, reading `input.txt` |
| `gui.py` | Graphical interface (Tkinter + Matplotlib) |
| `process.py` | `Process` class |
| `fcfs.py`, `sjf.py`, `srtf.py`, `priority.py`, `rr.py` | Scheduling algorithms |
| `utils.py` | Metrics, terminal output, Excel/CSV export |
| `test_scheduler.py` | Tests with textbook examples and edge cases |

## Task Distribution
- **Harun Görgün:** Algorithm Design and Development
  - Coded the core logic (`fcfs_schedule`) of the First-Come, First-Served (FCFS) algorithm in `fcfs.py`, including the calculation of CPU idle times, process waiting times and turnaround times.
  - Graphical interface (`gui.py`).
- **Beyza Arda:** Data Models & Core Architecture
  - Created the fundamental data structures in `process.py` and designed the `Process` class (PID, arrival time, burst time, priority, remaining time).
  - SJF and SRTF algorithms (`sjf.py`, `srtf.py`).
- **Arda Çiçekli:** System Integration & File I/O
  - Developed `main.py`, which manages the main execution flow of the simulation: parsing and reading process data from `input.txt`, missing file checks and feeding the objects into the algorithms.
  - Priority Scheduling and Round Robin algorithms (`priority.py`, `rr.py`).
  - Tests (`test_scheduler.py`).
- **Mehmethan Ünlü:** Visualization & Reporting
  - Designed the `print_results` function (`utils.py`): printing the algorithm metrics to the console in a tabular format and generating the text-based Gantt chart.
  - Comparison table and Excel/CSV export (`utils.py`).

## Future Work
- Response time metric
- Preemptive Priority Scheduling
- Aging to prevent starvation
