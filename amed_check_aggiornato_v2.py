import streamlit as st
import fitz  # PyMuPDF

def estrai_testo_pdf(file):
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        testo = ""
        for page in doc:
            testo += page.get_text()
    return testo.lower()

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

# Caricamento documenti
st.markdown("## Caricamento Documenti")
fattura = st.file_uploader("Carica la fattura (PDF)", type="pdf")
ricevuta = None
if pagato_contanti == "No":
    ricevuta = st.file_uploader("Carica la ricevuta di pagamento (PDF)", type="pdf")
documento_libri = None
if causale == "Libri scolastici":
    documento_libri = st.file_uploader("Carica l'elenco dei libri (PDF)", type="pdf")

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

        # Verifica beneficiario nella fattura
        if nome_ben.lower() not in testo_fattura and cognome_ben.lower() not in testo_fattura:
            st.warning("🟡 Da integrare")
            st.write("Il nome del beneficiario non risulta nel contenuto della fattura.")
        # Verifica intestatario nel pagamento (solo se non contanti)
        elif pagato_contanti == "No" and nome_dip.lower() not in testo_ricevuta and cognome_dip.lower() not in testo_ricevuta:
            st.warning("🟡 Da integrare")
            st.write("Il nome del dipendente non risulta nella ricevuta di pagamento.")
        else:
            st.success("✅ Accettata")
            st.write("Documentazione completa e coerente.")

