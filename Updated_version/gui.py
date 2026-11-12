import io
import re
import contextlib
import tkinter as tk
from tkinter import ttk, messagebox

from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from process import Process
from main import load_processes, run_algorithm
from utils import calc_metrics, export_to_excel, export_comparison_to_excel


# Menüdeki seçimler, main.py'deki run_algorithm'in beklediği numaralarla eşleşir
ALGORITMALAR = {
    "FCFS (First-Come, First-Served)": "1",
    "SJF (Non-Preemptive)": "2",
    "SRTF (Preemptive)": "3",
    "Priority (Non-Preemptive)": "4",
    "Round Robin": "5",
    "Hepsini karşılaştır": "6",
}

# Her process için farklı renk, IDLE gri, CS sarı
PROCESS_RENKLERI = ["#4C78A8", "#F58518", "#54A24B", "#B279A2", "#E45756",
                    "#72B7B2", "#9D755D", "#FF9DA6", "#BAB0AC", "#EECA3B"]
IDLE_RENK = "#D0D0D0"
CS_RENK = "#F2CF5B"

ANSI_KODU = re.compile(r"\x1b\[[0-9;]*m")


def renk_sec(pid):
    if pid == "IDLE":
        return IDLE_RENK
    if pid == "CS":
        return CS_RENK
    return PROCESS_RENKLERI[hash(pid) % len(PROCESS_RENKLERI)]


def ciktiyi_yakala(fonksiyon, *args):
    # utils.py'deki kaydetme fonksiyonları sonucu print ile yazıyor.
    # O yazıyı yakalayıp pencerede gösteriyoruz (renk kodlarını temizleyerek).
    tampon = io.StringIO()
    with contextlib.redirect_stdout(tampon):
        fonksiyon(*args)
    return ANSI_KODU.sub("", tampon.getvalue()).strip()


