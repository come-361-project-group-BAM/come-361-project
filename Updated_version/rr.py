def rr_schedule(process_list, quantum, cs_time=0):
    # quantum 0 veya negatif olursa döngü hiç bitmez, o yüzden baştan kontrol
    if quantum <= 0:
        raise ValueError("Time quantum 1 veya daha büyük olmalı")

    processes = sorted(process_list, key=lambda p: (p.arrival_time, p.pid))
    current_time = 0
    gantt = []
    queue = []
    idx = 0
    n = len(processes)
    last_pid = None

    # t=0'da gelmiş olanları kuyruğa al
    while idx < n and processes[idx].arrival_time <= current_time:
        queue.append(processes[idx])
        idx += 1

    while queue or idx < n:
        # Kuyruk boşsa bir sonraki işlem gelene kadar IDLE
        if not queue:
            next_arrival = processes[idx].arrival_time
            gantt.append(("IDLE", current_time, next_arrival))
            current_time = next_arrival
            while idx < n and processes[idx].arrival_time <= current_time:
                queue.append(processes[idx])
                idx += 1
            continue

        p = queue.pop(0)

        if cs_time > 0 and last_pid is not None and last_pid != p.pid:
            gantt.append(("CS", current_time, current_time + cs_time))
            current_time += cs_time
            # CS süresi geçerken yeni process geldiyse kuyruğa al
            while idx < n and processes[idx].arrival_time <= current_time:
                queue.append(processes[idx])
                idx += 1

        start_time = current_time
        run_time = min(p.remaining_time, quantum)
        current_time += run_time
        p.remaining_time -= run_time

        gantt.append((p.pid, start_time, current_time))
        last_pid = p.pid

        # Çalışırken gelenler, yarım kalan işlemden önce kuyruğa girer
        while idx < n and processes[idx].arrival_time <= current_time:
            queue.append(processes[idx])
            idx += 1

        if p.remaining_time > 0:
            queue.append(p)
        else:
            p.turnaround_time = current_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time

    return gantt
