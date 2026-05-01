import streamlit as st
import pandas as pd
import sqlite3
import os
import base64
from datetime import datetime

# 1. PODEŠAVANJA
st.set_page_config(page_title="ELEKTRO-LOG BUSINESS", layout="wide")

# Funkcija za logo u aplikaciji
if os.path.exists("elmar.webp"):
    with open("elmar.webp", "rb") as f:
        data = base64.b64encode(f.read()).decode()
    st.markdown(f'<img src="data:image/webp;base64,{data}" width="200">', unsafe_allow_html=True)

st.title("ELEKTRO-LOG BUSINESS v1.0 ⚡")

# 2. BAZA PODATAKA
def init_db():
    conn = sqlite3.connect('elektro_baza.db')
    conn.execute("""CREATE TABLE IF NOT EXISTS radovi 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                  datum TEXT, orman TEXT, opis TEXT, 
                  metara REAL, napomena TEXT)""")
    conn.close()

init_db()

# 3. FORMA ZA UNOS
with st.form("unos_forme", clear_on_submit=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        u_datum = st.date_input("Datum", datetime.now()).strftime("%d.%m.%Y")
        u_orman = st.text_input("Oznaka (RO)").upper()
    with c2:
        u_opis = st.text_input("Strujni krug / Opis")
        u_metara = st.number_input("Količina (m)", min_value=0.0, step=0.1)
    with c3:
        u_napomena = st.text_area("Napomena", height=68)
    
    if st.form_submit_button("💾 SNIMI / DODAJ"):
        if u_orman and u_opis:
            conn = sqlite3.connect('elektro_baza.db')
            conn.execute("INSERT INTO radovi (datum, orman, opis, metara, napomena) VALUES (?,?,?,?,?)", 
                         (u_datum, u_orman, u_opis, u_metara, u_napomena))
            conn.commit()
            conn.close()
            st.success("Sačuvano!")
            st.rerun()
        else:
            st.error("Popunite Oznaku i Strujni krug!")

# 4. PRIKAZ I OBRADA
st.divider()
conn = sqlite3.connect('elektro_baza.db')
df = pd.read_sql_query("SELECT * FROM radovi ORDER BY id DESC", conn)
conn.close()

if not df.empty:
    st.subheader("📋 Pregled radova")
    edited_df = st.data_editor(df, use_container_width=True, hide_index=True, num_rows="dynamic")
    
    if len(edited_df) < len(df):
        conn = sqlite3.connect('elektro_baza.db')
        conn.execute("DELETE FROM radovi")
        edited_df.to_sql('radovi', conn, if_exists='append', index=False)
        conn.commit()
        conn.close()
        st.rerun()

    ukupno = df['metara'].sum()
    st.metric("UKUPNO METARA", f"{ukupno:.2f} m")

    # 5. GENERISANJE IZVEŠTAJA PREMA SLICI
    st.write("---")
    if st.button("💎 GENERIŠI PROFESIONALNI IZVEŠTAJ"):
        logo_base64 = ""
        if os.path.exists("elmar.webp"):
            with open("elmar.webp", "rb") as f:
                logo_base64 = base64.b64encode(f.read()).decode()

        redovi_html = ""
        for i, r in df.iterrows():
            redovi_html += f"""
            <tr>
                <td>{r['datum']}</td>
                <td style="font-weight: bold;">{r['orman']}</td>
                <td>{r['opis']}</td>
                <td style="text-align: center;">{r['metara']:.2f} m</td>
                <td>{r['napomena'] if r['napomena'] else ''}</td>
            </tr>
            """

        izvestaj_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Helvetica', 'Arial', sans-serif; color: #34495e; padding: 40px; line-height: 1.6; }}
                
                /* Header sekcija */
                .header-container {{ display: flex; justify-content: space-between; align-items: flex-start; border-bottom: 2px solid #2c3e50; padding-bottom: 20px; margin-bottom: 40px; }}
                .logo {{ width: 120px; }}
                @media print {{ @page {{ margin: 0; }} body {{ padding: 1.5cm; }} }}
                .header-text {{ text-align: right; }}
                .header-text h1 {{ margin: 0; font-size: 28px; letter-spacing: 4px; color: #2c3e50; text-transform: uppercase; }}
                .header-text p {{ margin: 2px 0; font-size: 12px; color: #7f8c8d; text-transform: uppercase; letter-spacing: 2px; }}
                .header-text .date {{ margin-top: 15px; font-size: 16px; color: #2c3e50; letter-spacing: 1px; }}

                /* Tabela */
                table {{ width: 100%; border-collapse: collapse; margin-bottom: 30px; }}
                th {{ background-color: #2c3e50; color: #ffffff; padding: 12px; text-align: left; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; text-align: center; }}
                td {{ padding: 12px; border-bottom: 1px solid #ecf0f1; font-size: 13px; color: #2c3e50; text-align: center; word-wrap: break-word; }}
                
                /* Posebno pravilo za poslednju kolonu (NAPOMENA) */
                td:last-child {{ 
                    text-align: left;        /* NAPOMENA U LEVO */
                }}

                .kolicina-cell {
                    text-align: center !important;
                }
                
                /* Ukupno sekcija */
                .total-container {{ text-align: right; margin-top: 20px; }}
                .total-label {{ font-size: 14px; color: #7f8c8d; text-transform: uppercase; letter-spacing: 1px; }}
                .total-amount {{ font-size: 32px; font-weight: bold; color: #2c3e50; border-bottom: 4px double #2c3e50; display: inline-block; padding-left: 10px; }}

                /* Futer sa slike */
                .footer {{ 
                    position: fixed; bottom: 30px; left: 0; width: 100%; text-align: center; 
                    background-color: #5dade2; color: white; padding: 8px 0; font-size: 11px; 
                    text-transform: uppercase; letter-spacing: 1px; font-weight: bold;
                }}
            </style>
        </head>
        <body>
            <div class="header-container">
                <img src="data:image/webp;base64,{logo_base64}" class="logo">
                <div class="header-text">
                    <h1>SPECIFIKACIJA IZVEDENE INSTALACIJE</h1>
                    <p>UTORAŠAK MATERIJALA / KABLOVA</p>
                    <p class="date">DATUM: {datetime.now().strftime('%d.%m.%Y')}</p>
                </div>
            </div>

            <table>
                <thead>
                    <tr>
                        <th style="width: 15%;">DATUM</th>
                        <th style="width: 25%;">OZNAKA (RO)</th>
                        <th style="width: 15%;">STRUJNI KRUG </th>
                        <th style="width: 15%; text-align: center;">KOLIČINA</th>
                        <th style="width: 30%;">NAPOMENA</th>
                    </tr>
                </thead>
                <tbody>
                    {redovi_html}
                </tbody>
            </table>

            <div class="total-container">
                <span class="total-label">UKUPNA KOLIČINA:</span>
                <span class="total-amount">{ukupno:.2f} m</span>
            </div>

            <div class="footer">
                ELMAR ELEKTRO-INSTALACIJE &nbsp; | &nbsp; DESIGN VLADE 2026 &nbsp; | &nbsp; INTERNI DOKUMENT
            </div>
        </body>
        </html>
        """
        
        st.download_button(
            label="📩 PREUZMI PDF IZVEŠTAJ (HTML)",
            data=izvestaj_html,
            file_name=f"Specifikacija_{datetime.now().strftime('%d_%m_%Y')}.html",
            mime="text/html"
        )

    # 6. BRISANJE
    st.write("---")
    if st.checkbox("Prikaži opciju za brisanje"):
        if st.button("❌ OBRIŠI SVE"):
            conn = sqlite3.connect('elektro_baza.db')
            conn.execute("DELETE FROM radovi")
            conn.commit(); conn.close()
            st.rerun()
else:
    st.info("Baza je prazna.")
