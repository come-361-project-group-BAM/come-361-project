def fcfs_schedule(process_list, cs_time=0):
    processes = sorted(process_list, key=lambda p: (p.arrival_time, p.pid))
    current_time = 0
    gantt = []
    last_pid = None

    for p in processes:
        # Process henüz gelmediyse CPU boşta bekler
        if current_time < p.arrival_time:
            gantt.append(("IDLE", current_time, p.arrival_time))
            current_time = p.arrival_time

        # Daha önce çalışan farklı bir işlemden geçiyorsak araya CS ekle
        if cs_time > 0 and last_pid is not None and last_pid != p.pid:
            gantt.append(("CS", current_time, current_time + cs_time))
            current_time += cs_time

        start = current_time
        finish = start + p.burst_time

        p.waiting_time = start - p.arrival_time
        p.turnaround_time = finish - p.arrival_time
        p.remaining_time = 0

        gantt.append((p.pid, start, finish))
        current_time = finish
        last_pid = p.pid

    return gantt
