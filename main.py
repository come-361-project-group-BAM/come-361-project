# main.py
import os
from process import Process

def main():
    process_list = []
    
    # input.txt dosyasını okuma simülasyonu
    if not os.path.exists("input.txt"):
        print("Hata: input.txt dosyası bulunamadı!")
        return

    with open("input.txt", "r") as file:
        for line in file:
            parts = line.strip().split()
            if len(parts) == 3:
                pid = int(parts[0])
                arrival = int(parts[1])
                burst = int(parts[2])
                
                # Process nesnesini oluşturup listeye ekleme
                p = Process(pid, arrival, burst)
                process_list.append(p)

    # Okunan verileri terminale yazdırma testi
    print("--- CPU Scheduling Visualizer: Mini Demo ---")
    print(f"Dosyadan okunan Process sayısı: {len(process_list)}")
    print("PID\tGeliş(Arrival)\tSüre(Burst)")
    print("-" * 40)
    
    for p in process_list:
        print(f"{p.pid}\t{p.arrival_time}\t\t{p.burst_time}")

if __name__ == "__main__":
    main()