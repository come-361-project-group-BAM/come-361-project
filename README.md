# come-361-project
# CPU Scheduling Visualizer

This project is being developed to simulate and visualize various CPU scheduling algorithms as part of the Operating Systems course.

## Execution Instructions
To run the system, simply execute the main Python file directly via the terminal:
`python3 main.py`

## Task Distribution
- **Harun Görgün:** Algorithm Design and Development: Responsible for coding the core logic (fcfs_schedule) of the First-Come, First-Served (FCFS) algorithm in the fcfs.py file. Handles the calculation of CPU idle times, process waiting times, and turnaround times.   

- **Beyza Arda:** Data Models & Core Architecture: Responsible for creating the fundamental data structures in the process.py file. Designs the Process class (PID, arrival time, burst time, etc.) and the skeleton Scheduler class for future algorithms.   

- **Arda Çiçekli:** System Integration & File I/O: Responsible for developing the main.py file that manages the main execution flow of the simulation. Handles parsing and reading process data from the input.txt file, performing missing file checks, and feeding the objects into the algorithm.   

- **Mehmethan Ünlü:**  Visualization & Reporting: Responsible for designing the print_results function within fcfs.py. Handles printing the algorithm metrics to the console in a tabular format and generating the text-based Gantt Chart to visualize the execution timeline of the processes.   
