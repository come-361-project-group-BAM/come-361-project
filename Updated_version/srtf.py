def srtf_schedule(process_list, cs_time=0):
    current_time = 0
    completed = 0
    n = len(process_list)
    gantt = []
    last_pid = None

    while completed != n:
        available = [p for p in process_list if p.arrival_time <= current_time and p.remaining_time > 0]

        if not available:
            next_arrival = min(p.arrival_time for p in process_list if p.remaining_time > 0)
            gantt.append(("IDLE", current_time, next_arrival))
            current_time = next_arrival
            continue

        shortest = min(available, key=lambda p: (p.remaining_time, p.arrival_time, p.pid))

        # Başka bir işleme geçiyorsak araya CS ekle
        cs_eklendi = False
        if cs_time > 0 and last_pid is not None and last_pid != shortest.pid:
            gantt.append(("CS", current_time, current_time + cs_time))
            current_time += cs_time
            cs_eklendi = True

        # Bir sonraki işlem gelene kadar ya da işlem bitene kadar çalıştır
        # (her birimi tek tek ilerletmeye gerek yok, sadece bu noktalarda karar değişir)
        future = [p.arrival_time for p in process_list if p.remaining_time > 0 and p.arrival_time > current_time]
        run_time = shortest.remaining_time
        if future:
            run_time = min(run_time, min(future) - current_time)

        # CS sırasında yeni işlem gelmiş olabilir, 1 birim çalışıp durumu tekrar kontrol et
        if cs_eklendi:
            run_time = 1

        # Aynı işlem peş peşe çalışıyorsa Gantt'ta tek blok yap
        if gantt and gantt[-1][0] == shortest.pid and gantt[-1][2] == current_time:
            gantt[-1] = (shortest.pid, gantt[-1][1], current_time + run_time)
        else:
            gantt.append((shortest.pid, current_time, current_time + run_time))

        shortest.remaining_time -= run_time
        current_time += run_time
        last_pid = shortest.pid

        if shortest.remaining_time == 0:
            shortest.turnaround_time = current_time - shortest.arrival_time
            shortest.waiting_time = shortest.turnaround_time - shortest.burst_time
            completed += 1

    return gantt
