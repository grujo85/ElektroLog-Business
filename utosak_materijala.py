import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import base64
import os

# 1. PODEŠAVANJA STRANICE I DIZAJN
st.set_page_config(page_title="ELEKTRO-LOG BUSINESS", layout="wide")

st.markdown("""
    <style>
    .main { background-color: #f0f2f5; }
    .stButton>button { width: 100%; background-color: #3182ce; color: white; border-radius: 5px; }
    .total-box { padding: 20px; background-color: white; border-radius: 10px; border-left: 5px solid #3182ce; }
    </style>
    """, unsafe_allow_html=True)

# 2. FUNKCIJE ZA BAZU
def init_db():
    conn = sqlite3.connect('elektro_baza.db')
    conn.execute("""CREATE TABLE IF NOT EXISTS radovi 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  datum TEXT, orman TEXT, opis TEXT, 
                  metara REAL, napomena TEXT)""")
    conn.close()

def dodaj_u_bazu(datum, orman, opis, metara, napomena):
    conn = sqlite3.connect('elektro_baza.db')
    conn.execute("INSERT INTO radovi (datum, orman, opis, metara, napomena) VALUES (?,?,?,?,?)", 
                 (datum, orman.upper(), opis, metara, napomena))
    conn.commit()
    conn.close()

init_db()

# 3. LOGO (Pokušaj učitavanja elmar.webp)
logo_base64 = ""
if os.path.exists("elmar.webp"):
    with open("elmar.webp", "rb") as f:
        logo_base64 = base64.b64encode(f.read()).decode()

# 4. INTERFEJS - NASLOV I FORMA
st.title("⚡ ELEKTRO-LOG BUSINESS v1.0")
st.write("Aplikacija za evidenciju elektro-instalaterskih radova")

with st.container():
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        u_datum = st.date_input("Datum", datetime.now()).strftime("%d.%m.%Y")
        u_orman = st.text_input("Orman (RO)")
    with col2:
        u_opis = st.text_input("Strujni krug (npr. P-12)")
        u_metara = st.number_input("Količina (m)", min_value=0.0, step=0.1)
    with col3:
        u_napomena = st.text_area("Napomena", height=68)

    if st.button("💾 SNIMI / DODAJ PODATKE"):
        if u_orman and u_opis:
            dodaj_u_bazu(u_datum, u_orman, u_opis, u_metara, u_napomena)
            st.success(f"Uspešno dodato: {u_orman} - {u_opis}")
        else:
            st.error("Popunite Orman i Strujni krug!")

st.divider()

# 5. PRIKAZ PODATAKA
conn = sqlite3.connect('elektro_baza.db')
df = pd.read_sql_query("SELECT * FROM radovi ORDER BY id DESC", conn)
conn.close()

if not df.empty:
    c1, c2 = st.columns([3, 1])
    with c1:
        st.subheader("Pregled unetih stavki")
        # Dozvoljavamo brisanje i izmenu direktno u tabeli na sajtu
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    with c2:
        st.subheader("Statistika")
        ukupno = df['metara'].sum()
        st.markdown(f"""
            <div class="total-box">
                <p style='margin:0; color:#4a5568;'>UKUPNA METRAŽA</p>
                <h2 style='margin:0; color:#2d3748;'>{ukupno:.2f} m</h2>
            </div>
            """, unsafe_allow_html=True)
        
        # Dugme za brisanje cele baze (oprezno!)
        if st.checkbox("Omogući brisanje baze"):
            if st.button("❌ OBRIŠI SVE PODATKE"):
                conn = sqlite3.connect('elektro_baza.db')
                conn.execute("DELETE FROM radovi")
                conn.commit()
                conn.close()
                st.rerun()

# 6. GENERISANJE IZVEŠTAJA (HTML/PDF format)
if not df.empty:
    if st.button("💎 GENERIŠI HTML IZVEŠTAJ ZA ŠTAMPU"):
        rows_html = "".join([f"<tr><td>{r['datum']}</td><td>{r['orman']}</td><td>{r['opis']}</td><td>{r['metara']} m</td><td>{r['napomena']}</td></tr>" 
                             for _, r in df.iterrows()])
        
        html_code = f"""
        <html>
        <head><meta charset="UTF-8"><style>
            body {{ font-family: sans-serif; padding: 20px; }}
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
            th {{ background: #2d3748; color: white; padding: 10px; text-align: left; }}
            td {{ border-bottom: 1px solid #ddd; padding: 8px; }}
            .header {{ display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #3182ce; }}
        </style></head>
        <body>
            <div class="header">
                <h2>SPECIFIKACIJA RADOVA</h2>
                <p>Datum: {datetime.now().strftime('%d.%m.%Y')}</p>
            </div>
            <table>
                <thead><tr><th>Datum</th><th>Orman</th><th>Krug</th><th>Metara</th><th>Napomena</th></tr></thead>
                <tbody>{rows_html}</tbody>
            </table>
            <h3 style="text-align:right;">UKUPNO: {df['metara'].sum():.2f} m</h3>
        </body>
        </html>
        """
        st.download_button("Preuzmi izveštaj", html_code, file_name="Izvestaj.html", mime="text/html")

else:
    st.info("Baza je trenutno prazna. Unesite prve podatke iznad.")
