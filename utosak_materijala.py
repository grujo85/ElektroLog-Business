import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF

# ==============================================================================
# 1. KONFIGURACIJA
# ==============================================================================
st.set_page_config(
    page_title="ELEKTRO-LOG BUSINESS v1.1",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. KLASA ZA PDF (Bez linija, centrirano, sa napomenom)
# ==============================================================================
class PDFSpec(FPDF):
    def header(self):
        if os.path.exists("elmar.webp"):
            try: self.image("elmar.webp", 10, 8, 33)
            except: pass
        self.set_font("Arial", "B", 15)
        self.cell(0, 10, "SPECIFIKACIJA RADOVA", ln=True, align="R")
        self.set_font("Arial", "", 10)
        self.cell(0, 10, f"Datum izrade: {datetime.now().strftime('%d.%m.%Y')}", ln=True, align="R")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128)
        self.cell(0, 10, "ELMAR ELEKTRO-INSTALACIJE | DESIGN VLADE 2026 | INTERNI DOKUMENT", align="C")

# ==============================================================================
# 3. GLAVNA KLASA ZA LOGIKU
# ==============================================================================
class ElektroProUltra:
    def __init__(self):
        self.db_name = "elektro_baza.db"
        # Ovaj rečnik stavi unutar __init__ metode ili na početak skripte
