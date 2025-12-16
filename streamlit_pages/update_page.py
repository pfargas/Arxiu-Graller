import streamlit as st
from db import update_table

def update_page(conn):
    st.title("Actualitzar partitura")
    st.write("Funcionalitat per actualitzar una partitura anirà aquí.")

    partitures = conn.execute("SELECT id, title FROM partitures").fetchall()
    partitures_id = [p[0] for p in partitures]
    select_options = [None] + partitures_id
    partiture_selected = st.selectbox(
        "Selecciona la partitura",
        options=select_options,
        format_func=lambda id: next(t for (pid, t) in partitures if pid == id) if id is not None else "-"
    )

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM arrangements WHERE partiture_id = ?", (partiture_selected,))
    rows = cursor.fetchall()
    title_selected = next((t for (pid, t) in partitures if pid == partiture_selected), "Desconegut")
    if rows:
        st.info(f"nomes s'hauria de veure quan s'escull una partitura: {title_selected}")
        current_info = conn.execute("SELECT * FROM partitures WHERE id = ?", (partiture_selected,)).fetchone()
        partitures_columns = conn.execute("PRAGMA table_info(partitures)").fetchall()
        partitures_columns_names = [col[1] for col in partitures_columns]
        current_info_dict = dict(zip(partitures_columns_names, current_info))
        print(current_info_dict)
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
        
        gen_col, diff_col, rep_col = st.columns([1,1,1])
        with gen_col:
            genre = st.text_input("Gènere")
        with diff_col:
            difficulty = st.number_input("Dificultat", min_value=0, step=1, max_value=10)
        with rep_col:
            repertoire = st.checkbox("És part del repertori habitual?")
            
        tags = st.text_input("Etiquetes (separades per comes)")
        
        if st.button("Desar a la base de dades"):
            if not title:
                st.error("Cal introduir el títol.")
            elif not uploaded_pdf:
                st.error("Cal pujar un fitxer PDF.")
            else:
                # partiture_id, filepath = insert_partiture(conn, title, ensemble, uploaded_pdf, composer=composer, year=year, arranger=arranger, genre=genre, difficulty=difficulty, repertoire=repertoire, tags=tags)
                if partiture_id:
                    st.success(f"Partitura afegida amb ID: {partiture_id}")
                    st.code(filepath)
                else:
                    st.error("Error afegint la partitura.")
