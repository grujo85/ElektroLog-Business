import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import os
import base64

# ==============================================================================
# 1. KONFIGURACIJA I STILIZACIJA (Sve tvoje postavke, prilagođene za web/tel)
# ==============================================================================
st.set_page_config(
    page_title="ELEKTRO-LOG BUSINESS v1.0",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS da zadržimo onaj tvoj "Business" izgled (plave nijanse)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #3182ce; color: white; }
    .stTextInput>div>div>input { text-transform: uppercase; }
    </style>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. GLAVNA KLASA (Tvoja klasa ElektroProUltra - Identitčna tvojoj logici)
# ==============================================================================
class ElektroProUltra:
    def __init__(self):
        self.db_name = "elektro_baza.db"
        self.putanja_logotipa = "elmar.webp"
        self.logo_data = self.ucitaj_logo_u_base64()
        
        # TVOJA LISTA MATERIJALA - NIŠTA NIJE ODUZETO
        self.tipovi = [
            "Brezon M8", "Brezon M10", "C-šina 30x20", "C-šina 41x21", 
            "Regal 50", "Regal 100", "Regal 150", "Regal 200", "Regal 300", "Regal 400", "Regal 500", "Regal 600",
            "LR Krivina", "LR T-komad", "Poklopac regala",
            "PP-Y 2x1.5", "PP-Y 3x1.5", "PP-Y 3x2.5", "PP-Y 3x4", "PP-Y 4x1.5", "PP-Y 4x2.5", "PP-Y 4x4",
            "PP-Y 5x1.5", "PP-Y 5x2.5", "PP-Y 5x4", "PP-Y 5x6", "PP-Y 5x10", "PP-Y 5x16",
            "N2XH-J 3x1.5", "N2XH-J 3x2.5", "N2XH-J 3x4", "N2XH-J 5x1.5", "N2XH-J 5x2.5", "N2XH-J 5x4",
            "N2XH-J 5x6", "N2XH-J 5x10", "N2XH-J 5x16", "N2XH-J 5x25", "N2XH-J 5x35", "N2XH-J 5x50",
            "NHXH FE180 3x1.5", "NHXH FE180 3x2.5", "NHXH FE180 5x1.5", "NHXH FE180 5x2.5", "NHXH FE180 5x4", "NHXH FE180 5x6",
            "PP00 3x1.5", "PP00 3x2.5", "PP00 4x1.5", "PP00 4x2.5", "PP00 4x4", "PP00 4x6", "PP00 4x10",
            "PP00 4x16", "PP00 4x25", "PP00 4x35", "PP00 4x50", "PP00 4x70", "PP00 4x95", "PP00 4x120",
            "PP00 4x150", "PP00 4x185", "PP00 4x240", "PP00 5x1.5", "PP00 5x2.5", "PP00 5x4", "PP00 5x6",
            "PP00 5x10", "PP00 5x16", 
            "PP00-A (Al) 4x16", "PP00-A 4x25", "PP00-A 4x35", "PP00-A 4x50", 
            "PP00-A 4x70", "PP00-A 4x95", "PP00-A 4x120", "PP00-A 4x150", "PP00-A 4x240",
            "H07RN-F (GG/J) 3x1.5", "H07RN-F 3x2.5", "H07RN-F 5x1.5", "H07RN-F 5x2.5", "H07RN-F 5x4", 
            "H07RN-F 5x6", "H07RN-F 5x10", "H07RN-F 5x16", 
            "LiYCY 2x0.75", "LiYCY 3x0.75", "LiYCY 4x0.75", "LiYCY 5x0.75", "LiYCY 7x0.75", "LiYCY 12x0.75",
            "P/F (H07V-K) 0.75", "P/F 1.5", "P/F 2.5", "P/F 4", "P/F 6", "P/F 10", "P/F 16", "P/F 25", "P/F 35", "P/F 50",
            "P (H07V-U) 1.5", "P 2.5", "P 4", "P 6", 
            "SKS 2x16", "SKS 4x16", "SKS 4x25",
            "UTP Cat5e", "FTP Cat6", "SFTP Cat7", "Koaksijalni RG6", "Koaksijalni RG11",
            "Alarmni 4x0.22", "Alarmni 6x0.22", "Alarmni 8x0.22", "JH(St)H 2x2x0.8", "JH(St)H 4x2x0.8",
            "Solarni 4mm2", "Solarni 6mm2"
        ]
        self.kreiraj_bazu()

    def ucitaj_logo_u_base64(self):
        if os.path.exists(self.putanja_logotipa):
            try:
                with open(self.putanja_logotipa, "rb") as f: 
                    return base64.b64encode(f.read()).decode('utf-8')
            except: return ""
        return ""

    def kreiraj_bazu(self):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("""CREATE TABLE IF NOT EXISTS radovi 
                (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                datum TEXT, orman TEXT, opis TEXT, tip TEXT, 
                kol REAL, jed TEXT, napomena TEXT)""")

    def sacuvaj_u_bazu(self, d):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("INSERT INTO radovi (datum, orman, opis, tip, kol, jed, napomena) VALUES (?,?,?,?,?,?,?)", d)

    def obrisi_stavku(self, id_reda):
        with sqlite3.connect(self.db_name) as conn:
            conn.execute("DELETE FROM radovi WHERE id=?", (id_reda,))

    # TVOJ ORIGINALNI HTML IZVEŠTAJ - KOMPLETAN STIL
    def generisi_html(self, df, tm, tk):
        # Povećan logo na 120px i dodat blend mode da se stopi sa pozadinom
        logo_img = f'<img src="data:image/webp;base64,{self.logo_data}" style="height:120px; mix-blend-mode: multiply;">' if self.logo_data else ""
        rows = ""
        for _, r in df.iterrows():
            rows += f"<tr><td>{r['datum']}</td><td>{r['orman']}</td><td>{r['opis']}</td><td><b>{r['tip']}</b></td><td>{r['kol']} {r['jed']}</td><td>{r['napomena']}</td></tr>"
        
        return f"""
        <html><head><meta charset='UTF-8'><style>
            body {{ font-family: 'Segoe UI', sans-serif; margin: 30px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ background: #3182ce; color: white; padding: 10px; }}
            td {{ border-bottom: 1px solid #ddd; padding: 10px; text-align: center; }}
            
            /* STIL ZA SUMU (METRAŽU) */
            .summary-box {{ 
                margin-top: 20px; 
                text-align: right; 
                font-size: 18px; 
                font-weight: bold; 
            }}
            
            /* STIL ZA TVOJ POTPIS NA DNU */
            .footer {{ 
                margin-top: 60px; 
                text-align: center; 
                font-size: 11px; 
                color: #888888; 
                border-top: 1px solid #eeeeee; 
                padding-top: 15px; 
            }}
        </style></head><body>
            <div class='header'>
                {logo_img} 
                <div style="flex-grow: 1;">
                    <h1 style="margin:0; text-align: right;">SPECIFIKACIJA RADOVA</h1>
                    <p style="margin:0; color: #4a5568; text-align: right; width: 100%;">
                        Datum: {datetime.now().strftime('%d.%m.%Y')}
                    </p>
                </div>
            </div>
            
            <table>
                <tr><th>Datum</th><th>Orman</th><th>Krug</th><th>Tip</th><th>Kol</th><th>Napomena</th></tr>
                {rows}
            </table>
            
            <div class='summary-box'>UKUPNO KABLOVA: {tm:.2f} m | {int(tk)} kom</div>
            
            <!-- TVOJ SIVI CENTRIRANI FOOTER -->
            <div class="footer">
                ELMAR ELEKTRO-INSTALACIJE &nbsp; | &nbsp; DESIGN VLADE 2026 &nbsp; | &nbsp; INTERNI DOKUMENT
            </div>
        </body></html>"""

# ==============================================================================
# 3. INTERFEJS (Streamlit - Dodatna funkcionalnost za mobilni)
# ==============================================================================
app = ElektroProUltra()

# --- PRIKAZ LOGA NA VRHU ---
if app.logo_data:
    st.markdown(f'<div style="text-align: center;"><img src="data:image/webp;base64,{app.logo_data}" style="max-height: 100px;"></div>', unsafe_allow_html=True)

# Gornji panel: Unos podataka
with st.expander("📝 UNOS NOVE STAVKE", expanded=True):
    with st.form("forma_unos", clear_on_submit=True):
        c1, c2, c3 = st.columns([1, 1, 1])
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
                st.success(f"Dodato: {tip} u {orm}")
                st.rerun()
            else:
                st.error("Polja Orman i Strujni krug su obavezna!")

# Donji panel: Prikaz i statistika
with sqlite3.connect(app.db_name) as conn:
    df_prikaz = pd.read_sql_query("SELECT * FROM radovi ORDER BY id DESC", conn)

if not df_prikaz.empty:
    # Tvoja logika filtriranja nosača za ukupnu metražu
    oprema = ("REGAL", "BREZON", "C-ŠINA", "LR ", "POKLOPAC")
    mask = df_prikaz['tip'].str.upper().str.contains('|'.join(oprema))
    df_kablovska = df_prikaz[~mask]
    
    suma_m = df_kablovska[df_kablovska['jed'] == 'm']['kol'].sum()
    suma_k = df_kablovska[df_kablovska['jed'] == 'kom']['kol'].sum()

    # Veliki vidljivi brojevi (odlično za telefon)
    col_m, col_k = st.columns(2)
    col_m.metric("UKUPNO METARA", f"{suma_m:.2f} m")
    col_k.metric("UKUPNO KOMADA", f"{int(suma_k)} kom")

    st.markdown("### 📋 Pregled unetih stavki")
    st.dataframe(df_prikaz, use_container_width=True, hide_index=True)

    # Akcije ispod tabele
    col_btn1, col_btn2, col_btn3 = st.columns(3)
    
    with col_btn1:
        html_izv = app.generisi_html(df_prikaz, suma_m, suma_k)
        st.download_button("📥 PREUZMI HTML", html_izv, "izvestaj.html", "text/html")
        
    with col_btn2:
        if st.button("🗑️ OBRIŠI POSLEDNJI"):
            zadnji_id = df_prikaz['id'].max()
            app.obrisi_stavku(zadnji_id)
            st.rerun()

    with col_btn3:
        id_del = st.number_input("Obriši ID:", min_value=0, step=1)
        if st.button("❌ OBRIŠI PO ID"):
            app.obrisi_stavku(id_del)
            st.rerun()
else:
    st.info("Baza je trenutno prazna. Unesite prve podatke.")
