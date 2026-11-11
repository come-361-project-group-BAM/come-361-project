def sjf_schedule(process_list, cs_time=0):
    processes = sorted(process_list, key=lambda p: (p.arrival_time, p.pid))
    current_time = 0
    completed = 0
    n = len(processes)
    gantt = []
    last_pid = None

    while completed != n:
        available = [p for p in processes if p.arrival_time <= current_time and p.remaining_time > 0]

        # Hazır işlem yoksa bir sonraki geliş zamanına kadar IDLE
        if not available:
            next_arrival = min(p.arrival_time for p in processes if p.remaining_time > 0)
            gantt.append(("IDLE", current_time, next_arrival))
            current_time = next_arrival
            continue

        # Burst süresi en kısa olan seçilir, eşitlikte önce gelen
        shortest = min(available, key=lambda p: (p.burst_time, p.arrival_time, p.pid))

        if cs_time > 0 and last_pid is not None and last_pid != shortest.pid:
            gantt.append(("CS", current_time, current_time + cs_time))
            current_time += cs_time

        start_time = current_time
        finish_time = start_time + shortest.burst_time

        shortest.waiting_time = start_time - shortest.arrival_time
        shortest.turnaround_time = finish_time - shortest.arrival_time
        shortest.remaining_time = 0

        gantt.append((shortest.pid, start_time, finish_time))
        current_time = finish_time
        last_pid = shortest.pid
        completed += 1

    return gantt
