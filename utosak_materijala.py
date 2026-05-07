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
# 2. KLASA ZA PDF
# ==============================================================================
class PDFSpec(FPDF):
    def header(self):
        if os.path.exists("elmar.webp"):
            try: self.image("elmar.webp", 10, 8, 33)
            except: pass
        self.set_font("Arial", "B", 15)
        self.cell(0, 10, "SPECIFIKACIJA RADOVA", ln=True, align="R")
        self.cell(0, 10, "UTROSAK MATERIJALA", ln=True, align="R")
        self.set_font("Arial", "", 10)
        self.cell(0, 10, f"Datum izrade: {datetime.now().strftime('%d.%m.%Y')}", ln=True, align="R")
        self.ln(10)

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.set_text_color(128)
        self.cell(0, 10, "ELMAR ELEKTRO-INSTALACIJE | DESIGN VLADE 2026", align="C")

# ==============================================================================
# 3. GLAVNA KLASA ZA LOGIKU
# ==============================================================================
class ElektroProUltra:
    def __init__(self):
        self.db_name = "elektro_baza.db"
        self.kategorije_materijala = {
            "Nosaci i oprema": ["Brezon M8", "Brezon M10", "C-sina 30x20", "C-sina 41x21", "Regal 50", "Regal 100", "Regal 150", "Regal 200", "Regal 300", "Regal 400", "Regal 500", "Regal 600", "LR Krivina", "LR T-komad", "Poklopac regala"],
            "Instalacioni (PP-Y)": ["PP-Y 2x1.5", "PP-Y 3x1.5", "PP-Y 3x2.5", "PP-Y 3x4", "PP-Y 5x1.5", "PP-Y 5x2.5", "PP-Y 5x4", "PP-Y 5x6", "PP-Y 5x10", "PP-Y 5x16"],
            "Bezhalogeni (N2XH)": ["N2XH-J 3x1.5", "N2XH-J 3x2.5", "N2XH-J 3x4", "N2XH-J 5x1.5", "N2XH-J 5x2.5", "N2XH-J 5x4", "N2XH-J 5x6", "N2XH-J 5x10", "N2XH-J 5x16", "N2XH-J 5x25"],
            "Vatrootporni (FE180)": ["NHXH FE180 3x1.5", "NHXH FE180 3x2.5", "NHXH FE180 5x1.5", "NHXH FE180 5x2.5", "NHXH FE180 5x4", "NHXH FE180 5x6"],
            "Energetski (PP00)": ["PP00 3x1.5", "PP00 3x2.5", "PP00 4x1.5", "PP00 4x2.5", "PP00 4x4", "PP00 4x6", "PP00 4x10", "PP00 4x16", "PP00 4x25", "PP00 4x35", "PP00 4x50", "PP00 4x70", "PP00 5x1.5", "PP00 5x2.5", "PP00 5x4"],
            "Aluminijum (PP00-A)": ["PP00-A (Al) 4x16", "PP00-A 4x25", "PP00-A 4x35", "PP00-A 4x50", "PP00-A 4x70", "PP00-A 4x120", "PP00-A 4x240"],
            "Gumeni (H07RN-F)": ["H07RN-F 3x1.5", "H07RN-F 3x2.5", "H07RN-F 5x1.5", "H07RN-F 5x2.5", "H07RN-F 5x4", "H07RN-F 5x6"],
            "Signalni i P/F": ["LiYCY 2x0.75", "LiYCY 4x0.75", "P/F 0.75", "P/F 1.5", "P/F 2.5", "P/F 4", "P/F 6", "P/F 10", "P/F 16", "P 1.5", "P 2.5", "P 4"],
            "Telekom i Solarni": ["SKS 2x16", "SKS 4x16", "UTP Cat5e", "FTP Cat6", "SFTP Cat7", "Koaksijalni RG6", "Alarmni 6x0.22", "Solarni 6mm2"]
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
        
        # --- TABELA 1: SPECIFIKACIJA PO STAVKAMA ---
        pdf.set_fill_color(49, 130, 206) 
        pdf.set_text_color(255)
        pdf.set_font("Arial", "B", 9)
        cols = [("Datum", 22), ("RO", 18), ("Krug", 15), ("Tip materijala", 60), ("Kol", 15), ("Jed", 10), ("Napomena", 50)]
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

        pdf.ln(10)
        
        # --- TABELA 2: SUMARNI UTROSAK ---
        pdf.set_font("Arial", "B", 11)
        pdf.set_text_color(49, 130, 206) # Plava boja za naslov sume
        pdf.cell(0, 10, "SUMARNI UTROSAK MATERIJALA:", ln=True)
        
        pdf.set_text_color(0)
        pdf.set_font("Arial", "B", 9)
        pdf.set_fill_color(235, 235, 235) # Svetlo siva za zaglavlje sume
        pdf.cell(100, 8, "Materijal", border=0, fill=True, align="C")
        pdf.cell(30, 8, "Kolicina", border=0, fill=True, align="C")
        pdf.cell(30, 8, "Jedinica", border=0, fill=True, align="C")
        pdf.ln()

        pdf.set_font("Arial", "", 9)
        utrosak = df_clean.groupby(['tip', 'jed'])['kol'].sum().reset_index()
        for _, row in utrosak.iterrows():
            pdf.cell(100, 7, str(row['tip']), border=0, align="C")
            pdf.cell(30, 7, f"{row['kol']:.2f}", border=0, align="C")
            pdf.cell(30, 7, str(row['jed']), border=0, align="C")
            pdf.ln()

        # --- UOKVIRENI ZAKLJUČAK (UKUPNO KABLOVA) ---
        pdf.ln(10)
        
        # Podešavanje boja za okvir i unutrašnjost
        pdf.set_draw_color(49, 130, 206) # Tamno plava linija okvira
        pdf.set_fill_color(235, 248, 255) # Vrlo svetlo plava pozadina
        pdf.set_line_width(0.5)
        
        # Tekst koji ide unutra
        txt = f"UKUPNO KABLOVA: {tm:.2f} m | {int(tk)} kom"
        sirina_boxa = 100
        x_pozicija = 190 - sirina_boxa # Desno poravnanje
        
        # Crtanje pravougaonika i ispis teksta
        pdf.set_font("Arial", "B", 12)
        # rect(x, y, w, h, style) -> 'FD' znači Fill and Draw (boja + okvir)
        pdf.rect(x_pozicija, pdf.get_y(), sirina_boxa, 12, 'FD')
        
        # Pomaknemo kursor da ispiše tekst unutar tog pravougaonika
        pdf.set_x(x_pozicija)
        pdf.cell(sirina_boxa, 12, txt, border=0, align="C")
        
        return pdf.output()

# ==============================================================================
# 4. INTERFEJS
# ==============================================================================
app = ElektroProUltra()

with st.sidebar:
    st.header("⚙️ SISTEM")
    if os.path.exists(app.db_name):
        with open(app.db_name, "rb") as f:
            st.download_button("📥 PREUZMI BACKUP", f, file_name="elektro_baza.db")
    st.divider()
    f_res = st.file_uploader("Restore .db", type="db")
    if f_res and st.button("⚠️ POTVRDI RESTORE"):
        with open(app.db_name, "wb") as f: f.write(f_res.getbuffer())
        st.rerun()
    st.divider()
    if st.checkbox("Potvrda brisanja") and st.button("🔴 OBRIŠI SVE"):
        app.obrisi_sve(); st.rerun()

# UNOS
with st.expander("📝 UNOS NOVE STAVKE", expanded=True):
    c1, c2, c3 = st.columns(3)
    dat = c1.text_input("📅 Datum", datetime.now().strftime("%d.%m.%Y"))
    orm = c2.text_input("🏗️ RO").upper()
    krug = c3.text_input("🔌 Krug")
    kat_col, tip_col = st.columns(2)
    izab_kat = kat_col.selectbox("📁 Kategorija", options=list(app.kategorije_materijala.keys()), key="m_kat")
    tip = tip_col.selectbox("📦 Tip materijala", options=app.kategorije_materijala[izab_kat], key="m_tip")
    
    with st.form("forma_podaci", clear_on_submit=True):
        c4, c5, c6 = st.columns([1, 1, 2])
        kol = c4.number_input("Kolicina", min_value=0.0, step=0.1)
        jed = c5.selectbox("Jedinica", ["m", "kom"])
        nap = c6.text_input("📝 Napomena")
        if st.form_submit_button("💾 SNIMI"):
            if orm and krug:
                app.sacuvaj_u_bazu((dat, orm, krug, tip, kol, jed, nap))
                st.rerun()

# PRIKAZ
with sqlite3.connect(app.db_name) as conn:
    df_prikaz = pd.read_sql_query("SELECT * FROM radovi ORDER BY id DESC", conn)

if not df_prikaz.empty:
    oprema_keywords = ("REGAL", "BREZON", "C-SINA", "LR ")
    mask = df_prikaz['tip'].str.upper().str.contains('|'.join(oprema_keywords))
    df_kab = df_prikaz[~mask]
    s_m = df_kab[df_kab['jed'] == 'm']['kol'].sum()
    s_k = df_kab[df_kab['jed'] == 'kom']['kol'].sum()

    st.metric("UKUPNO METARA KABLA", f"{s_m:.2f} m")
    edited_df = st.data_editor(df_prikaz, use_container_width=True, hide_index=True, num_rows="dynamic")
    
    if st.button("✅ SAČUVAJ IZMENE"):
        app.azuriraj_bazu(edited_df); st.rerun()

    st.divider()
    pdf_out = app.generisi_pdf(edited_df, s_m, s_k)
    st.download_button("📄 PREUZMI PDF IZVESTAJ", bytes(pdf_out), "izvestaj.pdf", "application/pdf")
else:
    st.info("Baza je prazna.")
