# ELEKTRO-LOG BUSINESS v1.0 ⚡

Program za vođenje evidencije o izvedenim elektro-instalacijama, utrošku kablova i strujnim krugovima. Namenjen je elektro-instalerima za brzu izradu specifikacija radova.

## Glavne Funkcije:
*   **Unos podataka**: Brz unos datuma, ormana (RO), strujnih krugova i metraže.
*   **Baza podataka**: Automatsko čuvanje svih unetih radova u lokalnu SQLite bazu.
*   **PDF/HTML Izveštaj**: Generisanje profesionalnog izveštaja sa logotipom firme, tabelarnim prikazom i automatskim sabiranjem metraže.
*   **Backup & Restore**: Sigurnosna kopija baze i mogućnost vraćanja podataka.

## Kako se pokreće:
1.  Instalirajte Python (ako već niste).
2.  Potrebno je imati logo u istom folderu pod nazivom `elmar.webp`.
3.  Pokrenite program komandom:
    ```bash
    python program.py
    ```

## Korišćene tehnologije:
*   **Python** (Tkinter za interfejs)
*   **SQLite** (Baza podataka)
*   **HTML/CSS** (Formatiranje izveštaja za štampu)

---
*Autor: Vlade*
