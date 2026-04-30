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

    # 5. MODERAN I PREGLEDAN IZVEŠTAJ (SVAKO POLJE OZNAČENO)
    st.write("---")
    if st.button("💎 GENERIŠI DETALJAN IZVEŠTAJ"):
        # 1. Priprema logotipa
        logo_data = ""
        if os.path.exists("elmar.webp"):
            with open("elmar.webp", "rb") as f:
                logo_base64 = base64.b64encode(f.read()).decode()
            logo_data = f'<img src="data:image/webp;base64,{logo_base64}" style="width:160px;">'

        # 2. Pravljenje stavki sa jasnim oznakama šta je šta
        stavke_html = ""
        for _, r in df.iterrows():
            stavke_html += f"""
            <div style="border: 1px solid #333; padding: 15px; margin-bottom: 20px; border-radius: 5px; background-color: #ffffff;">
                <div style="display: flex; justify-content: space-between; border-bottom: 1px solid #eee; padding-bottom: 8px; margin-bottom: 10px;">
                    <span style="font-size: 14px; color: #555;"><b>DATUM:</b> {r['datum']}</span>
                    <span style="font-size: 14px; color: #555;"><b>RO:</b> {r['orman']}</span>
                </div>
                <div style="margin-bottom: 8px;">
                    <span style="color: #1a1a1a; font-size: 16px;"><b>OPIS / KRUG:</b> {r['opis']}</span>
                </div>
                <div style="margin-bottom: 8px;">
                    <span style="color: #000; font-size: 18px;"><b>KOLIČINA:</b> <span style="background: #ffff00; padding: 2px 5px;">{r['metara']:.2f} m</span></span>
                </div>
                <div style="color: #666; font-size: 14px; border-top: 1px dashed #ccc; padding-top: 5px;">
                    <b>NAPOMENA:</b> {r['napomena'] if r['napomena'] else '/'}
                </div>
            </div>
            """

        # 3. HTML Dokument
        izvestaj_html = f"""
        <!DOCTYPE html>
        <html lang="sr">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Arial', sans-serif; padding: 50px; background-color: #f5f5f5; color: #333; }}
                .page {{ background: white; padding: 40px; box-shadow: 0 0 10px rgba(0,0,0,0.1); max-width: 800px; margin: auto; }}
                .header {{ text-align: center; border-bottom: 4px solid #000; padding-bottom: 20px; margin-bottom: 40px; }}
                .total {{ background: #222; color: white; padding: 25px; text-align: right; margin-top: 30px; border-radius: 5px; }}
                h1 {{ margin: 10px 0; letter-spacing: 1px; }}
            </style>
        </head>
        <body>
            <div class="page">
                <div class="header">
                    {logo_data}
                    <h1>SPECIFIKACIJA RADOVA</h1>
                    <p style="font-size: 18px; color: #555;">ELMAR - Elektro-instalacije</p>
                </div>

                {stavke_html}

                <div class="total">
                    <span style="font-size: 16px; opacity: 0.8;">UKUPNO ZA NAPLATU:</span><br>
                    <span style="font-size: 36px; font-weight: bold;">{ukupno:.2f} m</span>
                </div>

                <p style="text-align: center; margin-top: 40px; font-size: 12px; color: #999;">
                    Dokument je generisan automatski: {datetime.now().strftime("%d.%m.%Y. u %H:%M")}
                </p>
            </div>
        </body>
        </html>
        """
        
        st.download_button(
            label="📩 PREUZMI MODERAN IZVEŠTAJ",
            data=izvestaj_html,
            file_name=f"Elmar_Specifikacija_{datetime.now().strftime('%d_%m_%Y')}.html",
            mime="text/html"
        )
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
