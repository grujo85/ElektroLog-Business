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
    st.info("💡 Brisanje jednog reda: Klikni na kvadratić levo od reda i pritisni 'Delete' na tastaturi.")
    
    # Tabela u kojoj možeš da brišeš jedan po jedan red
    edited_df = st.data_editor(
        df,
        use_container_width=True,
        hide_index=True,
        num_rows="dynamic",
        key="tabela_editor"
    )
    
    # Ako si obrisao red u tabeli, sačuvaj to u bazu
    if len(edited_df) < len(df):
        conn = sqlite3.connect('elektro_baza.db')
        conn.execute("DELETE FROM radovi")
        edited_df.to_sql('radovi', conn, if_exists='append', index=False)
        conn.commit()
        conn.close()
        st.rerun()

    ukupno = df['metara'].sum()
    st.metric("UKUPNO METARA", f"{ukupno:.2f} m")

    # 5. MODERAN IZVEŠTAJ (BEZ TABELE)
    st.write("---")
    if st.button("💎 GENERIŠI MODERAN IZVEŠTAJ"):
        # Pripremamo logo
        logo_html = ""
        if os.path.exists("elmar.webp"):
            with open("elmar.webp", "rb") as f:
                kodiranje = base64.b64encode(f.read()).decode()
            logo_html = f'<img src="data:image/webp;base64,{kodiranje}" width="120">'

        # Pravimo kartice za svaki unos
        stavke_html = ""
        for _, r in df.iterrows():
            stavke_html += f"""
            <div style="border-bottom: 1px solid #eee; padding: 15px 0;">
                <div style="display: flex; justify-content: space-between;">
                    <span style="font-weight: bold; color: #333;">{r['orman']} &nbsp; | &nbsp; {r['opis']}</span>
                    <span style="color: #666;">{r['datum']}</span>
                </div>
                <div style="margin-top: 5px; color: #444;">
                    <strong>{r['metara']:.2f} m</strong> <span style="margin-left: 20px; font-style: italic; color: #888;">{r['napomena'] if r['napomena'] else ''}</span>
                </div>
            </div>
            """

        html = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; color: #333; line-height: 1.6; }}
                .container {{ max-width: 800px; margin: auto; padding: 20px; }}
                .header {{ text-align: center; margin-bottom: 40px; border-bottom: 2px solid #333; padding-bottom: 20px; }}
                .footer {{ margin-top: 50px; text-align: center; font-size: 12px; color: #999; }}
                .total-box {{ background: #f9f9f9; padding: 20px; text-align: right; margin-top: 30px; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    {logo_html}
                    <h1 style="margin-top: 10px; letter-spacing: 2px;">SPECIFIKACIJA RADOVA</h1>
                    <p>Elektro-instalacije Elmar</p>
                </div>
                
                {stavke_html}

                <div class="total-box">
                    <span style="font-size: 18px;">UKUPAN UTROŠAK:</span>
                    <br>
                    <span style="font-size: 32px; font-weight: bold; color: #000;">{ukupno:.2f} m</span>
                </div>

                <div class="footer">
                    Izveštaj generisan dana {datetime.now().strftime("%d.%m.%Y u %H:%M")}
                </div>
            </div>
        </body>
        </html>
        """
        st.download_button("Preuzmi moderan izveštaj", html, file_name=f"Specifikacija_{datetime.now().strftime('%d_%m')}.html", mime="text/html")
    # 6. BRISANJE CELE BAZE - VRACENO
    st.write("---")
    if st.checkbox("Prikaži opciju za brisanje cele baze"):
        if st.button("❌ OBRIŠI SVE PODATKE IZ BAZE"):
            conn = sqlite3.connect('elektro_baza.db')
            conn.execute("DELETE FROM radovi")
            conn.commit()
            conn.close()
            st.rerun()
else:
    st.info("Baza je prazna.")
