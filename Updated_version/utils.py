import os
import csv

# colorama yüklü değilse program çökmesin, renksiz çalışsın
try:
    from colorama import init, Fore, Style
    # Windows dahil tüm terminallerde renklerin düzgün çalışması için
    init(autoreset=True)
except ImportError:
    class _RenksizStil:
        def __getattr__(self, name):
            return ""
    Fore = Style = _RenksizStil()

# Çok uzun süreli işlemler Gantt satırını terminalden taşırmasın
MAX_BLOK_GENISLIK = 24


def calc_metrics(process_list, gantt):
    n = len(process_list)
    avg_wait = sum(p.waiting_time for p in process_list) / n if n > 0 else 0
    avg_tat = sum(p.turnaround_time for p in process_list) / n if n > 0 else 0

    # IDLE ve CS blokları CPU'nun işe yaradığı süreye dahil değil
    total = gantt[-1][2] if gantt else 0
    busy = sum(end - start for pid, start, end in gantt if pid not in ("IDLE", "CS"))
    cs_count = sum(1 for pid, start, end in gantt if pid == "CS")
    cpu_util = busy / total * 100 if total > 0 else 0

    return {"avg_wait": avg_wait, "avg_tat": avg_tat, "total": total,
            "cpu_util": cpu_util, "cs_count": cs_count}


def print_results(process_list, gantt, algo_name="Sonuçlar"):
    print(f"\n{Fore.CYAN}{Style.BRIGHT}=== {algo_name} CPU Scheduling ==={Style.RESET_ALL}")
    print(f"{'PID':<6}{'Arrival':<10}{'Burst':<8}{'Priority':<10}{'Waiting':<10}{'Turnaround':<12}")
    print("-" * 56)

    for p in sorted(process_list, key=lambda p: p.pid):
        print(f"{p.pid:<6}{p.arrival_time:<10}{p.burst_time:<8}{p.priority:<10}"
              f"{p.waiting_time:<10}{p.turnaround_time:<12}")

    if len(process_list) > 0:
        m = calc_metrics(process_list, gantt)
        print("-" * 56)
        print(f"{Fore.GREEN}Ortalama Bekleme Süresi   : {m['avg_wait']:.2f}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}Ortalama Dönüş Süresi     : {m['avg_tat']:.2f}{Style.RESET_ALL}")
        print(f"{Fore.GREEN}CPU Kullanımı             : %{m['cpu_util']:.1f} "
              f"(Toplam süre: {m['total']}, CS sayısı: {m['cs_count']}){Style.RESET_ALL}")

    # Renkli ve Dinamik Gantt Chart
    print(f"\n{Fore.CYAN}{Style.BRIGHT}=== Gantt Chart ==={Style.RESET_ALL}")
    bar, timeline = "|", ""
    for pid, start, end in gantt:
        if pid == "IDLE":
            label = "IDLE"
            color = Fore.RED
        elif pid == "CS":
            label = "CS"
            color = Fore.YELLOW
        else:
            label = f"P{pid}"
            color = Fore.BLUE

        width = max(len(label) + 2, min((end - start) * 2, MAX_BLOK_GENISLIK))
        # Hizalamayı saf metinle yapıp, rengi üzerine sarıyoruz
        colored_label = f"{color}{label.center(width)}{Style.RESET_ALL}"
        bar += colored_label + "|"
        # Rakam blok genişliğinden uzunsa yanındakiyle birleşmesin
        timeline += str(start).ljust(max(width + 1, len(str(start)) + 1))

    timeline += str(gantt[-1][2]) if gantt else ""
    print(bar)
    print(timeline)
    print("\n")


def print_comparison(results):
    # results: [(algoritma adı, process listesi, gantt), ...]
    print(f"\n{Fore.CYAN}{Style.BRIGHT}=== Algoritma Karşılaştırması ==={Style.RESET_ALL}")
    print(f"{'Algoritma':<28}{'Avg Wait':<11}{'Avg TAT':<11}{'CPU %':<9}{'Toplam':<8}{'CS':<4}")
    print("-" * 71)

    best = min(results, key=lambda r: calc_metrics(r[1], r[2])["avg_wait"])[0]
    for name, procs, gantt in results:
        m = calc_metrics(procs, gantt)
        line = (f"{name:<28}{m['avg_wait']:<11.2f}{m['avg_tat']:<11.2f}"
                f"{m['cpu_util']:<9.1f}{m['total']:<8}{m['cs_count']:<4}")
        # En iyi ortalama bekleme süresine sahip satırı yeşil yap
        print(f"{Fore.GREEN}{line}{Style.RESET_ALL}" if name == best else line)

    print(f"\n{Fore.GREEN}En düşük ortalama bekleme süresi: {best}{Style.RESET_ALL}\n")


# Raporlar programın bulunduğu klasöre kaydedilir (hangi klasörden çalıştırılırsa çalıştırılsın aynı yer)
RAPOR_KLASORU = os.path.dirname(os.path.abspath(__file__))


