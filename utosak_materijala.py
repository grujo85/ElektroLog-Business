import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from datetime import datetime
import webbrowser
import os
import sqlite3
import shutil
import base64

class ElektroProUltra:
    def __init__(self, root):
        self.root = root
        self.root.title("ELEKTRO-LOG BUSINESS v1.0")
        self.root.geometry("1150x850")
        self.root.configure(bg="#f0f2f5")
        
        self.db_name = "elektro_baza.db"
        self.putanja_logotipa = "elmar.webp" 
        self.logo_data = self.ucitaj_logo_u_base64()
        self.edit_id = None
        
        self.kreiraj_bazu()

        self.main = tk.Frame(root, bg="#f0f2f5", padx=30, pady=20)
        self.main.pack(fill="both", expand=True)

        tk.Label(self.main, text="PRO SPECIFIKACIJA RADOVA", 
                 font=("Segoe UI", 20, "bold"), fg="#2d3748", bg="#f0f2f5").pack(pady=(0,15))

        # Forma za unos
        self.f_unos = tk.Frame(self.main, bg="white", padx=20, pady=20, relief="flat", highlightthickness=1, highlightbackground="#e2e8f0")
        self.f_unos.pack(fill="x")

        def in_f(label, row, col):
            tk.Label(self.f_unos, text=label, font=("Segoe UI", 9, "bold"), bg="white", fg="#4a5568").grid(row=row, column=col, sticky="w", pady=5, padx=5)
            e = tk.Entry(self.f_unos, font=("Segoe UI", 11), bd=1, relief="solid")
            e.grid(row=row, column=col+1, sticky="we", padx=10, pady=5)
            return e

        self.e_dat = in_f("Datum:", 0, 0)
        self.e_dat.insert(0, datetime.now().strftime("%d.%m.%Y"))
        self.e_orm = in_f("Orman (RO):", 0, 2)
        self.e_naz = in_f("Strujni krug:", 1, 0)
        self.e_met = in_f("Količina (m):", 1, 2)
        self.e_nap = in_f("Napomena:", 2, 0)
        self.f_unos.columnconfigure((1,3), weight=1)

        # Dugmad za akcije
        btn_f = tk.Frame(self.main, bg="#f0f2f5")
        btn_f.pack(fill="x", pady=15)

        self.btn_dodaj = tk.Button(btn_f, text="+ SNIMI / DODAJ", command=self.sacuvaj_podatke, bg="#3182ce", fg="white", font=("Segoe UI", 10, "bold"), padx=20)
        self.btn_dodaj.pack(side="left", padx=5)
        
        tk.Button(btn_f, text="✏️ POVUCI ZA PREPRAVKU", command=self.popuni_za_izmenu, bg="#805ad5", fg="white", font=("Segoe UI", 10), padx=15).pack(side="left", padx=5)
        tk.Button(btn_f, text="OBRIŠI", command=self.obrisi, bg="#e53e3e", fg="white", font=("Segoe UI", 10), padx=15).pack(side="left", padx=5)
        tk.Button(btn_f, text="OČISTI", command=self.ocisti_formu, bg="#a0aec0", fg="white", font=("Segoe UI", 10), padx=10).pack(side="left", padx=5)
        
        # Backup i Restore dugmad
        tk.Button(btn_f, text="📥 RESTORE (VRATI)", command=self.restore_baze, bg="#d69e2e", fg="white", font=("Segoe UI", 10), padx=15).pack(side="right", padx=5)
        tk.Button(btn_f, text="💾 BACKUP", command=self.backup, bg="#38a169", fg="white", font=("Segoe UI", 10, "bold"), padx=15).pack(side="right")

        # Tabela
        self.tree = ttk.Treeview(self.main, columns=("id", "1", "2", "3", "4", "5"), show='headings')
        for i, h in enumerate(["ID", "DATUM", "ORMAN", "STRUJNI KRUG", "METARA", "NAPOMENA"]):
            self.tree.heading(str(i if i>0 else "id"), text=h)
        self.tree.column("id", width=40, anchor="center")
        self.tree.column("1", width=90, anchor="center")
        self.tree.pack(fill="both", expand=True)

        self.footer = tk.Frame(self.main, bg="#f0f2f5")
        self.footer.pack(fill="x", pady=20)
        self.total_lbl = tk.Label(self.footer, text="UKUPNO: 0.00 m", font=("Segoe UI", 16, "bold"), bg="#f0f2f5")
        self.total_lbl.pack(side="left")
        tk.Button(self.footer, text="💎 GENERIŠI PDF IZVEŠTAJ", command=self.export_html, bg="#2d3748", fg="white", font=("Segoe UI", 12, "bold"), padx=30, pady=12).pack(side="right")

        self.osvezi_tabelu()

    def ucitaj_logo_u_base64(self):
        if os.path.exists(self.putanja_logotipa):
            try:
                with open(self.putanja_logotipa, "rb") as f:
                    return base64.b64encode(f.read()).decode('utf-8')
            except: return ""
        return ""

    def kreiraj_bazu(self):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("CREATE TABLE IF NOT EXISTS radovi (id INTEGER PRIMARY KEY AUTOINCREMENT, datum TEXT, orman TEXT, opis TEXT, metara REAL, napomena TEXT)")

    def osvezi_tabelu(self):
        for i in self.tree.get_children(): self.tree.delete(i)
        with sqlite3.connect(self.db_name) as conn:
            rows = conn.execute("SELECT * FROM radovi ORDER BY id DESC").fetchall()
            for r in rows: self.tree.insert("", "end", values=r)
        t = sum(float(self.tree.item(c)["values"][4]) for c in self.tree.get_children())
        self.total_lbl.config(text=f"UKUPNO: {t:.2f} m")

    def popuni_za_izmenu(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Izmena", "Izaberite red u tabeli!")
            return
        v = self.tree.item(selected[0])['values']
        self.edit_id = v[0]
        self.ocisti_formu(reset_id=False)
        self.e_dat.insert(0, v[1]); self.e_orm.insert(0, v[2]); self.e_naz.insert(0, v[3])
        self.e_met.insert(0, v[4]); self.e_nap.insert(0, v[5])
        self.btn_dodaj.config(text="💾 SAČUVAJ IZMENE", bg="#ed8936")

    def sacuvaj_podatke(self):
        try:
            m = float(self.e_met.get().replace(',', '.'))
            with sqlite3.connect(self.db_name) as conn:
                if self.edit_id:
                    conn.execute("UPDATE radovi SET datum=?, orman=?, opis=?, metara=?, napomena=? WHERE id=?",
                                 (self.e_dat.get(), self.e_orm.get().upper(), self.e_naz.get(), m, self.e_nap.get(), self.edit_id))
                else:
                    conn.execute("INSERT INTO radovi (datum, orman, opis, metara, napomena) VALUES (?,?,?,?,?)", 
                                 (self.e_dat.get(), self.e_orm.get().upper(), self.e_naz.get(), m, self.e_nap.get()))
            self.ocisti_formu(); self.osvezi_tabelu()
        except: messagebox.showerror("Greška", "Proverite unos metara!")

    def ocisti_formu(self, reset_id=True):
        for e in [self.e_dat, self.e_orm, self.e_naz, self.e_met, self.e_nap]: e.delete(0, 'end')
        self.e_dat.insert(0, datetime.now().strftime("%d.%m.%Y"))
        if reset_id:
            self.edit_id = None
            self.btn_dodaj.config(text="+ SNIMI / DODAJ", bg="#3182ce")

    def obrisi(self):
        sel = self.tree.selection()
        if sel and messagebox.askyesno("Baza", "Obrisati trajno?"):
            with sqlite3.connect(self.db_name) as conn:
                for s in sel: conn.execute("DELETE FROM radovi WHERE id=?", (self.tree.item(s)['values'][0],))
            self.osvezi_tabelu()

    def backup(self):
        d = f"backup_elektro_{datetime.now().strftime('%Y%m%d_%H%M')}.db"
        shutil.copy2(self.db_name, d)
        messagebox.showinfo("Backup", f"Snimljeno kao: {d}")

    def restore_baze(self):
        """Funkcija za vraćanje baze iz backup fajla."""
        fajl = filedialog.askopenfilename(title="Izaberi backup bazu", filetypes=[("Database fajlovi", "*.db")])
        if fajl:
            pitanje = messagebox.askyesno("RESTORE", "UPOZORENJE!\nOvo će obrisati trenutne podatke i učitati one iz backup-a.\nŽelite li da nastavite?")
            if pitanje:
                try:
                    shutil.copy2(fajl, self.db_name)
                    self.osvezi_tabelu()
                    messagebox.showinfo("Uspeh", "Baza je uspešno vraćena!")
                except Exception as e:
                    messagebox.showerror("Greška", f"Neuspešan restore: {e}")

    def export_html(self):
        stavke = [self.tree.item(c)["values"] for c in self.tree.get_children()]
        if not stavke: return
        rows_html = "".join([f"<tr><td>{s[1]}</td><td>{s[2]}</td><td>{s[3]}</td><td>{s[4]} m</td><td>{s[5]}</td></tr>" 
                             for s in sorted(stavke, key=lambda x: x[2])])
        html = f"""
        <html>
        <head><meta charset="UTF-8"><style>
		body {{ font-family: 'Segoe UI', sans-serif; padding: 40px; color: #2d3748; }}
		@media print {{ @page {{ margin: 0; }} body {{ padding: 1.5cm; }} }}
		.header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 3px solid #3182ce; padding-bottom: 20px; }}
		.logo {{ max-width: 150px; max-height: 80px; }}
		
		/* 1. Ovde dodajemo table-layout: fixed */
		table {{ 
			width: 100%; 
			border-collapse: collapse; 
			margin-top: 30px; 
			table-layout: fixed; 
		}}
		
		th {{ background: #2d3748; color: white; padding: 12px; text-align: left; }}
		
		/* 2. Ovde brišemo 'white-space: nowrap' i dodajemo 'word-wrap' */
		td {{ 
			padding: 10px; 
			border-bottom: 1px solid #e2e8f0; 
			font-size: 13px; 
			word-wrap: break-word; 
			overflow-wrap: break-word;
			vertical-align: top; 
		}}
		
		/* 3. OPCIONO: Odredi širinu kolona da 'Napomena' ima najviše mesta */
		th:nth-child(1) {{ width: 100px; }} /* Datum */
		th:nth-child(2) {{ width: 80px; }}  /* Orman */
		th:nth-child(3) {{ width: 150px; }} /* Oznaka(SK) */
		th:nth-child(4) {{ width: 80px; }}  /* Metraža */
		/* Peta kolona (Napomena) će automatski uzeti sav preostali prostor */

		.total {{ text-align: right; margin-top: 20px; font-size: 18px; font-weight: bold; }}
		.footer {{ margin-top: 60px; display: flex; justify-content: space-between; }}
		.sig-box {{ border-top: 1px solid #000; width: 220px; text-align: center; padding-top: 5px; }}
		</style></head>
        <body>
            <div class="header">
                <img src="data:image/webp;base64,{self.logo_data}" class="logo">
                <div><h2>SPECIFIKACIJA IZVEDENIH INSTALACIJA</h2><p>Dokumentacija o utrošku kablova i strujnih krugova</p><p>Datum: {datetime.now().strftime('%d.%m.%Y')}</p></div>
            </div>,
            <table><thead><tr><th>Datum</th><th>Orman</th><th>Oznaka(SK)</th><th>Metraža</th><th>Napomena</th></tr></thead>
            <tbody>{rows_html}</tbody></table>
            <div class="total">UKUPNO: {sum(float(s[4]) for s in stavke):.2f} m</div>
            <div class="footer"><div class="sig-box">Izvođač</div><div class="sig-box">Nadzor</div></div>
        </body></html>"""
        f_name = os.path.realpath("Izvestaj_Pro.html")
        with open(f_name, "w", encoding="utf-8") as f: f.write(html)
        webbrowser.open("file://" + f_name)

if __name__ == "__main__":
    r = tk.Tk(); app = ElektroProUltra(r); r.mainloop()