class SchedulerArayuz(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CPU Scheduling Visualizer")
        self.geometry("1200x760")
        self.minsize(1000, 640)

        self.processler = []      # Kullanıcının girdiği orijinal Process listesi
        self.son_sonuc = None     # Excel'e kaydetmek için son çalıştırmanın sonucu

        self._sol_panel_olustur()
        self._sag_panel_olustur()
        self._process_yukle_dosyadan(sessiz=True)

    # ------------------------------------------------------------------ #
    # Sol panel: process listesi ve ayarlar
    # ------------------------------------------------------------------ #
    def _sol_panel_olustur(self):
        sol = ttk.Frame(self, padding=10)
        sol.pack(side=tk.LEFT, fill=tk.Y)

        # --- Process tablosu ---
        ttk.Label(sol, text="Process Listesi", font=("TkDefaultFont", 11, "bold")).pack(anchor="w")
        kolonlar = ("PID", "Arrival", "Burst", "Priority")
        self.process_tablo = ttk.Treeview(sol, columns=kolonlar, show="headings", height=10)
        for k in kolonlar:
            self.process_tablo.heading(k, text=k)
            self.process_tablo.column(k, width=70, anchor="center")
        self.process_tablo.pack(fill=tk.X, pady=(4, 6))

        # --- Yeni process girişi ---
        giris = ttk.Frame(sol)
        giris.pack(fill=tk.X)
        self.giris_kutulari = {}
        for i, ad in enumerate(kolonlar):
            ttk.Label(giris, text=ad).grid(row=0, column=i, padx=2)
            kutu = ttk.Entry(giris, width=8, justify="center")
            kutu.grid(row=1, column=i, padx=2)
            self.giris_kutulari[ad] = kutu
        self.giris_kutulari["Priority"].insert(0, "0")
        # Enter'a basınca da eklesin
        for kutu in self.giris_kutulari.values():
            kutu.bind("<Return>", lambda e: self._process_ekle())

        butonlar = ttk.Frame(sol)
        butonlar.pack(fill=tk.X, pady=6)
        ttk.Button(butonlar, text="Ekle", command=self._process_ekle).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(butonlar, text="Seçileni Sil", command=self._process_sil).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(butonlar, text="Temizle", command=self._process_temizle).pack(side=tk.LEFT, expand=True, fill=tk.X)
        ttk.Button(sol, text="input.txt dosyasından yükle",
                   command=self._process_yukle_dosyadan).pack(fill=tk.X)

        ttk.Separator(sol).pack(fill=tk.X, pady=12)

        # --- Algoritma ayarları ---
        ttk.Label(sol, text="Ayarlar", font=("TkDefaultFont", 11, "bold")).pack(anchor="w")
        ayar = ttk.Frame(sol)
        ayar.pack(fill=tk.X, pady=4)

        ttk.Label(ayar, text="Algoritma:").grid(row=0, column=0, sticky="w", pady=3)
        self.algoritma_secim = ttk.Combobox(ayar, values=list(ALGORITMALAR), state="readonly", width=28)
        self.algoritma_secim.current(0)
        self.algoritma_secim.grid(row=0, column=1, sticky="w", pady=3)
        self.algoritma_secim.bind("<<ComboboxSelected>>", lambda e: self._quantum_durumu())

        ttk.Label(ayar, text="Time quantum:").grid(row=1, column=0, sticky="w", pady=3)
        self.quantum_kutu = ttk.Spinbox(ayar, from_=1, to=100, width=6)
        self.quantum_kutu.set(2)
        self.quantum_kutu.grid(row=1, column=1, sticky="w", pady=3)

        ttk.Label(ayar, text="Context switch:").grid(row=2, column=0, sticky="w", pady=3)
        self.cs_kutu = ttk.Spinbox(ayar, from_=0, to=100, width=6)
        self.cs_kutu.set(0)
        self.cs_kutu.grid(row=2, column=1, sticky="w", pady=3)

        self._quantum_durumu()

        ttk.Button(sol, text="▶  Çalıştır", command=self._calistir).pack(fill=tk.X, pady=(10, 4), ipady=4)
        self.kaydet_buton = ttk.Button(sol, text="Excel'e kaydet", command=self._excele_kaydet, state="disabled")
        self.kaydet_buton.pack(fill=tk.X)

    # ------------------------------------------------------------------ #
    # Sağ panel: sonuç tablosu, ortalamalar ve Gantt şeması
    # ------------------------------------------------------------------ #
    def _sag_panel_olustur(self):
        sag = ttk.Frame(self, padding=10)
        sag.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.baslik = ttk.Label(sag, text="Sonuçlar", font=("TkDefaultFont", 12, "bold"))
        self.baslik.pack(anchor="w")

        self.sonuc_tablo = ttk.Treeview(sag, show="headings", height=8)
        self.sonuc_tablo.pack(fill=tk.X, pady=(4, 4))

        self.ozet = ttk.Label(sag, text="Bir algoritma seçip Çalıştır'a basın.", foreground="#2E7D32")
        self.ozet.pack(anchor="w", pady=(0, 6))

        # Matplotlib grafiği pencerenin içine gömülü
        self.figur = Figure(figsize=(8, 3.5), dpi=100)
        self.eksen = self.figur.add_subplot(111)
        self.tuval = FigureCanvasTkAgg(self.figur, master=sag)
        self.tuval.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        # Yakınlaştırma ve grafiği resim olarak kaydetme çubuğu
        NavigationToolbar2Tk(self.tuval, sag).update()
        self._bos_grafik()

    def _bos_grafik(self):
        self.eksen.clear()
        self.eksen.set_title("Gantt Chart")
        self.eksen.set_yticks([])
        self.eksen.set_xlabel("Zaman")
        self.tuval.draw()

    # ------------------------------------------------------------------ #
    # Process işlemleri
    # ------------------------------------------------------------------ #
    def _process_tablosunu_yenile(self):
        self.process_tablo.delete(*self.process_tablo.get_children())
        for p in sorted(self.processler, key=lambda p: p.pid):
            self.process_tablo.insert("", tk.END, iid=str(p.pid),
                                      values=(p.pid, p.arrival_time, p.burst_time, p.priority))
        # Bir sonraki PID'i otomatik öner
        self.giris_kutulari["PID"].delete(0, tk.END)
        sonraki = max((p.pid for p in self.processler), default=0) + 1
        self.giris_kutulari["PID"].insert(0, str(sonraki))

    def _process_ekle(self):
        try:
            pid = int(self.giris_kutulari["PID"].get())
            arrival = int(self.giris_kutulari["Arrival"].get())
            burst = int(self.giris_kutulari["Burst"].get())
            priority = int(self.giris_kutulari["Priority"].get() or 0)
        except ValueError:
            messagebox.showwarning("Geçersiz giriş", "Tüm alanlara tam sayı girin.")
            return

        if arrival < 0 or burst < 1 or priority < 0:
            messagebox.showwarning("Geçersiz giriş", "Arrival ≥ 0, Burst ≥ 1 ve Priority ≥ 0 olmalı.")
            return
        if any(p.pid == pid for p in self.processler):
            messagebox.showwarning("Geçersiz giriş", f"PID {pid} zaten var.")
            return

        self.processler.append(Process(pid, arrival, burst, priority))
        self._process_tablosunu_yenile()
        self.giris_kutulari["Arrival"].delete(0, tk.END)
        self.giris_kutulari["Burst"].delete(0, tk.END)
        self.giris_kutulari["Arrival"].focus_set()

    def _process_sil(self):
        secili = self.process_tablo.selection()
        if not secili:
            messagebox.showinfo("Bilgi", "Silmek için tablodan bir process seçin.")
            return
        silinecek = {int(iid) for iid in secili}
        self.processler = [p for p in self.processler if p.pid not in silinecek]
        self._process_tablosunu_yenile()

    def _process_temizle(self):
        self.processler = []
        self._process_tablosunu_yenile()

    def _process_yukle_dosyadan(self, sessiz=False):
        yuklenen = load_processes()
        if not yuklenen:
            if not sessiz:
                messagebox.showwarning("Dosya", "input.txt bulunamadı ya da içinde geçerli satır yok.")
            self._process_tablosunu_yenile()
            return
        self.processler = yuklenen
        self._process_tablosunu_yenile()

    # ------------------------------------------------------------------ #
    # Algoritmayı çalıştırma
    # ------------------------------------------------------------------ #
    def _quantum_durumu(self):
        # Quantum sadece Round Robin ve karşılaştırmada kullanılıyor
        secim = ALGORITMALAR[self.algoritma_secim.get()]
        self.quantum_kutu.configure(state="normal" if secim in ("5", "6") else "disabled")

    def _sayi_oku(self, kutu, ad, minimum):
        try:
            sayi = int(kutu.get())
        except ValueError:
            sayi = minimum - 1
        if sayi < minimum:
            messagebox.showwarning("Geçersiz giriş", f"{ad} en az {minimum} olmalı.")
            return None
        return sayi

    def _calistir(self):
        if not self.processler:
            messagebox.showwarning("Process yok", "Önce en az bir process ekleyin.")
            return

        secim = ALGORITMALAR[self.algoritma_secim.get()]
        cs_time = self._sayi_oku(self.cs_kutu, "Context switch", 0)
        if cs_time is None:
            return
        quantum = None
        if secim in ("5", "6"):
            quantum = self._sayi_oku(self.quantum_kutu, "Time quantum", 1)
            if quantum is None:
                return

        # run_algorithm her seferinde listenin kopyasıyla çalışıyor, orijinal bozulmuyor
        if secim == "6":
            sonuclar = [run_algorithm(c, self.processler, cs_time, quantum) for c in "12345"]
            self.son_sonuc = ("karsilastirma", sonuclar, cs_time, quantum)
            self._karsilastirma_goster(sonuclar)
        else:
            ad, procs, gantt = run_algorithm(secim, self.processler, cs_time, quantum)
            self.son_sonuc = ("tek", ad, procs, gantt)
            self._tek_sonuc_goster(ad, procs, gantt)

        self.kaydet_buton.configure(state="normal")

    def _tabloyu_hazirla(self, kolonlar, genislikler):
        self.sonuc_tablo.delete(*self.sonuc_tablo.get_children())
        self.sonuc_tablo.configure(columns=kolonlar)
        for k, g in zip(kolonlar, genislikler):
            self.sonuc_tablo.heading(k, text=k)
            self.sonuc_tablo.column(k, width=g, anchor="center")

    def _tek_sonuc_goster(self, ad, procs, gantt):
        self.baslik.configure(text=f"Sonuçlar — {ad}")
        self._tabloyu_hazirla(("PID", "Arrival", "Burst", "Priority", "Waiting", "Turnaround"),
                              (70, 80, 70, 80, 80, 100))
        for p in sorted(procs, key=lambda p: p.pid):
            self.sonuc_tablo.insert("", tk.END, values=(p.pid, p.arrival_time, p.burst_time,
                                                        p.priority, p.waiting_time, p.turnaround_time))

        m = calc_metrics(procs, gantt)
        self.ozet.configure(text=(f"Ortalama bekleme: {m['avg_wait']:.2f}    "
                                  f"Ortalama dönüş: {m['avg_tat']:.2f}    "
                                  f"CPU kullanımı: %{m['cpu_util']:.1f}    "
                                  f"Toplam süre: {m['total']}    CS sayısı: {m['cs_count']}"))

        self._gantt_ciz([(ad, gantt)], f"Gantt Chart — {ad}")

    def _karsilastirma_goster(self, sonuclar):
        self.baslik.configure(text="Algoritma Karşılaştırması")
        self._tabloyu_hazirla(("Algoritma", "Avg Wait", "Avg TAT", "CPU %", "Toplam", "CS"),
                              (200, 80, 80, 70, 70, 50))

        metrikler = [(ad, calc_metrics(procs, gantt)) for ad, procs, gantt in sonuclar]
        en_iyi = min(metrikler, key=lambda x: x[1]["avg_wait"])[0]
        self.sonuc_tablo.tag_configure("en_iyi", background="#DFF0D8")
        for ad, m in metrikler:
            self.sonuc_tablo.insert("", tk.END, tags=("en_iyi",) if ad == en_iyi else (),
                                    values=(ad, f"{m['avg_wait']:.2f}", f"{m['avg_tat']:.2f}",
                                            f"{m['cpu_util']:.1f}", m["total"], m["cs_count"]))

        self.ozet.configure(text=f"En düşük ortalama bekleme süresi: {en_iyi} (yeşil satır)")
        self._gantt_ciz([(ad, gantt) for ad, procs, gantt in sonuclar], "Gantt Chart — Tüm Algoritmalar")

    # ------------------------------------------------------------------ #
    # Gantt şeması
    # ------------------------------------------------------------------ #
    def _gantt_ciz(self, satirlar, baslik):
        # satirlar: [(satır adı, gantt listesi), ...]  Her algoritma bir satır olur
        self.eksen.clear()
        yukseklik = 0.6
        tek_satir = len(satirlar) == 1
        bitis = max((g[-1][2] for _, g in satirlar if g), default=0)

        for i, (ad, gantt) in enumerate(reversed(satirlar)):
            for pid, bas, son in gantt:
                self.eksen.broken_barh([(bas, son - bas)], (i - yukseklik / 2, yukseklik),
                                       facecolors=renk_sec(pid), edgecolor="black", linewidth=0.8,
                                       hatch="//" if pid == "IDLE" else None)
                etiket = pid if pid in ("IDLE", "CS") else f"P{pid}"
                # Blok çok darsa yazıyı sığdırmaya çalışma
                if (son - bas) / max(bitis, 1) > 0.025:
                    self.eksen.text((bas + son) / 2, i, etiket, ha="center", va="center",
                                    fontsize=9 if tek_satir else 8)

        self.eksen.set_yticks(range(len(satirlar)))
        self.eksen.set_yticklabels([] if tek_satir else [ad for ad, _ in reversed(satirlar)])
        self.eksen.set_ylim(-0.6, len(satirlar) - 0.4)
        self.eksen.set_xlim(0, max(bitis, 1))

        # Tek algoritmada her blok sınırını eksende göster (terminaldeki zaman çizgisi gibi)
        if tek_satir and satirlar[0][1]:
            sinirlar = sorted({0} | {t for _, b, s in satirlar[0][1] for t in (b, s)})
            self.eksen.set_xticks(sinirlar)
        self.eksen.set_xlabel("Zaman")
        self.eksen.set_title(baslik)
        self.eksen.grid(axis="x", linestyle=":", alpha=0.5)
        self.figur.tight_layout()
        self.tuval.draw()

    # ------------------------------------------------------------------ #
    # Excel'e kaydetme (utils.py'deki fonksiyonları kullanır)
    # ------------------------------------------------------------------ #
    def _excele_kaydet(self):
        if self.son_sonuc is None:
            return
        if self.son_sonuc[0] == "karsilastirma":
            _, sonuclar, cs_time, quantum = self.son_sonuc
            mesaj = ciktiyi_yakala(export_comparison_to_excel, sonuclar, cs_time, quantum)
        else:
            _, ad, procs, gantt = self.son_sonuc
            mesaj = ciktiyi_yakala(export_to_excel, procs, gantt, ad)

        if "kaydedilemedi" in mesaj:
            messagebox.showerror("Kaydetme hatası", mesaj)
        else:
            messagebox.showinfo("Kaydedildi", mesaj or "Sonuçlar kaydedildi.")


if __name__ == "__main__":
    SchedulerArayuz().mainloop()
