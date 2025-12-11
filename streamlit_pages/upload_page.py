import streamlit as st
from const import ENSEMBLES
from db import insert_partiture

def upload_page(conn):
    st.title("Afegir partitura")
    st.write("Introdueix la informació de la peça.")

    title_col, comp_col, year_col, arr_col = st.columns([1,1,1,1])
    with title_col:
        title = st.text_input("Títol de la partitura")
    with comp_col:
        composer = st.text_input("Compositor/a")
    with year_col:
        year = st.text_input("Any de composició")
        try: 
            year = int(year)
        except:
            year = None
            
    with arr_col:
        arranger = st.text_input("Arranjador/a")
    
    ensemble_col, gen_col, diff_col, rep_col = st.columns([1,1,1,1])
    with ensemble_col:
        ensemble = st.selectbox("Conjunt / Formació", ENSEMBLES)
    with gen_col:
        genre = st.text_input("Gènere")
    with diff_col:
        difficulty = st.number_input("Dificultat", min_value=0, step=1, max_value=10)
    with rep_col:
        repertoire = st.checkbox("És part del repertori habitual?")
        
    tags = st.text_input("Etiquetes (separades per comes)")
    
    uploaded_pdf = st.file_uploader("Selecciona un fitxer PDF", type=["pdf"])

    if st.button("Desar a la base de dades"):
        if not title:
            st.error("Cal introduir el títol.")
        elif not uploaded_pdf:
            st.error("Cal pujar un fitxer PDF.")
        else:
            partiture_id, filepath = insert_partiture(conn, title, ensemble, uploaded_pdf, composer=composer, year=year, arranger=arranger, genre=genre, difficulty=difficulty, repertoire=repertoire, tags=tags)
            if partiture_id:
                st.success(f"Partitura afegida amb ID: {partiture_id}")
                st.code(filepath)
            else:
                st.error("Error afegint la partitura.")