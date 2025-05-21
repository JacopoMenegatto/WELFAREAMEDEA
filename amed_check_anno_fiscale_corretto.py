
import streamlit as st
import fitz  # PyMuPDF

def estrai_testo_pdf(file):
    with fitz.open(stream=file.read(), filetype="pdf") as doc:
        testo = ""
        for page in doc:
            testo += page.get_text()
    return testo.lower()

st.set_page_config(page_title="Amedea Check – Controllo anno fiscale", layout="centered")

st.title("Amedea Check – Validazione pratica welfare con anno fiscale corretto")

st.markdown("## Dati dipendente")
nome_dip = st.text_input("Nome dipendente")
cognome_dip = st.text_input("Cognome dipendente")

st.markdown("## Dati beneficiario")
nome_ben = st.text_input("Nome beneficiario")
cognome_ben = st.text_input("Cognome beneficiario")

st.markdown("## Dettagli della pratica")
causale = st.selectbox("Causale", ["Retta scolastica", "Trasporto pubblico", "Baby sitting", "Utenze domestiche"])
pagamento = st.selectbox("Metodo di pagamento", ["Bonifico", "Carta", "POS", "Contanti"])
data_fattura = st.date_input("Data fattura")
data_pagamento = st.date_input("Data pagamento")
anno_portale = st.selectbox("Anno selezionato nel portale", ["2024", "2025"])

st.markdown("## Caricamento documenti")
fattura = st.file_uploader("Carica la fattura (PDF)", type="pdf")
ricevuta = st.file_uploader("Carica la ricevuta di pagamento (PDF)", type="pdf")

if st.button("✅ Valuta pratica"):
    if not fattura or not ricevuta:
        st.warning("⚠️ Carica tutti i documenti richiesti.")
    elif nome_dip.strip() == "" or cognome_dip.strip() == "" or nome_ben.strip() == "" or cognome_ben.strip() == "":
        st.warning("⚠️ Inserisci tutti i nomi e cognomi.")
    else:
        testo_fattura = estrai_testo_pdf(fattura)
        testo_ricevuta = estrai_testo_pdf(ricevuta)

        errore_anno = False
        anno_pagamento = data_pagamento.year
        mese_pagamento = data_pagamento.month

        if anno_portale == "2025":
            if anno_pagamento == 2024 and mese_pagamento < 10:
                errore_anno = True
        elif anno_portale == "2024":
            if anno_pagamento == 2025 or (anno_pagamento == 2024 and mese_pagamento >= 10):
                errore_anno = True

        if nome_ben.lower() not in testo_fattura and cognome_ben.lower() not in testo_fattura:
            st.warning("🟡 Da integrare")
            st.write("Il nome del beneficiario non risulta nel contenuto della fattura.")
        elif nome_dip.lower() not in testo_ricevuta and cognome_dip.lower() not in testo_ricevuta:
            st.warning("🟡 Da integrare")
            st.write("Il nome del dipendente non risulta nella ricevuta.")
        elif errore_anno:
            st.error("❌ Da correggere")
            st.write("L'anno selezionato nel portale non corrisponde all'anno fiscale corretto in base alla data di pagamento.")
        else:
            st.success("✅ Accettata")
            st.write("Tutti i dati e i documenti risultano corretti.")
