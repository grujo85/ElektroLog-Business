import streamlit as st
import pandas as pd
import sqlite3
import os
import base64
from datetime import datetime

st.set_page_config(page_title="ELEKTRO-LOG", layout="wide")

# 1. LOGO (Direktno, bez mnogo filozofije)
if os.path.exists("elmar.webp"):
    with open("elmar.webp", "rb") as f:
        data = base64.b64encode(f.read()).decode()
    st.markdown(f'<img src="data:image/webp;base64,{data}" width="200">', unsafe_allow_html=True)

st.title("ELEKTRO-LOG BUSINESS v1.0 ⚡")

# 2. BAZA
conn = sqlite3.connect('elektro_baza.db')
conn.execute("CREATE TABLE IF NOT EXISTS radovi (id INTEGER PRIMARY KEY AUTOINCREMENT, datum TEXT, orman TEXT, opis TEXT, metara REAL, napomena TEXT)")
conn.close()

# 3. UNOS
with st.form("unos"):
    c1, c2, c3 = st.columns(3)
    d = c1.date_input("Datum").strftime("%d.%m.%Y")
    o = c1.text_input("Orman").upper()
    kr = c2.text_input("Strujni krug")
    m = c2.number_input("Metara", min_value=0.0)
    n = c3.text_area("Napomena")
    if st.form_submit_button("SNIMI"):
        c = sqlite3.connect('elektro_baza.db')
        c.execute("INSERT INTO radovi (datum, orman, opis, metara, napomena) VALUES (?,?,?,?,?)", (d, o, kr, m, n))
        c.commit()
        c.close()
        st.rerun()

# 4. TABELA SA BRISANJEM
c = sqlite3.connect('elektro_baza.db')
df = pd.read_sql_query("SELECT * FROM radovi ORDER BY id DESC", c)
c.close()

if not df.empty:
    st.write("---")
    st.subheader("Lista (Označi red i lupni 'Delete' za brisanje)")
    
    # Ovo je ta tabela koja ima brisanje u sebi
    edited_df = st.data_editor(df, use_container_width=True, num_rows="dynamic", hide_index=True)
    
    if len(edited_df) < len(df):
        c = sqlite3.connect('elektro_baza.db')
        c.execute("DELETE FROM radovi")
        edited_df.to_sql('radovi', c, if_exists='append', index=False)
        c.commit()
        c.close()
        st.rerun()

    st.metric("UKUPNO", f"{df['metara'].sum()} m")
