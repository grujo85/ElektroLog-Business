# ELEKTRO-LOG BUSINESS v1.0 ⚡

Program za vođenje evidencije o izvedenim elektro-instalacijama, utrošku kablova i strujnim krugovima. Namenjen je elektro-instalerima za brzu izradu profesionalnih specifikacija radova.

## 🚀 Glavne Funkcije
* **Unos podataka**: Brz unos datuma, oznake ormana (RO), strujnih krugova i metraže putem intuitivne forme.
* **Baza podataka**: Automatsko čuvanje unetih radova u lokalnu SQLite bazu podataka (`elektro_baza.db`).
* **Pregled i Editovanje**: Interaktivna tabela unutar aplikacije koja omogućava izmenu podataka u hodu.
* **Profesionalni Izveštaj**: Generisanje stilizovanog dokumenta sa logotipom firme, centriranom količinom i automatski izračunatim ukupnim zbirom metara.

## 🛠 Korišćene tehnologije
* **Python** (Glavni programski jezik)
* **Streamlit** (Web interfejs i interaktivnost)
* **Pandas** (Obrada i prikaz podataka)
* **SQLite** (Lokalna baza podataka)
* **HTML/CSS** (Dizajn i formatiranje izveštaja za štampu)

## 💻 Kako pokrenuti lokalno
1. Klonirajte repozitorijum.
2. Instalirajte potrebne biblioteke:
   ```bash
   pip install streamlit pandas
   ```
3. Postavite svoj logo u korenski folder pod nazivom `elmar.webp`.
4. Pokrenite aplikaciju komandom:
   ```bash
   streamlit run utosak_materijala.py
   ```

## 🌍 Live Demo
Aplikaciju možete testirati uživo na:  
https://elektrolog-business-jqreartnmchqekfzjtjzwv.streamlit.app

---
*Autor: **Vlade** (Design 2026)*
```
