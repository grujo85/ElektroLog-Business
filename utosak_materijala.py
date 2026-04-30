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

   # 5. MODERNA TABELA BEZ GRUBIH LINIJA
    st.write("---")
    if st.button("💎 GENERIŠI ČIST IZVEŠTAJ"):
        # 1. Priprema logotipa
        logo_data = ""
        if os.path.exists("elmar.webp"):
            with open("elmar.webp", "rb") as f:
                logo_base64 = base64.b64encode(f.read()).decode()
            logo_data = f'<img src="data:image/webp;base64,{logo_base64}" style="width:140px;">'

        # 2. Pravljenje redova (čist dizajn)
        redovi_html = ""
        for _, r in df.iterrows():
            redovi_html += f"""
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 12px; color: #666;">{r['datum']}</td>
                <td style="padding: 12px; font-weight: bold;">{r['orman']}</td>
                <td style="padding: 12px;">{r['opis']}</td>
                <td style="padding: 12px; text-align: right; font-weight: bold;">{r['metara']:.2f} m</td>
                <td style="padding: 12px; color: #888; font-size: 13px;">{r['napomena'] if r['napomena'] else ''}</td>
            </tr>
            """

        # 3. HTML Dokument
        izvestaj_html = f"""
        <!DOCTYPE html>
        <html lang="sr">
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: 'Helvetica', Arial, sans-serif; padding: 40px; color: #333; }}
                .container {{ max-width: 900px; margin: auto; }}
                .header {{ text-align: center; margin-bottom: 50px; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                th {{ text-align: left; padding: 12px; border-bottom: 2px solid #333; text-transform: uppercase; font-size: 13px; color: #000; }}
                .total-section {{ margin-top: 30px; border-top: 2px solid #000; padding-top: 15px; text-align: right; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    {logo_data}
                    <h2 style="margin-top: 15px; font-weight: 300; letter-spacing: 1px;">SPECIFIKACIJA RADOVA</h2>
                </div>

                <table>
                    <thead>
                        <tr>
                            <th>Datum</th>
                            <th>RO</th>
                            <th>Strujni krug / Opis</th>
                            <th style="text-align: right;">Metara</th>
                            <th>Napomena</th>
                        </tr>
                    </thead>
                    <tbody>
                        {redovi_html}
                    </tbody>
                </table>

                <div class="total-section">
                    <span style="font-size: 16px;">UKUPNO:</span>
                    <span style="font-size: 24px; font-weight: bold; margin-left: 15px;">{ukupno:.2f} m</span>
                </div>
                
                <p style="margin-top: 60px; font-size: 11px; color: #aaa; text-align: center; border-top: 1px solid #eee; padding-top: 10px;">
                    ELMAR Elektro-instalacije | Dokument generisan: {datetime.now().strftime("%d.%m.%Y.")}
                </p>
            </div>
        </body>
        </html>
        """
        
        st.download_button(
            label="📩 PREUZMI ČIST IZVEŠTAJ",
            data=izvestaj_html,
            file_name=f"Elmar_Specifikacija_{datetime.now().strftime('%d_%m')}.html",
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
