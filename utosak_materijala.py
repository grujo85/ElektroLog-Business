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

   # 5. PROFESIONALNI MEMORANDUM (PREMIUM DIZAJN)
    st.write("---")
    if st.button("💎 GENERIŠI PROFESIONALNI IZVEŠTAJ"):
        # 1. Priprema logotipa (Base64)
        logo_data = ""
        if os.path.exists("elmar.webp"):
            with open("elmar.webp", "rb") as f:
                logo_base64 = base64.b64encode(f.read()).decode()
            logo_data = f'<img src="data:image/webp;base64,{logo_base64}" style="height:80px;">'

        # 2. Generisanje redova tabele - SMANJENO I DISKRETNIJE
        redovi_html = ""
        for i, r in df.iterrows():
            bg_color = "#f9f9f9" if i % 2 == 0 else "#ffffff"
            redovi_html += f"""
            <tr style="background-color: {bg_color}; border-bottom: 1px solid #eee;">
                <td style="padding: 8px 12px; color: #666; font-size: 12px;">{r['datum']}</td>
                
                
                <td style="padding: 8px 12px; font-weight: 500; text-transform: uppercase; font-size: 13px;">{r['orman']}</td>
                
                <td style="padding: 8px 12px; font-size: 13px;">{r['opis']}</td>
                
                
                <td style="padding: 8px 12px; text-align: right; font-weight: 500; font-size: 12px;">{r['metara']:.2f} m</td>
                
                <td style="padding: 8px 12px; color: #888; font-size: 11px; font-style: italic;">{r['napomena'] if r['napomena'] else ''}</td>
            </tr>
            """

        # 3. HTML Memoranduma
        izvestaj_html = f"""
        <!DOCTYPE html>
        <html lang="sr">
        <head>
            <meta charset="UTF-8">
            <style>
                @page {{ size: A4; margin: 20mm; }}
                body {{ font-family: 'Helvetica Neue', Helvetica, Arial, sans-serif; color: #2c3e50; margin: 0; padding: 0; }}
                .wrapper {{ max-width: 800px; margin: auto; }}
                @media print {{ @page {{ margin: 0; }} body {{ padding: 1.5cm; }} }}
                .header-table {{ width: 100%; border-bottom: 2px solid #2c3e50; padding-bottom: 20px; margin-bottom: 30px; }}
                .doc-title {{ text-align: right; text-transform: uppercase; letter-spacing: 2px; color: #2c3e50; }}
                table {{ width: 100%; border-collapse: collapse; margin-top: 10px; }}
                th {{ background-color: #2c3e50; color: white; text-align: left; padding: 12px 15px; text-transform: uppercase; font-size: 11px; letter-spacing: 1px; }}
                .total-row {{ border-top: 3px solid #2c3e50; margin-top: 20px; padding: 20px 0; display: flex; justify-content: flex-end; align-items: baseline; }}
                .footer {{ margin-top: 100px; padding-top: 20px; border-top: 1px solid #eee; text-align: center; font-size: 10px; color: #bdc3c7; text-transform: uppercase; letter-spacing: 1px; }}
            </style>
        </head>
        <body>
            <div class="wrapper">
                <table class="header-table">
                    <tr>
                        <td style="width: 50%;">{logo_data}</td>
                        <td class="doc-title">
                            <h2 style="margin:0;">Specifikacija</h2>
                            <p style="margin:0; font-size: 12px; opacity: 0.7;">Utorašak materijala / Kablova</p>
                            <p>Datum: {datetime.now().strftime('%d.%m.%Y')}</p></div>
                        </td>
                    </tr>
                </table>

                <table>
                    <thead>
                        <tr>
                            <th>Datum</th>
                            <th>Oznaka (RO)</th>
                            <th>Strujni krug / Opis radova</th>
                            <th style="text-align: right;">Količina</th>
                            <th>Napomena</th>
                        </tr>
                    </thead>
                    <tbody>
                        {redovi_html}
                    </tbody>
                </table>

                <div class="total-row">
                    <span style="font-size: 14px; margin-right: 15px; font-weight: 300;">UKUPNA KOLIČINA:</span>
                    <span style="font-size: 28px; font-weight: 800; border-bottom: 4px double #2c3e50;">{ukupno:.2f} m</span>
                </div>

                <div class="footer">
                    ELMAR Elektro-instalacije &nbsp; | &nbsp; DESIGN VLADE {datetime.now().strftime("%Y")} &nbsp; | &nbsp; Interni dokument
                </div>
            </div>
        </body>
        </html>
        """
        
        st.download_button(
            label="📩 PREUZMI PROFESIONALNI IZVEŠTAJ",
            data=izvestaj_html,
            file_name=f"Elmar_Business_Spec_{datetime.now().strftime('%d_%m_%y')}.html",
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
