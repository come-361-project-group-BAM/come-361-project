import os
import copy
from process import Process
from utils import print_results, print_comparison, export_to_excel, export_comparison_to_excel
from fcfs import fcfs_schedule
from sjf import sjf_schedule
from srtf import srtf_schedule
from priority import priority_schedule
from rr import rr_schedule


def load_processes(filename="input.txt"):
    # input.txt programla aynı klasörde aranır, terminal başka klasörde açık olsa da çalışsın
    filename = os.path.join(os.path.dirname(os.path.abspath(__file__)), filename)
    if not os.path.exists(filename):
        print(f"Hata: {filename} bulunamadı!")
        return []

    processes = []
    kullanilan_pidler = set()
    with open(filename, "r") as file:
        for line_no, line in enumerate(file, 1):
            line = line.strip()
            # Boş satırları ve # ile başlayan yorum satırlarını atla
            if not line or line.startswith("#"):
                continue

            try:
                parts = [int(x) for x in line.split()]
            except ValueError:
                print(f"Uyarı: {line_no}. satırda sayı olmayan değer var, atlandı: '{line}'")
                continue

            if len(parts) < 3:
                print(f"Uyarı: {line_no}. satırda en az 3 değer olmalı, atlandı: '{line}'")
                continue

            pid, arrival, burst = parts[0], parts[1], parts[2]
            # 4. sütun (priority) yoksa varsayılan 0 ata
            priority = parts[3] if len(parts) > 3 else 0

            if burst <= 0 or arrival < 0:
                print(f"Uyarı: {line_no}. satır geçersiz (burst > 0, arrival >= 0 olmalı), atlandı: '{line}'")
                continue
            if pid in kullanilan_pidler:
                print(f"Uyarı: {line_no}. satırdaki PID {pid} daha önce kullanılmış, atlandı.")
                continue

            kullanilan_pidler.add(pid)
            processes.append(Process(pid, arrival, burst, priority))
    return processes


def read_int(mesaj, minimum=0):
    # Geçerli bir sayı girilene kadar tekrar sor
    while True:
        try:
            sayi = int(input(mesaj).strip())
            if sayi >= minimum:
                return sayi
        except ValueError:
            pass
        print(f"Lütfen en az {minimum} olan bir tam sayı girin.")


def read_processes_from_user():
    # PID'leri otomatik veriyoruz (1, 2, 3...), kullanıcı geri kalanını girer
    n = read_int("Kaç process girilecek? (en az 1): ", 1)
    processes = []
    for pid in range(1, n + 1):
        print(f"\n--- P{pid} ---")
        arrival = read_int("Geliş zamanı (Arrival): ", 0)
        burst = read_int("Çalışma süresi (Burst, en az 1): ", 1)
        priority = read_int("Öncelik (küçük sayı = yüksek öncelik, yoksa 0): ", 0)
        processes.append(Process(pid, arrival, burst, priority))
    return processes


def ask_int(mesaj, varsayilan, minimum=0):
    # Geçersiz giriş olursa program çökmesin, varsayılan değer kullanılsın
    try:
        sayi = int(input(mesaj).strip())
        if sayi >= minimum:
            return sayi
    except ValueError:
        pass
    print(f"Geçersiz giriş, varsayılan değer kullanıldı: {varsayilan}")
    return varsayilan


def run_algorithm(choice, original_procs, cs_time, quantum=None):
    # Her seferinde listenin kopyasıyla çalış ki süreler baştan hesaplansın
    procs = copy.deepcopy(original_procs)

    if choice == '1':
        return "FCFS", procs, fcfs_schedule(procs, cs_time)
    if choice == '2':
        return "SJF (Non-Preemptive)", procs, sjf_schedule(procs, cs_time)
    if choice == '3':
        return "SRTF (Preemptive)", procs, srtf_schedule(procs, cs_time)
    if choice == '4':
        return "Priority (Non-Preemptive)", procs, priority_schedule(procs, cs_time)
    return f"Round Robin (q={quantum})", procs, rr_schedule(procs, quantum, cs_time)


def main():
    print("--- CPU Scheduling Visualizer Kurulumu ---")
    print("1. Process'leri input.txt dosyasından oku")
    print("2. Process'leri elle gir")
    kaynak = input("Seçiminiz (varsayılan 1): ").strip()

    if kaynak == '2':
        original_procs = read_processes_from_user()
    else:
        original_procs = load_processes()
    if not original_procs:
        return

    # Program başında Context Switch süresini bir kere sor
    cs_time = ask_int("Context Switch gecikmesi (ms) eklensin mi? (Yoksa 0 girin): ", 0, 0)

    while True:
        print("\n" + "=" * 52)
        print("1. FCFS (First-Come, First-Served)")
        print("2. SJF  (Shortest Job First - Non-Preemptive)")
        print("3. SRTF (Shortest Remaining Time First - Preemptive)")
        print("4. Priority (Non-Preemptive, küçük sayı = yüksek öncelik)")
        print("5. Round Robin")
        print("6. Hepsini karşılaştır")
        print("0. Çıkış")
        print("=" * 52)

        choice = input("Çalıştırmak istediğiniz algoritmayı seçin: ").strip()
        if choice == '0':
            print("Sistemden çıkılıyor...")
            break
        if choice not in ('1', '2', '3', '4', '5', '6'):
            print("Geçersiz seçim, tekrar deneyin.")
            continue

        # Round Robin için time quantum lazım
        quantum = None
        if choice in ('5', '6'):
            quantum = ask_int("Time quantum değeri (en az 1): ", 2, 1)

        # Hepsini sırayla çalıştırıp karşılaştırma tablosu yazdır
        if choice == '6':
            results = [run_algorithm(c, original_procs, cs_time, quantum) for c in '12345']
            print_comparison(results)

            save = input("Bu karşılaştırmayı Excel dosyasına kaydetmek ister misiniz? (E/H): ").strip().upper()
            if save == 'E':
                export_comparison_to_excel(results, cs_time, quantum)
            continue

        algo_name, procs, chart = run_algorithm(choice, original_procs, cs_time, quantum)

        # Sonuçları renkli olarak terminale çizdir (Mehmethan'ın modülü)
        print_results(procs, chart, algo_name)

        # Excel kaydetme menüsü
        save = input("Bu sonuçları Excel dosyasına kaydetmek ister misiniz? (E/H): ").strip().upper()
        if save == 'E':
            export_to_excel(procs, chart, algo_name)


if __name__ == "__main__":
    main()
