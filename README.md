# ⚡ ELEKTRO-LOG BUSINESS v1.0

Sistem za digitalno praćenje elektro-instalaterskih radova, specifikaciju materijala i automatski obračun metraže.

## 📌 O Projektu
Aplikacija je dizajnirana da olakša posao elektro-instalaterima na terenu. Omogućava preciznu evidenciju utrošenog materijala, automatski odvaja metražu kablova od ostale montažne opreme (regali, C-šine, brezoni) i generiše profesionalne izveštaje.

## 📁 Struktura Projekta

Projekat je podeljen na dve funkcionalne celine:

*   **`Web/Mobile Verzija` (Glavni folder):** Bazirana na **Streamlit** okviru. Ova verzija je optimizovana za korišćenje putem mobilnih telefona na gradilištu.
*   **[`Desktop_Tkinter`](./Desktop_Tkinter):** Originalna verzija aplikacije sa klasičnim Windows/Linux interfejsom. Pogodna za kancelarijsku obradu podataka i unos sa desktop računara.

## ✨ Ključne Funkcije
*   **Pametno filtriranje:** Sistem automatski prepoznaje jedinice mere (metri vs komadi) i vrši kalkulaciju totala samo za kablove.
*   **SQLite Baza:** Svi podaci se čuvaju u lokalnoj bazi `elektro_baza.db`, što omogućava rad bez stalne internet konekcije (u Desktop verziji).
*   **Export Izveštaja:** Generisanje stilizovanog HTML dokumenta sa logotipom firme **ELMAR**, spremnog za štampu ili slanje investitoru.

## 🚀 Instalacija i Pokretanje
```
### 1. Web/Mobile Verzija (Streamlit)
Ova verzija je primarna za rad na terenu:
```bash
pip install streamlit pandas
streamlit run utosak_materijala.py

## **2. Desktop Verzija (Tkinter)**

Nalazi se u folderu Desktop_Tkinter:
Bash

cd Desktop_Tkinter
python utrosak_materijala.py

## **📋 Potrebne Biblioteke**

Sve potrebne biblioteke možete instalirati odjednom komandom:
Bash

pip install -r requirements.txt



## 🌍 Live Demo
Aplikaciju možete testirati uživo na:  
https://elektrolog-business-jqreartnmchqekfzjtjzwv.streamlit.app

---
📝 Autor

    Inženjering i razvoj: Vlade (2026)
```
