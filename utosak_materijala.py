import streamlit as st
import pandas as pd
import sqlite3
import os
import base64
from datetime import datetime

# 1. PODEŠAVANJA I LOGO
st.set_page_config(page_title="ELEKTRO-LOG BUSINESS", layout="wide")

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
        u_orman = st.text_input("Orman (RO)").upper()
    with c2:
        u_opis = st.text_input("Strujni krug")
        u_metara = st.number_input("Metara (m)", min_value=0.0, step=0.1)
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
            st.error("Popunite Orman i Strujni krug!")

# 4. PRIKAZ, POJEDINAČNO BRISANJE I UKUPNO
st.divider()
conn = sqlite3.connect('elektro_baza.db')
df = pd.read_sql_query("SELECT * FROM radovi ORDER BY id DESC", conn)
conn.close()

if not df.empty:
    st.subheader("📋 Pregled radova")
    st.info("💡 Brisanje jednog reda: Selektuj red i pritisni Delete.")
    
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        key="tabela_editor"
    )
    
    if len(edited_df) < len(df):
        conn = sqlite3.connect('elektro_baza.db')
        conn.execute("DELETE FROM radovi")
        edited_df.to_sql('radovi', conn, if_exists='append', index=False)
        conn.commit()
        conn.close()
        st.rerun()

    ukupno = df['metara'].sum()
    st.metric("UKUPNO METARA", f"{ukupno:.2f} m")

    # 5. PROFESIONALNI IZVEŠTAJ
    st.write("---")
    if st.button("💎 GENERIŠI PROFESIONALNI IZVEŠTAJ"):
        logo_data = ""
        if os.path.exists("elmar.webp"):
            with open("elmar.webp", "rb") as f:
                logo_base64 = base64.b64encode(f.read()).decode()
            logo_data = f'<img src="data:image/webp;base64,{logo_base64}" style="height:80px;">'

        redovi_html = ""
        for i, r in df.iterrows():
            bg_color = "#f9f9f9" if i % 2 == 0 else "#ffffff"
            redovi_html += f"""
            <tr style="background-color: {bg_color}; border-bottom: 1px solid #eee;">
                <td style="padding: 8px 12px; font-size: 12px;">{r['datum']}</td>
                <td style="padding: 8px 12px; font-weight: 600; text-transform: uppercase;">{r['orman']}</td>
                <td style="padding: 8px 12px;">{r['opis']}</td>
                <td style="padding: 8px 12px; text-align: right;">{r['metara']:.2f} m</td>
                <td style="padding: 8px 12px; font-style: italic; color: #666;">{r['napomena'] if r['napomena'] else ''}</td>
            </tr>"""

        izvestaj_html = f"""
        <html>
        <head><meta charset="UTF-8"><style>
            body {{ font-family: Arial, sans-serif; color: #333; }}
            .header {{ border-bottom: 2px solid #2c3e50; padding-bottom: 10px; margin-bottom: 20px; }}
            table {{ width: 100%; border-collapse: collapse; }}
            th {{ background: #2c3e50; color: white; padding: 10px; text-align: left; font-size: 12px; }}
            td {{ padding: 8px; border-bottom: 1px solid #eee; }}
            .total {{ text-align: right; font-size: 20px; font-weight: bold; margin-top: 20px; }}
        </style></head>
        <body>
            <div class="header">
                {logo_data}
                <div style="text-align:right;"><h2>Specifikacija</h2><p>Datum: {datetime.now().strftime('%d.%m.%Y')}</p></div>
            </div>
            <table>
                <thead><tr><th>Datum</th><th>Orman</th><th>Strujni krug</th><th style="text-align:right;">Količina</th><th>Napomena</th></tr></thead>
                <tbody>{redovi_html}</tbody>
            </table>
            <div class="total">UKUPNO: {ukupno:.2f} m</div>
        </body>
        </html>"""
        
        st.download_button("📩 PREUZMI IZVEŠTAJ", data=izvestaj_html, file_name="Specifikacija.html", mime="text/html")

    # 6. BRISANJE BAZE
    st.write("---")
    if st.checkbox("Prikaži opciju za brisanje cele baze"):
        if st.button("❌ OBRIŠI SVE PODATKE"):
            conn = sqlite3.connect('elektro_baza.db')
            conn.execute("DELETE FROM radovi")
            conn.commit()
            conn.close()
            st.rerun()
else:
    st.info("Baza je prazna.")
