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
# 2. KLASA ZA PDF (Bez linija, centrirano, izbegnuta UNICODE greška)
# ==============================================================================
class PDFSpec(FPDF):
    def header(self):
        if os.path.exists("elmar.webp"):
            try: self.image("elmar.webp", 10, 8, 33)
            except: pass
        self.set_font("Arial", "B", 15)
        # Koristimo 'S' umesto 'Š' da ne bi pucao PDF bez ttf fonta
        self.cell(0, 10, "UTROSAK MATERIJALA", ln=True, align="R")
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
        
        # Organizacija po kategorijama
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
        pdf.set_fill_color(49, 130, 206) 
        pdf.set_text_color(255)
        pdf.set_font("Arial", "B", 9)
        # Naslovi kolona
        cols = [("Datum", 22), ("RO", 18), ("Krug", 15), ("Tip materijala", 60), ("Kol", 15), ("Jed", 10), ("Napomena", 50)]
        for col_name, width in cols:
            pdf.cell(width, 10, col_name, border=0, align="C", fill=True)
        pdf.ln()

        # Podaci bez linija
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
# 4. INTERFEJS
# ==============================================================================
app = ElektroProUltra()

with st.sidebar:
    st.header("⚙️ SISTEM")
    # BACKUP
    if os.path.exists(app.db_name):
        with open(app.db_name, "rb") as f:
            st.download_button("📥 PREUZMI BACKUP", f, file_name="elektro_baza.db")
    st.divider()
    # RESTORE
    st.subheader("📤 RESTORE")
    f_res = st.file_uploader("Ubaci .db fajl", type="db")
    if f_res:
        if st.button("⚠️ POTVRDI RESTORE"):
            with open(app.db_name, "wb") as f: f.write(f_res.getbuffer())
            st.success("Baza uspesno vracena!")
            st.rerun()
    st.divider()
    # DELETE ALL
    st.subheader("🗑️ RESET")
    potvrda_del = st.checkbox("Potvrdujem brisanje svih podataka")
    if st.button("🔴 OBRIŠI SVE"):
        if potvrda_del:
            app.obrisi_sve()
            st.rerun()
        else:
            st.warning("Prvo stikliraj potvrdu!")

# --- SEKCIJA ZA UNOS ---
with st.expander("📝 UNOS NOVE STAVKE", expanded=True):
    c1, c2, c3 = st.columns(3)
    dat = c1.text_input("📅 Datum", datetime.now().strftime("%d.%m.%Y"))
    orm = c2.text_input("🏗️ RO").upper()
    krug = c3.text_input("🔌 Krug")
    
    # Dinamicki izbor kategorije i tipa
    kat_col, tip_col = st.columns(2)
    izab_kat = kat_col.selectbox("📁 Kategorija", options=list(app.kategorije_materijala.keys()), key="main_kat")
    tip = tip_col.selectbox("📦 Tip materijala", options=app.kategorije_materijala[izab_kat], key="main_tip")
    
    with st.form("forma_podaci", clear_on_submit=True):
        c4, c5, c6 = st.columns([1, 1, 2])
        kol = c4.number_input("Kolicina", min_value=0.0, step=0.1)
        jed = c5.selectbox("Jedinica", ["m", "kom"])
        nap = c6.text_input("📝 Napomena")
        
        if st.form_submit_button("💾 SNIMI U BAZU"):
            if orm and krug:
                app.sacuvaj_u_bazu((dat, orm, krug, tip, kol, jed, nap))
                st.rerun()
            else:
                st.error("Popuni RO i Krug!")

# --- PRIKAZ I OBRADA PODATAKA ---
with sqlite3.connect(app.db_name) as conn:
    df_prikaz = pd.read_sql_query("SELECT * FROM radovi ORDER BY id DESC", conn)

if not df_prikaz.empty:
    # Metrika (Kalkulacija)
    oprema_keywords = ("REGAL", "BREZON", "C-SINA", "LR ")
    mask = df_prikaz['tip'].str.upper().str.contains('|'.join(oprema_keywords))
    df_kablovska = df_prikaz[~mask]
    s_m = df_kablovska[df_kablovska['jed'] == 'm']['kol'].sum()
    s_k = df_kablovska[df_kablovska['jed'] == 'kom']['kol'].sum()

    st.metric("UKUPNO METARA KABLA", f"{s_m:.2f} m")
    
    # Tabela za izmenu
    edited_df = st.data_editor(df_prikaz, use_container_width=True, hide_index=True, num_rows="dynamic")
    
    if st.button("✅ SAČUVAJ IZMENE U TABELI"):
        app.azuriraj_bazu(edited_df)
        st.success("Podaci azurirani!")
        st.rerun()

    st.divider()
    # Generisanje PDF-a
    pdf_out = app.generisi_pdf(edited_df, s_m, s_k)
    st.download_button("📄 PREUZMI PDF IZVESTAJ", bytes(pdf_out), "izvestaj.pdf", "application/pdf")
else:
    st.info("Baza je trenutno prazna.")
