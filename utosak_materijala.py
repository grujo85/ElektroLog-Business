import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
from fpdf import FPDF

# ==============================================================================
# 1. KONFIGURACIJA I STILIZACIJA
# ==============================================================================
st.set_page_config(
    page_title="ELEKTRO-LOG BUSINESS v1.1",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #3182ce; color: white; }
    .stTextInput>div>div>input { text-transform: uppercase; }
    [data-testid="stMetricValue"] { font-size: 24px; color: #3182ce; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. KLASA ZA PDF (Centriran tekst sa Napomenom)
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
        self.tipovi = [
            "Brezon M8", "Brezon M10", "C-šina 30x20", "C-šina 41x21", 
            "Regal 50", "Regal 100", "Regal 150", "Regal 200", "Regal 300", "Regal 400", "Regal 500", "Regal 600",
            "LR Krivina", "LR T-komad", "Poklopac regala",
            "PP-Y 3x1.5", "PP-Y 3x2.5", "PP-Y 5x1.5", "PP-Y 5x2.5", "PP-Y 5x4",
            "N2XH-J 3x1.5", "N2XH-J 3x2.5", "N2XH-J 5x1.5", "N2XH-J 5x2.5", "N2XH-J 5x4", "N2XH-J 5x6",
            "PP00 4x16", "PP00 4x25", "PP00 4x35", "PP00 4x50", "PP00 4x70",
            "LiYCY 2x0.75", "UTP Cat5e", "FTP Cat6", "Solarni 6mm2"
        ]
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

    def obrisi_stavku(self, id_reda):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("DELETE FROM radovi WHERE id=?", (id_reda,))

    def generisi_pdf(self, df, tm, tk):
        pdf = PDFSpec()
        pdf.add_page()
        
        # Plavo zaglavlje (ovde ostavljamo border=0 da nema linija ni oko naslova)
        pdf.set_fill_color(49, 130, 206) 
        pdf.set_text_color(255)
        pdf.set_font("Arial", "B", 9)
        
        cols = [
            ("Datum", 22), ("RO", 18), ("Krug", 15), 
            ("Tip materijala", 60), ("Kol", 15), ("Jed", 10), ("Napomena", 50)
        ]
        
        for col_name, width in cols:
            # border=0 uklanja linije
            pdf.cell(width, 10, col_name, border=0, align="C", fill=True)
        pdf.ln()

        # Podaci - Centrirani, BEZ LINIJA
        pdf.set_text_color(0)
        pdf.set_font("Arial", "", 8)
        
        df_clean = df.dropna(subset=['datum', 'orman', 'tip'])

        for _, r in df_clean.iterrows():
            # Svuda menjamo border=1 u border=0
            pdf.cell(22, 8, str(r['datum']), border=0, align="C")
            pdf.cell(18, 8, str(r['orman']), border=0, align="C")
            pdf.cell(15, 8, str(r['opis']), border=0, align="C")
            pdf.cell(60, 8, str(r['tip']), border=0, align="C")
            pdf.cell(15, 8, str(r['kol']), border=0, align="C")
            pdf.cell(10, 8, str(r['jed']), border=0, align="C")
            
            nap = str(r['napomena']) if r['napomena'] and str(r['napomena']) != 'None' else ""
            pdf.cell(50, 8, nap, border=0, align="C")
            pdf.ln()
            
            # Opciono: Možeš dodati tanku sivu liniju ispod svakog reda za bolju preglednost
            # pdf.set_draw_color(230, 230, 230)
            # pdf.line(10, pdf.get_y(), 200, pdf.get_y())

        pdf.ln(5)
        pdf.set_font("Arial", "B", 11)
        pdf.cell(0, 10, f"UKUPNO KABLOVA: {tm:.2f} m | {int(tk)} kom", ln=True, align="R")
        
        return pdf.output()

# ==============================================================================
# 4. INTERFEJS
# ==============================================================================
app = ElektroProUltra()

# SIDEBAR
with st.sidebar:
    st.header("⚙️ SISTEM")
    if os.path.exists(app.db_name):
        with open(app.db_name, "rb") as f:
            st.download_button("📥 BACKUP BAZE (.db)", f, file_name=f"backup_{datetime.now().strftime('%Y%m%d')}.db")

# UNOS NOVE STAVKE
with st.expander("📝 UNOS NOVE STAVKE", expanded=False):
    with st.form("forma_unos", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        dat = c1.text_input("📅 Datum", datetime.now().strftime("%d.%m.%Y"))
        orm = c2.text_input("🏗️ Orman (RO)").upper()
        krug = c3.text_input("🔌 Strujni krug")
        tip = st.selectbox("📦 Tip materijala", app.tipovi)
        c4, c5, c6 = st.columns([1, 1, 2])
        kol = c4.number_input("Količina", min_value=0.0, step=0.1)
        jed = c5.selectbox("Jedinica", ["m", "kom"])
        nap = c6.text_input("📝 Napomena")
        if st.form_submit_button("💾 SNIMI U BAZU"):
            if orm and krug:
                app.sacuvaj_u_bazu((dat, orm, krug, tip, kol, jed, nap))
                st.rerun()

# RAD SA PODACIMA
with sqlite3.connect(app.db_name) as conn:
    df_prikaz = pd.read_sql_query("SELECT * FROM radovi ORDER BY id DESC", conn)

if not df_prikaz.empty:
    # Metrika
    oprema = ("REGAL", "BREZON", "C-ŠINA", "LR ", "POKLOPAC")
    mask = df_prikaz['tip'].str.upper().str.contains('|'.join(oprema))
    df_kablovska = df_prikaz[~mask]
    suma_m = df_kablovska[df_kablovska['jed'] == 'm']['kol'].sum()
    suma_k = df_kablovska[df_kablovska['jed'] == 'kom']['kol'].sum()

    col_m, col_k = st.columns(2)
    col_m.metric("UKUPNO METARA", f"{suma_m:.2f} m")
    col_k.metric("UKUPNO KOMADA", f"{int(suma_k)} kom")

    st.markdown("### ✏️ Izmena podataka")
    edited_df = st.data_editor(
        df_prikaz, 
        use_container_width=True, 
        hide_index=True,
        num_rows="dynamic"
    )

    if st.button("✅ SAČUVAJ SVE IZMENE U TABELI"):
        app.azuriraj_bazu(edited_df)
        st.success("Baza je ažurirana!")
        st.rerun()

    st.divider()
    c_pdf, c_del = st.columns([1, 1])
    
    with c_pdf:
        # Rešen IndentationError i dodat PDF download
        pdf_output = app.generisi_pdf(edited_df, suma_m, suma_k)
        pdf_bytes = bytes(pdf_output) 
        st.download_button("📄 PREUZMI PDF IZVEŠTAJ", pdf_bytes, "izvestaj.pdf", "application/pdf")
        
    with c_del:
        if st.button("🗑️ OBRIŠI POSLEDNJI UNOS"):
            app.obrisi_stavku(df_prikaz['id'].max())
            st.rerun()
else:
    st.info("Baza je prazna.")
