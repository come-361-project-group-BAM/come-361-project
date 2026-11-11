def priority_schedule(process_list, cs_time=0):
    processes = sorted(process_list, key=lambda p: p.arrival_time)
    current_time = 0
    completed = 0
    n = len(processes)
    gantt = []
    last_pid = None

    while completed != n:
        available = [p for p in processes if p.arrival_time <= current_time and p.remaining_time > 0]

        if not available:
            next_arrival = min(p.arrival_time for p in processes if p.remaining_time > 0)
            gantt.append(("IDLE", current_time, next_arrival))
            current_time = next_arrival
            continue

        # En düşük numara (Örn: 1), en yüksek önceliktir
        highest_priority = min(available, key=lambda p: (p.priority, p.arrival_time, p.pid))

        if cs_time > 0 and last_pid is not None and last_pid != highest_priority.pid:
            gantt.append(("CS", current_time, current_time + cs_time))
            current_time += cs_time

        start_time = current_time
        finish_time = start_time + highest_priority.burst_time

        highest_priority.waiting_time = start_time - highest_priority.arrival_time
        highest_priority.turnaround_time = finish_time - highest_priority.arrival_time
        highest_priority.remaining_time = 0

        gantt.append((highest_priority.pid, start_time, finish_time))
        current_time = finish_time
        last_pid = highest_priority.pid
        completed += 1

    return gantt