self.kategorije_materijala = {
    "Nosači i oprema": [
        "Brezon M8", "Brezon M10", "C-šina 30x20", "C-šina 41x21", 
        "Regal 50", "Regal 100", "Regal 150", "Regal 200", "Regal 300", 
        "Regal 400", "Regal 500", "Regal 600", "LR Krivina", "LR T-komad", "Poklopac regala"
    ],
    "Instalacioni kablovi (PP-Y)": [
        "PP-Y 2x1.5", "PP-Y 3x1.5", "PP-Y 3x2.5", "PP-Y 3x4", "PP-Y 4x1.5", 
        "PP-Y 4x2.5", "PP-Y 4x4", "PP-Y 5x1.5", "PP-Y 5x2.5", "PP-Y 5x4", 
        "PP-Y 5x6", "PP-Y 5x10", "PP-Y 5x16"
    ],
    "Bezhalogeni kablovi (N2XH)": [
        "N2XH-J 3x1.5", "N2XH-J 3x2.5", "N2XH-J 3x4", "N2XH-J 5x1.5", 
        "N2XH-J 5x2.5", "N2XH-J 5x4", "N2XH-J 5x6", "N2XH-J 5x10", 
        "N2XH-J 5x16", "N2XH-J 5x25", "N2XH-J 5x35", "N2XH-J 5x50"
    ],
    "Vatrootporni kablovi (FE180)": [
        "NHXH FE180 3x1.5", "NHXH FE180 3x2.5", "NHXH FE180 5x1.5", 
        "NHXH FE180 5x2.5", "NHXH FE180 5x4", "NHXH FE180 5x6"
    ],
    "Energetski kablovi (PP00)": [
        "PP00 3x1.5", "PP00 3x2.5", "PP00 4x1.5", "PP00 4x2.5", "PP00 4x4", 
        "PP00 4x6", "PP00 4x10", "PP00 4x16", "PP00 4x25", "PP00 4x35", 
        "PP00 4x50", "PP00 4x70", "PP00 4x95", "PP00 4x120", "PP00 4x150", 
        "PP00 4x185", "PP00 4x240", "PP00 5x1.5", "PP00 5x2.5", "PP00 5x4", 
        "PP00 5x6", "PP00 5x10", "PP00 5x16"
    ],
    "Aluminijumski kablovi (PP00-A)": [
        "PP00-A (Al) 4x16", "PP00-A 4x25", "PP00-A 4x35", "PP00-A 4x50", 
        "PP00-A 4x70", "PP00-A 4x95", "PP00-A 4x120", "PP00-A 4x150", "PP00-A 4x240"
    ],
    "Gumeni kablovi (H07RN-F)": [
        "H07RN-F (GG/J) 3x1.5", "H07RN-F 3x2.5", "H07RN-F 5x1.5", 
        "H07RN-F 5x2.5", "H07RN-F 5x4", "H07RN-F 5x6", "H07RN-F 5x10", "H07RN-F 5x16"
    ],
    "Signalni i provodnici": [
        "LiYCY 2x0.75", "LiYCY 3x0.75", "LiYCY 4x0.75", "LiYCY 5x0.75", 
        "P/F (H07V-K) 0.75", "P/F 1.5", "P/F 2.5", "P/F 4", "P/F 6", 
        "P 1.5", "P 2.5", "P 4", "P 6"
    ],
    "Specijalni i Telekom": [
        "SKS 2x16", "SKS 4x16", "UTP Cat5e", "FTP Cat6", "SFTP Cat7", 
        "Koaksijalni RG6", "Alarmni 4x0.22", "Alarmni 6x0.22", "Solarni 6mm2"
    ]
}
        self.kreiraj_bazu()

    def kreiraj_bazu(self):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS radovi 
                (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                datum TEXT, orman TEXT, opis TEXT, tip TEXT, 
                kol REAL, jed TEXT, napomena TEXT)""")

    def sacuvaj_u_bazu(self, d):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("INSERT INTO radovi (datum, orman, opis, tip, kol, jed, napomena) VALUES (?,?,?,?,?,?,?)", d)

    def azuriraj_bazu(self, df_izmenjen):
        with sqlite3.connect(self.db_name) as conn:
            df_izmenjen.to_sql("radovi", conn, if_exists="replace", index=False)

    def obrisi_sve(self):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("DELETE FROM radovi")

    def generisi_pdf(self, df, tm, tk):
        pdf = PDFSpec()
        pdf.add_page()
        
        pdf.set_fill_color(49, 130, 206) 
        pdf.set_text_color(255)
        pdf.set_font("Arial", "B", 9)
        
        cols = [
            ("Datum", 22), ("RO", 18), ("Krug", 15), 
            ("Tip materijala", 60), ("Kol", 15), ("Jed", 10), ("Napomena", 50)
        ]
        
        for col_name, width in cols:
            pdf.cell(width, 10, col_name, border=0, align="C", fill=True)
        pdf.ln()

        pdf.set_text_color(0)
        pdf.set_font("Arial", "", 8)
        
        df_clean = df.dropna(subset=['datum', 'orman', 'tip'])

        for _, r in df_clean.iterrows():
            pdf.cell(22, 8, str(r['datum']), border=0, align="C")
            pdf.cell(18, 8, str(r['orman']), border=0, align="C")
            pdf.cell(15, 8, str(r['opis']), border=0, align="C")
            pdf.cell(60, 8, str(r['tip']), border=0, align="C")
            pdf.cell(15, 8, str(r['kol']), border=0, align="C")
            pdf.cell(10, 8, str(r['jed']), border=0, align="C")
            nap = str(r['napomena']) if r['napomena'] and str(r['napomena']) != 'None' else ""
            pdf.cell(50, 8, nap, border=0, align="C")
            pdf.ln()

        pdf.ln(5)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 10, f"UKUPNO KABLOVA: {tm:.2f} m | {int(tk)} kom", ln=True, align="R")
        return pdf.output()

# ==============================================================================
# 4. INTERFEJS (Streamlit)
# ==============================================================================
app = ElektroProUltra()

with st.sidebar:
    st.header("⚙️ SISTEM")
    
    # 1. BACKUP
    if os.path.exists(app.db_name):
        with open(app.db_name, "rb") as f:
            st.download_button("📥 PREUZMI REZERVNU KOPIJU (Backup)", f, file_name="elektro_baza_backup.db")
    
    st.divider()
    
    # 2. RESTORE
    st.subheader("📤 VRATI PODATKE (Restore)")
    fajl_za_vracanje = st.file_uploader("Ubaci .db fajl", type="db")
    if fajl_za_vracanje is not None:
        if st.button("⚠️ POTVRDI RESTORE"):
            with open(app.db_name, "wb") as f:
                f.write(fajl_za_vracanje.getbuffer())
            st.success("Podaci su uspešno vraćeni!")
            st.rerun()

    st.divider()
    
    # 3. DELETE ALL
    st.subheader("🗑️ BRISANJE")
    potvrda = st.checkbox("Potvrđujem brisanje cele baze")
    if st.button("🔴 OBRIŠI SVE"):
        if potvrda:
            app.obrisi_sve()
            st.success("Baza je ispražnjena!")
            st.rerun()
        else:
            st.warning("Prvo štikliraj potvrdu!")

# GLAVNI EKRAN - UNOS
with st.expander("📝 UNOS NOVE STAVKE"):
    with st.form("forma_unos", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        dat = c1.text_input("📅 Datum", datetime.now().strftime("%d.%m.%Y"))
        orm = c2.text_input("🏗️ RO").upper()
        krug = c3.text_input("🔌 Krug")
        
        # --- NOVI DEO ZA KATEGORIJE ---
        col_kat, col_tip = st.columns(2)
        
        # 1. Korisnik bira grupu
        izabrana_kat = col_kat.selectbox("📁 Izaberi kategoriju", list(app.kategorije_materijala.keys()))
        
        # 2. Na osnovu grupe, nudi se podlista materijala
        tip = col_tip.selectbox("📦 Tip materijala", app.kategorije_materijala[izabrana_kat])
        # ------------------------------
        
        c4, c5, c6 = st.columns([1, 1, 2])
        kol = c4.number_input("Kol", min_value=0.0, step=0.1)
        jed = c5.selectbox("Jed", ["m", "kom"])
        nap = c6.text_input("📝 Napomena")
        
        if st.form_submit_button("💾 SNIMI"):
            app.sacuvaj_u_bazu((dat, orm, krug, tip, kol, jed, nap))
            st.rerun()

# PRIKAZ I PDF
with sqlite3.connect(app.db_name) as conn:
    df_prikaz = pd.read_sql_query("SELECT * FROM radovi ORDER BY id DESC", conn)

if not df_prikaz.empty:
    # Metrika
    oprema = ("REGAL", "BREZON", "C-ŠINA")
    mask = df_prikaz['tip'].str.upper().str.contains('|'.join(oprema))
    df_k = df_prikaz[~mask]
    suma_m = df_k[df_k['jed'] == 'm']['kol'].sum()
    suma_k = df_k[df_k['jed'] == 'kom']['kol'].sum()

    st.metric("UKUPNO METARA", f"{suma_m:.2f} m")

    edited_df = st.data_editor(df_prikaz, use_container_width=True, hide_index=True, num_rows="dynamic")

    if st.button("✅ SAČUVAJ IZMENE"):
        app.azuriraj_bazu(edited_df)
        st.success("Ažurirano!")
        st.rerun()

    st.divider()
    pdf_output = app.generisi_pdf(edited_df, suma_m, suma_k)
    st.download_button("📄 PREUZMI PDF IZVEŠTAJ", bytes(pdf_output), "izvestaj.pdf", "application/pdf")
else:
    st.info("Baza je prazna.")
