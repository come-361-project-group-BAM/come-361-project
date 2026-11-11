# come-361-project
# CPU Scheduling Visualizer

This project is being developed to simulate and visualize various CPU scheduling algorithms as part of the Operating Systems course.

## Execution Instructions
Install the dependencies (`colorama` for colored output, `openpyxl` for Excel export), then run the main file:

`pip install -r requirements.txt`

`python3 main.py`

## Input Format (`input.txt`)
Each line describes one process: `PID Arrival Burst [Priority]`

```
1 0 8 2
2 1 4 1
```

The priority column is optional (default 0). A smaller number means a higher priority. Lines starting with `#` are ignored.

## Algorithms
1. FCFS (First-Come, First-Served)
2. SJF (Shortest Job First, non-preemptive)
3. SRTF (Shortest Remaining Time First, preemptive)
4. Priority Scheduling (non-preemptive)
5. Round Robin (time quantum is asked at runtime)
6. Compare all algorithms in a single table

An optional context switch delay can be entered at startup. Results can be appended to `rapor.xlsx` (saved next to `main.py`) and opened in Excel or Numbers. If `openpyxl` is missing, a `rapor.csv` is written instead.

## Task Distribution
- **Harun Görgün:** Set up the shared Git repository, prepared the `README.md`, designed the basic `Process` classes, and coded the Mini Demo (PoC) that reads data from the `input.txt` file into memory.
- **Beyza Arda:** Will integrate the logical skeleton of the FCFS (First-Come, First-Served) and SJF (Shortest Job First) scheduling algorithms into the Python simulation by the next submission.
- **Arda Çiçekli:** Will establish the structure for the Round Robin (RR) and Priority Scheduling algorithms and plan the time quantum management by the next submission.
- **Mehmethan Ünlü:** Will determine the libraries (e.g., Matplotlib or Tkinter) for rendering the results on the interface (such as Gantt Chart visualization) and design the visual output format by the next submission.
