# fcfs.py
# First-Come, First-Served (FCFS) CPU Scheduling Algoritması

from process import Process


def fcfs_schedule(process_list):
    """
    FCFS algoritmasını çalıştırır.

    Parametre:
        process_list: Process nesnelerinden oluşan liste

    Döndürür:
        gantt: [(pid, başlangıç, bitiş), ...] şeklinde Gantt Chart verisi
               (CPU'nun boş kaldığı aralıklar için pid = "IDLE")
    """
    # Geliş zamanına göre sırala (eşitlikte PID sırası)
    processes = sorted(process_list, key=lambda p: (p.arrival_time, p.pid))

    current_time = 0
    gantt = []

    for p in processes:
        # Process henüz gelmediyse CPU boşta bekler
        if current_time < p.arrival_time:
            gantt.append(("IDLE", current_time, p.arrival_time))
            current_time = p.arrival_time

        start_time = current_time
        finish_time = start_time + p.burst_time

        # Metrikleri hesapla
        p.waiting_time = start_time - p.arrival_time
        p.turnaround_time = finish_time - p.arrival_time
        p.remaining_time = 0

        gantt.append((p.pid, start_time, finish_time))
        current_time = finish_time

    return gantt


def print_results(process_list, gantt):
    """Sonuç tablosunu, ortalamaları ve metin tabanlı Gantt Chart'ı yazdırır."""
    print("\n=== FCFS Sonuçları ===")
    print(f"{'PID':<6}{'Arrival':<10}{'Burst':<8}{'Waiting':<10}{'Turnaround':<12}")
    print("-" * 46)

    for p in sorted(process_list, key=lambda p: p.pid):
        print(f"{p.pid:<6}{p.arrival_time:<10}{p.burst_time:<8}"
              f"{p.waiting_time:<10}{p.turnaround_time:<12}")

    n = len(process_list)
    if n > 0:
        avg_wait = sum(p.waiting_time for p in process_list) / n
        avg_tat = sum(p.turnaround_time for p in process_list) / n
        print("-" * 46)
        print(f"Ortalama Bekleme Süresi (Avg Waiting)   : {avg_wait:.2f}")
        print(f"Ortalama Dönüş Süresi (Avg Turnaround)  : {avg_tat:.2f}")

    # Metin tabanlı Gantt Chart
    print("\n=== Gantt Chart ===")
    bar = "|"
    timeline = ""
    for pid, start, end in gantt:
        label = "IDLE" if pid == "IDLE" else f"P{pid}"
        width = max(len(label) + 2, (end - start) * 2)
        bar += label.center(width) + "|"
        timeline += str(start).ljust(width + 1)
    timeline += str(gantt[-1][2]) if gantt else ""
    print(bar)
    print(timeline)


def load_processes(filename="input.txt"):
    """input.txt dosyasından (pid arrival burst) Process listesi okur."""
    processes = []
    with open(filename, "r") as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) == 3:
                processes.append(Process(int(parts[0]), int(parts[1]), int(parts[2])))
    return processes


if __name__ == "__main__":
    procs = load_processes()
    chart = fcfs_schedule(procs)
    print_results(procs, chart)
