import streamlit as st
import fitz  # PyMuPDF
import re

def estrai_testo_pdf(file):
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        testo = ""
        for page in doc:
            testo += page.get_text()
    return testo.lower()

def normalizza(testo):
    return testo.lower().replace("'", "").replace("-", " ").replace(",", ".")

st.set_page_config(page_title="Amedea Check – Validatore aggiornato", layout="centered")

st.title("Amedea Check – Validazione Pratica Welfare (versione aggiornata)")

# Intestatario del conto welfare
st.markdown("## Dati Dipendente (intestatario conto welfare)")
nome_dip = st.text_input("Nome dipendente")
cognome_dip = st.text_input("Cognome dipendente")

# Dati beneficiario
st.markdown("## Dati Beneficiario")
nome_ben = st.text_input("Nome beneficiario")
cognome_ben = st.text_input("Cognome beneficiario")

# Dettagli pratica
st.markdown("## Dettagli Pratica")
causale = st.selectbox("Causale", [
    "Retta scolastica", 
    "Spese iscrizione", 
    "Tasse scolastiche", 
    "Libri scolastici", 
    "Pre-scuola", 
    "Dopo-scuola", 
    "Mensa scolastica",
    "Trasporto pubblico", 
    "Baby sitting", 
    "Utenze domestiche"
])

pagamento = st.selectbox("Metodo di pagamento", ["Bonifico", "Carta", "POS", "Contanti"])
pagato_contanti = st.radio("Pagato in contanti?", ["No", "Sì"])
data_fattura = st.date_input("Data fattura")
data_pagamento = st.date_input("Data pagamento")
anno_portale = st.selectbox("Anno selezionato nel portale", ["2023", "2024", "2025"])
importo_richiesto = st.number_input("Importo richiesto a rimborso (€)", min_value=0.0, step=0.01)

# Caricamento documenti
st.markdown("## Caricamento Documenti")
fattura = st.file_uploader("Carica la fattura (PDF)", type="pdf")
ricevuta = None
if pagato_contanti == "No":
    ricevuta = st.file_uploader("Carica la ricevuta di pagamento (PDF)", type="pdf")
documento_libri = None
if causale == "Libri scolastici":
    documento_libri = st.file_uploader("Carica il documento dei libri (PDF)", type="pdf")

# Bottone di validazione
if st.button("✅ Valuta pratica"):
    if not fattura:
        st.warning("⚠️ Devi caricare almeno la fattura.")
    elif pagato_contanti == "No" and not ricevuta:
        st.warning("⚠️ Carica la ricevuta se non è stato pagato in contanti.")
    elif causale == "Libri scolastici" and not documento_libri:
        st.warning("⚠️ Devi caricare il documento dei libri.")
    else:
        testo_fattura = estrai_testo_pdf(fattura)
        testo_ricevuta = estrai_testo_pdf(ricevuta) if ricevuta else ""

        # Verifica nome beneficiario
        nomi_varianti = [
            nome_ben.lower(),
            cognome_ben.lower(),
            f"{cognome_ben.lower()} {nome_ben.lower()}",
            f"{nome_ben.lower()} {cognome_ben.lower()}"
        ]
        if not any(n in testo_fattura for n in nomi_varianti):
            st.warning("🟡 Da integrare")
            st.write("Il nome del beneficiario non risulta nel contenuto della fattura.")
        elif pagato_contanti == "No" and not any(n in testo_ricevuta for n in [nome_dip.lower(), cognome_dip.lower()]):
            st.warning("🟡 Da integrare")
            st.write("Il nome del dipendente non risulta nella ricevuta di pagamento.")
        else:
            # Estrai importo
            testo_totale = testo_ricevuta if ricevuta else testo_fattura
            pattern = re.compile(r"\b([0-9]+[\.,][0-9]{2})\b")
            importi_trovati = [float(normalizza(m.group(1))) for m in pattern.finditer(testo_totale) if float(normalizza(m.group(1))) > 5.0]

            if importi_trovati:
                importo_doc = max(importi_trovati)
                tolleranza = 3.00
                if abs(importo_doc - importo_richiesto) > tolleranza:
                    st.warning("🟡 Da integrare")
                    st.write(f"L'importo richiesto (€{importo_richiesto:.2f}) è troppo diverso da quello rilevato nel documento (€{importo_doc:.2f}).")
                else:
                    st.success("✅ Accettata")
                    st.write("Documentazione completa e coerente.")
            else:
                st.warning("🟡 Da integrare")
                st.write("Non è stato rilevato alcun importo nel documento.")
