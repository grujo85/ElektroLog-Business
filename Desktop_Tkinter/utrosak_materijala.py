import streamlit as st  # Glavna biblioteka za Web interfejs
import sqlite3          # Baza ostaje ista
import pandas as pd     # Za lakši prikaz tabela na webu
from datetime import datetime
import os
import base64
-----------------------------------------------------------------------------------------------------
UKLONI NA SVOM DESTOPU KOMENTARE I OBRISI GORNJI UNOS
#import tkinter as tk  # Uvoz glavne biblioteke za grafički interfejs
#from tkinter import ttk, messagebox, filedialog  # Uvoz dodatnih vidžeta, dijaloga i birača fajlova
#from datetime import datetime  # Uvoz biblioteke za rad sa datumom i vremenom
#import webbrowser  # Uvoz biblioteke za automatsko otvaranje internet pregledača
#import os  # Uvoz biblioteke za rad sa sistemskim putanjama i fajlovima
#import sqlite3  # Uvoz biblioteke za rad sa SQLite bazom podataka
#import shutil  # Uvoz biblioteke za kopiranje fajlova (korišćeno za backup/restore)
#import base64  # Uvoz biblioteke za enkodiranje slika u tekstualni format
------------------------------------------------------------------------------------------------------

class ElektroProUltra:  # Definicija glavne klase aplikacije
    def __init__(self, root):  # Konstruktor klase koji inicijalizuje glavni prozor
        self.root = root  # Dodela korenskog prozora varijabli unutar klase
        self.root.title("ELEKTRO-LOG BUSINESS v1.0")  # Postavljanje naslova prozora
        self.root.geometry("1250x850")  # Definisanje početne rezolucije prozora
        self.root.configure(bg="#f0f2f5")  # Postavljanje boje pozadine glavnog prozora
        
        self.db_name = "elektro_baza.db"  # Definisanje naziva fajla baze podataka
        self.putanja_logotipa = "/home/vlade/elmar.webp"  # Putanja do slike logotipa na disku
        self.logo_data = self.ucitaj_logo_u_base64()  # Poziv funkcije za pretvaranje slike u Base64 kod
        self.edit_id = None  # Inicijalizacija varijable koja čuva ID reda koji se menja (None ako je novi unos)
        
        self.tipovi = [  # Lista svih dostupnih materijala u padajućem meniju
            # Nosači i oprema
            "Brezon M8", "Brezon M10", "C-šina 30x20", "C-šina 41x21", 
            "Regal 50", "Regal 100", "Regal 150", "Regal 200", "Regal 300", "Regal 400", "Regal 500", "Regal 600",
            "LR Krivina", "LR T-komad", "Poklopac regala",
            
            # Instalacioni kablovi (PP-Y / NYM)
            "PP-Y 2x1.5", "PP-Y 3x1.5", "PP-Y 3x2.5", "PP-Y 3x4", "PP-Y 4x1.5", "PP-Y 4x2.5", "PP-Y 4x4",
            "PP-Y 5x1.5", "PP-Y 5x2.5", "PP-Y 5x4", "PP-Y 5x6", "PP-Y 5x10", "PP-Y 5x16",
            
            # Bezhalogeni kablovi (N2XH)
            "N2XH-J 3x1.5", "N2XH-J 3x2.5", "N2XH-J 3x4", "N2XH-J 5x1.5", "N2XH-J 5x2.5", "N2XH-J 5x4",
            "N2XH-J 5x6", "N2XH-J 5x10", "N2XH-J 5x16", "N2XH-J 5x25", "N2XH-J 5x35", "N2XH-J 5x50",
            
            # Vatrootporni kablovi (FE180)
            "NHXH FE180 3x1.5", "NHXH FE180 3x2.5", "NHXH FE180 5x1.5", "NHXH FE180 5x2.5", "NHXH FE180 5x4", "NHXH FE180 5x6",
            
            # Energetski kablovi (PP00 / NYY)
            "PP00 3x1.5", "PP00 3x2.5", "PP00 4x1.5", "PP00 4x2.5", "PP00 4x4", "PP00 4x6", "PP00 4x10",
            "PP00 4x16", "PP00 4x25", "PP00 4x35", "PP00 4x50", "PP00 4x70", "PP00 4x95", "PP00 4x120",
            "PP00 4x150", "PP00 4x185", "PP00 4x240", "PP00 5x1.5", "PP00 5x2.5", "PP00 5x4", "PP00 5x6",
            "PP00 5x10", "PP00 5x16", 
            
            # Aluminijumski kablovi (PP00-A / NAYY)
            "PP00-A (Al) 4x16", "PP00-A 4x25", "PP00-A 4x35", "PP00-A 4x50", 
            "PP00-A 4x70", "PP00-A 4x95", "PP00-A 4x120", "PP00-A 4x150", "PP00-A 4x240",
            
            # Gumeni kablovi (H07RN-F)
            "H07RN-F (GG/J) 3x1.5", "H07RN-F 3x2.5", "H07RN-F 5x1.5", "H07RN-F 5x2.5", "H07RN-F 5x4", 
            "H07RN-F 5x6", "H07RN-F 5x10", "H07RN-F 5x16", 
            
            # Signalni i kontrolni (LiYCY)
            "LiYCY 2x0.75", "LiYCY 3x0.75", "LiYCY 4x0.75", "LiYCY 5x0.75", "LiYCY 7x0.75", "LiYCY 12x0.75",
            
            # Provodnici (P, P/F)
            "P/F (H07V-K) 0.75", "P/F 1.5", "P/F 2.5", "P/F 4", "P/F 6", "P/F 10", "P/F 16", "P/F 25", "P/F 35", "P/F 50",
            "P (H07V-U) 1.5", "P 2.5", "P 4", "P 6", 
            
            # Vazdušni snop (SKS) i specijalni
            "SKS 2x16", "SKS 4x16", "SKS 4x25",
            "UTP Cat5e", "FTP Cat6", "SFTP Cat7", "Koaksijalni RG6", "Koaksijalni RG11",
            "Alarmni 4x0.22", "Alarmni 6x0.22", "Alarmni 8x0.22", "JH(St)H 2x2x0.8", "JH(St)H 4x2x0.8",
            "Solarni 4mm2", "Solarni 6mm2"
        ]

        self.kreiraj_bazu()  # Pozivanje funkcije za inicijalno kreiranje tabele u bazi

        self.main = tk.Frame(root, bg="#f0f2f5", padx=30, pady=20)  # Kreiranje glavnog okvira sa marginama
        self.main.pack(fill="both", expand=True)  # Postavljanje okvira da popuni sav prostor

        tk.Label(self.main, text="ELEKTRO-LOG BUSINESS SPECIFIKACIJA",   # Glavni naslov aplikacije
                 font=("Segoe UI", 20, "bold"), fg="#2d3748", bg="#f0f2f5").pack(pady=(0,15)) # Stil i razmak naslova

        self.f_unos = tk.Frame(self.main, bg="white", padx=20, pady=20, relief="flat", highlightthickness=1, highlightbackground="#e2e8f0") # Beli okvir za formu
        self.f_unos.pack(fill="x")  # Postavljanje okvira za unos da se širi horizontalno

        def labela(text, r, c):  # Interna pomoćna funkcija za kreiranje tekstualnih labela u formi
            tk.Label(self.f_unos, text=text, font=("Segoe UI", 9, "bold"), bg="white", fg="#4a5568").grid(row=r, column=c, sticky="w", pady=5, padx=5) # Grid pozicioniranje

        labela("Datum:", 0, 0); self.e_dat = tk.Entry(self.f_unos, font=("Segoe UI", 11), bd=1, relief="solid"); self.e_dat.grid(row=0, column=1, sticky="we", padx=10); self.e_dat.insert(0, datetime.now().strftime("%d.%m.%Y")) # Polje za datum
        labela("Orman (RO):", 0, 2); self.e_orm = tk.Entry(self.f_unos, font=("Segoe UI", 11), bd=1, relief="solid"); self.e_orm.grid(row=0, column=3, sticky="we", padx=10) # Polje za naziv ormana
        labela("Strujni krug:", 1, 0); self.e_naz = tk.Entry(self.f_unos, font=("Segoe UI", 11), bd=1, relief="solid"); self.e_naz.grid(row=1, column=1, sticky="we", padx=10) # Polje za opis kruga
        labela("Tip:", 1, 2); self.e_tip = ttk.Combobox(self.f_unos, values=self.tipovi, font=("Segoe UI", 11)); self.e_tip.grid(row=1, column=3, sticky="we", padx=10) # Padajući meni za materijale
        
        labela("Količina:", 2, 0) # Labela za količinu
        self.f_kol_wrap = tk.Frame(self.f_unos, bg="white") # Mali okvir za grupisanje unosa broja i jedinice mere
        self.f_kol_wrap.grid(row=2, column=1, sticky="we", padx=10) # Pozicioniranje wrap okvira
        self.e_met = tk.Entry(self.f_kol_wrap, font=("Segoe UI", 11), bd=1, relief="solid", width=10); self.e_met.pack(side="left", fill="x", expand=True) # Polje za unos broja
        self.e_jed = ttk.Combobox(self.f_kol_wrap, values=["m", "kom"], font=("Segoe UI", 10), width=5, state="readonly"); self.e_jed.set("m"); self.e_jed.pack(side="left", padx=(5, 0)) # Birač jedinice (m ili kom)

        labela("Napomena:", 2, 2); self.e_nap = tk.Entry(self.f_unos, font=("Segoe UI", 11), bd=1, relief="solid"); self.e_nap.grid(row=2, column=3, sticky="we", padx=10) # Polje za dodatnu napomenu
        self.f_unos.columnconfigure((1,3), weight=1) # Omogućavanje da se kolone unosa šire ravnomerno

        btn_f = tk.Frame(self.main, bg="#f0f2f5") # Okvir za komandnu dugmad
        btn_f.pack(fill="x", pady=15) # Razmak okvira sa dugmićima
        self.btn_dodaj = tk.Button(btn_f, text="+ SNIMI / DODAJ", command=self.sacuvaj_podatke, bg="#3182ce", fg="white", font=("Segoe UI", 10, "bold"), padx=20); self.btn_dodaj.pack(side="left", padx=5) # Dugme za snimanje
        tk.Button(btn_f, text="✏️ POVUCI", command=self.popuni_za_izmenu, bg="#805ad5", fg="white", font=("Segoe UI", 10), padx=15).pack(side="left", padx=5) # Dugme za povlačenje podataka u formu
        tk.Button(btn_f, text="OBRIŠI", command=self.obrisi, bg="#e53e3e", fg="white", font=("Segoe UI", 10), padx=15).pack(side="left", padx=5) # Dugme za brisanje selektovanog
        tk.Button(btn_f, text="📂 RESTORE", command=self.restore, bg="#718096", fg="white", font=("Segoe UI", 10), padx=15).pack(side="right", padx=5) # Dugme za vraćanje baze
        tk.Button(btn_f, text="💾 BACKUP", command=self.backup, bg="#38a169", fg="white", font=("Segoe UI", 10), padx=15).pack(side="right") # Dugme za pravljenje kopije baze

        self.tree = ttk.Treeview(self.main, columns=("id", "1", "2", "3", "4", "5", "6", "7"), show='headings') # Kreiranje tabele za prikaz podataka
        zaglavlja = [("id", "ID", 40), ("1", "DATUM", 90), ("2", "ORMAN", 90), ("3", "KRUG", 120), ("4", "TIP", 180), ("5", "KOL", 60), ("6", "JED", 50), ("7", "NAPOMENA", 200)] # Definicija zaglavlja
        for k, t, w in zaglavlja: # Petlja za postavljanje zaglavlja i širina kolona
            self.tree.heading(k, text=t); self.tree.column(k, width=w, anchor="center") # Primena podešavanja na svaku kolonu
        self.tree.pack(fill="both", expand=True) # Postavljanje tabele da popuni raspoloživ prostor

        self.footer = tk.Frame(self.main, bg="#f0f2f5") # Donji okvir za sumarne informacije
        self.footer.pack(fill="x", pady=20) # Pozicioniranje footera
        self.total_lbl = tk.Label(self.footer, text="UKUPNO KABLOVA: 0.00 m | 0 kom", font=("Segoe UI", 16, "bold"), bg="#f0f2f5") # Labela za prikaz totala
        self.total_lbl.pack(side="left") # Postavljanje labele na levu stranu
        tk.Button(self.footer, text="💎 GENERIŠI IZVEŠTAJ", command=self.export_html, bg="#2d3748", fg="white", font=("Segoe UI", 12, "bold"), padx=30, pady=12).pack(side="right") # Dugme za HTML export

        self.osvezi_tabelu() # Prvo učitavanje podataka iz baze u tabelu

    def ucitaj_logo_u_base64(self): # Funkcija za konverziju logotipa
        if os.path.exists(self.putanja_logotipa): # Provera da li fajl postoji
            try: # Pokušaj čitanja
                with open(self.putanja_logotipa, "rb") as f: return base64.b64encode(f.read()).decode('utf-8') # Čitanje bajtova i enkodiranje u string
            except: return "" # U slučaju greške vrati prazan string
        return "" # Ako fajl ne postoji vrati prazan string

    def kreiraj_bazu(self): # Funkcija za inicijalizaciju SQLite baze
        with sqlite3.connect(self.db_name) as conn: # Otvaranje konekcije
            conn.execute("CREATE TABLE IF NOT EXISTS radovi (id INTEGER PRIMARY KEY AUTOINCREMENT, datum TEXT, orman TEXT, opis TEXT, tip TEXT, kol REAL, jed TEXT, napomena TEXT)") # SQL komanda za kreiranje tabele

    def osvezi_tabelu(self): # Funkcija za sinhronizaciju tabele na ekranu sa bazom
        for i in self.tree.get_children(): self.tree.delete(i) # Brisanje svih trenutnih redova u Treeview
        tm, tk = 0.0, 0.0 # Pomoćne promenljive za zbir metara i komada
        # Reči koje označavaju opremu (ono što NE sabiramo)
        oprema_kljucne_reci = ("REGAL", "BREZON", "C-ŠINA", "LR ", "POKLOPAC") # Lista ključnih reči za filter
        
        with sqlite3.connect(self.db_name) as conn: # Konekcija na bazu
            for r in conn.execute("SELECT * FROM radovi ORDER BY id DESC").fetchall(): # Čitanje svih redova, najnoviji prvi
                self.tree.insert("", "end", values=r) # Ubacivanje reda u vizuelnu tabelu
                
                # Provera: Sabiramo samo ako u nazivu NEMA ključnih reči za opremu
                tip_stavke = str(r[4]).upper() # Pretvaranje tipa materijala u velika slova za lakšu proveru
                if not any(word in tip_stavke for word in oprema_kljucne_reci): # Ako nije oprema
                    try: # Pokušaj sabiranja
                        if r[6] == "m": tm += float(r[5]) # Ako je jedinica mere metar
                        else: tk += float(r[5]) # Ako je jedinica mere komad
                    except: pass # Preskoči ako podatak nije broj
        self.total_lbl.config(text=f"UKUPNO KABLOVA: {tm:.2f} m | {int(tk)} kom") # Ažuriranje teksta sa sumom

    def sacuvaj_podatke(self): # Funkcija za unos u bazu
        try: # Validacija unosa
            m = float(self.e_met.get().replace(',', '.')) # Zamena zareza tačkom i pretvaranje u decimalni broj
            p = (self.e_dat.get(), self.e_orm.get().upper(), self.e_naz.get(), self.e_tip.get(), m, self.e_jed.get(), self.e_nap.get()) # Pakovanje podataka u torku
            with sqlite3.connect(self.db_name) as conn: # Konekcija na bazu
                if self.edit_id: conn.execute("UPDATE radovi SET datum=?, orman=?, opis=?, tip=?, kol=?, jed=?, napomena=? WHERE id=?", (*p, self.edit_id)) # Ako menjamo postojeći red
                else: conn.execute("INSERT INTO radovi (datum, orman, opis, tip, kol, jed, napomena) VALUES (?,?,?,?,?,?,?)", p) # Ako dodajemo novi red
            self.ocisti_formu(); self.osvezi_tabelu() # Čišćenje unosa i osvežavanje prikaza
        except: messagebox.showerror("Greška", "Proverite unos!") # Poruka u slučaju pogrešnog unosa broja

    def popuni_za_izmenu(self): # Funkcija za "povlačenje" podataka u formu
        sel = self.tree.selection() # Provera šta je selektovano u tabeli
        if not sel: return # Ako ništa nije izabrano, prekini
        v = self.tree.item(sel[0])['values'] # Uzimanje vrednosti iz izabranog reda
        self.edit_id = v[0]; self.ocisti_formu(False) # Postavljanje ID-a i parcijalno čišćenje forme
        self.e_dat.insert(0, v[1]); self.e_orm.insert(0, v[2]); self.e_naz.insert(0, v[3]) # Vraćanje teksta u polja
        self.e_tip.set(v[4]); self.e_met.insert(0, v[5]); self.e_jed.set(v[6]); self.e_nap.insert(0, v[7]) # Vraćanje vrednosti u birače i ostala polja
        self.btn_dodaj.config(text="💾 SAČUVAJ IZMENE", bg="#ed8936") # Promena izgleda dugmeta u mod za izmenu

    def ocisti_formu(self, reset_id=True): # Funkcija za pražnjenje polja
        for e in [self.e_dat, self.e_orm, self.e_naz, self.e_met, self.e_nap]: e.delete(0, 'end') # Brisanje svih tekstova
        self.e_tip.set(''); self.e_jed.set('m'); self.e_dat.insert(0, datetime.now().strftime("%d.%m.%Y")) # Resetovanje datuma i birača
        if reset_id: self.edit_id = None; self.btn_dodaj.config(text="+ SNIMI / DODAJ", bg="#3182ce") # Vraćanje dugmeta u normalan mod

    def obrisi(self): # Funkcija za brisanje podataka
        sel = self.tree.selection() # Uzmi selektovano
        if sel and messagebox.askyesno("Baza", "Obrisati?"): # Potvrda od strane korisnika
            with sqlite3.connect(self.db_name) as conn: # Konekcija na bazu
                for s in sel: conn.execute("DELETE FROM radovi WHERE id=?", (self.tree.item(s)['values'][0],)) # Brisanje svakog izabranog reda po ID-u
            self.osvezi_tabelu() # Osvežavanje prikaza

    def backup(self): # Funkcija za pravljenje sigurnosne kopije
        d = f"backup_{datetime.now().strftime('%Y%m%d_%H%M')}.db"; shutil.copy2(self.db_name, d) # Kreiranje naziva sa vremenom i kopiranje fajla
        messagebox.showinfo("Backup", f"Snimljeno kao: {d}") # Obaveštenje

    def export_html(self): # Funkcija za generisanje HTML izveštaja
        stavke = [self.tree.item(c)["values"] for c in self.tree.get_children()] # Prikupljanje svih podataka iz trenutnog prikaza
        if not stavke: return # Prekini ako nema podataka
        
        # 1. LOGIKA ZA SABIRANJE (Isto kao u tabeli, preskače nosače)
        tm_rep, tk_rep = 0.0, 0.0 # Reset suma za izveštaj
        oprema_kljucne_reci = ("REGAL", "BREZON", "C-ŠINA", "LR ", "POKLOPAC") # Reči za filtriranje
        
        for s in stavke: # Prolaz kroz sve stavke za export
            tip_stavke = str(s[4]).upper() # Tip materijala
            if not any(word in tip_stavke for word in oprema_kljucne_reci): # Ako nije oprema
                try: # Saberi
                    val = float(s[5]) # Vrednost količine
                    if str(s[6]) == "m": tm_rep += val # Sumiraj metre
                    else: tk_rep += val # Sumiraj komade
                except: pass # Preskoči greške u formatu

        # 2. PRIPREMA LOGOTIPA I REDOVA
        logo_html = f'<img src="data:image/webp;base64,{self.logo_data}" style="height:80px;">' if self.logo_data else "" # Priprema slike u HTML formatu
        rows = "".join([f'<tr><td>{s[1]}</td><td>{s[2]}</td><td>{s[3]}</td><td><b>{s[4]}</b></td><td>{s[5]} {s[6]}</td><td><i>{s[7]}</i></td></tr>' for s in stavke]) # Generisanje HTML redova tabele
        
        # 3. HTML SA DODATIM REDOM ZA TOTAL
        html = f"""
        <html><head><meta charset='UTF-8'>
        <style>
            body {{ font-family: 'Segoe UI', Arial; margin: 40px; color: #333; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #3182ce; padding-bottom: 20px; margin-bottom: 30px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ background-color: #3182ce; color: white; padding: 12px; text-transform: uppercase; font-size: 13px; }}
            td {{ border-bottom: 1px solid #e2e8f0; padding: 12px; text-align: center; font-size: 14px; }}
            .total-row {{ background-color: #edf2f7; font-weight: bold; font-size: 16px; color: #2d3748; }}
            tr:nth-child(even) {{ background-color: #f7fafc; }}
            .footer-info {{ margin-top: 30px; text-align: right; font-size: 18px; font-weight: bold; color: #2d3748; border-top: 2px solid #3182ce; padding-top: 10px; }}
            @media print {{ @page {{ margin: 0; }} body {{ padding: 1.5cm; }} }}
        </style></head>
        <body>
            <div class='header'>
                <div>{logo_html}</div>
                <div style='text-align: right;'>
                    <h1 style='margin:0; color:#2d3748;'>SPECIFIKACIJA RADOVA</h1>
                    <p style='margin:5px 0;'>Datum izveštaja: {datetime.now().strftime("%d.%m.%Y")}</p>
                </div>
            </div>
            <table>
                <thead>
                    <tr><th>Datum</th><th>Orman</th><th>Strujni krug</th><th>Tip (Materijal)</th><th>Količina</th><th>Napomena</th></tr>
                </thead>
                <tbody>
                    {rows}
                    <tr class='total-row'>
                        <td colspan='4' style='text-align:right; padding:15px;'>UKUPNA METRAŽA KABLOVA:</td>
                        <td colspan='2' style='text-align:left; padding:15px;'>{tm_rep:.2f} m | {int(tk_rep)} kom</td>
                    </tr>
                </tbody>
            </table>
            <div class='footer-info'>UKUPNO STAVKI NA LISTI: {len(stavke)}</div>
        </body>
        </html>
        """ # Kraj HTML strukture sa CSS-om i podacima
        f_name = os.path.realpath("Izvestaj_Radova.html") # Kreiranje pune putanje fajla
        with open(f_name, "w", encoding="utf-8") as f: f.write(html) # Pisanje HTML fajla na disk
        webbrowser.open("file://" + f_name) # Otvaranje izveštaja u default browseru

    def restore(self): # Funkcija za vraćanje stare baze podataka
        # Otvara prozor za biranje fajla i filtrira samo .db fajlove
        f_putanja = filedialog.askopenfilename(title="Izaberi backup bazu", filetypes=[("Database files", "*.db")])
        
        # Ako je korisnik izabrao fajl (nije kliknuo Cancel)
        if f_putanja:
            # Traži potvrdu jer ova radnja prepisuje trenutne podatke
            if messagebox.askyesno("Restore", "Ovo će obrisati trenutne podatke i učitati backup. Nastaviti?"):
                try:
                    # Kopira izabrani backup fajl preko aktivne baze (elektro_baza.db)
                    shutil.copy2(f_putanja, self.db_name)
                    
                    # Odmah osvežava prikaz u tabeli sa novim podacima
                    self.osvezi_tabelu()
                    
                    # Obaveštava korisnika da je sve prošlo kako treba
                    messagebox.showinfo("Uspeh", "Baza uspešno vraćena!")
                except Exception as e:
                    # U slučaju greške (npr. fajl je zauzet), ispisuje šta nije u redu
                    messagebox.showerror("Greška", f"Neuspešan restore: {e}")

if __name__ == "__main__": # Provera da li se skripta pokreće direktno
    r = tk.Tk(); app = ElektroProUltra(r); r.mainloop() # Inicijalizacija prozora, klase i pokretanje glavne petlje aplikacije