def _rapor_dosyasi_ac(path):
    # Dosya varsa aç, yoksa oluştur. Eksik sayfaları (Sonuçlar, Karşılaştırma) başlıklarıyla ekler
    from openpyxl import Workbook, load_workbook
    from openpyxl.styles import Font

    sayfalar = {
        "Sonuçlar": (["Algoritma", "PID", "Arrival", "Burst", "Priority", "Waiting", "Turnaround"],
                     [28, 10, 10, 10, 10, 10, 12]),
        "Karşılaştırma": (["Algoritma", "Avg Wait", "Avg TAT", "CPU %", "Toplam Süre", "CS Sayısı", "CS Süresi", "Quantum"],
                          [28, 11, 11, 9, 13, 11, 11, 9]),
    }

    if os.path.isfile(path):
        wb = load_workbook(path)
    else:
        wb = Workbook()
        wb.remove(wb.active)

    for ad, (baslik, genislikler) in sayfalar.items():
        if ad in wb.sheetnames:
            continue
        ws = wb.create_sheet(ad)
        ws.append(baslik)
        for hucre in ws[1]:
            hucre.font = Font(bold=True)
        for i, genislik in enumerate(genislikler):
            ws.column_dimensions[chr(ord("A") + i)].width = genislik
    return wb


def _kaydet(wb, path, filename):
    try:
        wb.save(path)
    except PermissionError:
        print(f"{Fore.RED}Dosya kaydedilemedi, '{filename}' başka bir programda açık olabilir. Kapatıp tekrar deneyin.{Style.RESET_ALL}")
        return
    print(f"{Fore.GREEN}Sonuçlar şu dosyaya eklendi: {path}{Style.RESET_ALL}")


def export_to_excel(process_list, gantt, algo_name, filename="rapor.xlsx"):
    try:
        from openpyxl.styles import Font
        path = os.path.join(RAPOR_KLASORU, filename)
        wb = _rapor_dosyasi_ac(path)
    except ImportError:
        # openpyxl yoksa CSV'ye düş
        print(f"{Fore.YELLOW}openpyxl yüklü değil, CSV olarak kaydediliyor.{Style.RESET_ALL}")
        export_to_csv(process_list, gantt, algo_name)
        return

    ws = wb["Sonuçlar"]
    for p in sorted(process_list, key=lambda p: p.pid):
        ws.append([algo_name, p.pid, p.arrival_time, p.burst_time, p.priority, p.waiting_time, p.turnaround_time])

    if len(process_list) > 0:
        m = calc_metrics(process_list, gantt)
        ws.append([algo_name, "ORTALAMA", "-", "-", "-", round(m["avg_wait"], 2), round(m["avg_tat"], 2)])
        for hucre in ws[ws.max_row]:
            hucre.font = Font(bold=True)
    ws.append([])  # Algoritmalar arasına boşluk bırak

    _kaydet(wb, path, filename)


def export_comparison_to_excel(results, cs_time, quantum, filename="rapor.xlsx"):
    # results: [(algoritma adı, process listesi, gantt), ...]
    try:
        path = os.path.join(RAPOR_KLASORU, filename)
        wb = _rapor_dosyasi_ac(path)
    except ImportError:
        # openpyxl yoksa CSV'ye düş
        print(f"{Fore.YELLOW}openpyxl yüklü değil, CSV olarak kaydediliyor.{Style.RESET_ALL}")
        csv_yolu = os.path.join(RAPOR_KLASORU, "rapor_karsilastirma.csv")
        yeni_dosya = not os.path.isfile(csv_yolu)
        with open(csv_yolu, mode='a', newline='', encoding='utf-8-sig') as file:
            writer = csv.writer(file, delimiter=';')
            if yeni_dosya:
                writer.writerow(["Algoritma", "Avg Wait", "Avg TAT", "CPU %", "Toplam Süre", "CS Sayısı", "CS Süresi", "Quantum"])
            for name, procs, gantt in results:
                m = calc_metrics(procs, gantt)
                writer.writerow([name, f"{m['avg_wait']:.2f}", f"{m['avg_tat']:.2f}",
                                 f"{m['cpu_util']:.1f}", m["total"], m["cs_count"], cs_time, quantum])
            writer.writerow([])
        print(f"{Fore.GREEN}Karşılaştırma şu dosyaya eklendi: {csv_yolu}{Style.RESET_ALL}")
        return

    ws = wb["Karşılaştırma"]
    for name, procs, gantt in results:
        m = calc_metrics(procs, gantt)
        ws.append([name, round(m["avg_wait"], 2), round(m["avg_tat"], 2), round(m["cpu_util"], 1),
                   m["total"], m["cs_count"], cs_time, quantum])
    ws.append([])  # Çalıştırmalar arasına boşluk bırak

    _kaydet(wb, path, filename)


def export_to_csv(process_list, gantt, algo_name, filename="rapor.csv"):
    filename = os.path.join(RAPOR_KLASORU, filename)
    file_exists = os.path.isfile(filename)

    # utf-8-sig: Excel'de Türkçe karakterler bozulmadan açılsın
    with open(filename, mode='a', newline='', encoding='utf-8-sig') as file:
        # Türkçe Excel'de sütunlar noktalı virgülle ayrılır
        writer = csv.writer(file, delimiter=';')
        if not file_exists:
            writer.writerow(["Algoritma", "PID", "Arrival", "Burst", "Priority", "Waiting", "Turnaround"])

        for p in sorted(process_list, key=lambda p: p.pid):
            writer.writerow([algo_name, p.pid, p.arrival_time, p.burst_time, p.priority, p.waiting_time, p.turnaround_time])

        if len(process_list) > 0:
            m = calc_metrics(process_list, gantt)
            writer.writerow([algo_name, "ORTALAMA", "-", "-", "-", f"{m['avg_wait']:.2f}", f"{m['avg_tat']:.2f}"])
        writer.writerow([])  # Algoritmalar arasına boşluk bırak

    print(f"{Fore.GREEN}Sonuçlar '{filename}' dosyasına başarıyla eklendi! (Excel ile açabilirsiniz){Style.RESET_ALL}")
