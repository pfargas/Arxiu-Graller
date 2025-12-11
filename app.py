import streamlit as st
from db import create_connection
import pandas as pd
from streamlit_pages import home_page, upload_page


st.set_page_config(page_title="Arxiu Graller", page_icon="🎼")

# --------------------
# Sidebar navigation
# --------------------
page = st.sidebar.radio(
    "Navegació",
    ["🏠 Inici","➕ Afegir partitura", "📄 Veure partitures", "🎼 Veure arranjaments", "⚠️ Admin: Neteja BD"]
)

# input the database name with streamlit CLI argument or default to "partitures.db"
import sys
if len(sys.argv) > 1:
    db_name = sys.argv[1]
else:
    db_name = "partitures.db"

conn = create_connection(db_name)

partitures_columns = conn.execute("PRAGMA table_info(partitures)").fetchall() if conn else []
partitures_columns_names = [col[1] for col in partitures_columns]

#--------------------------------------------------------------------
# PAGE 0 — HOME
#--------------------------------------------------------------------
if page == "🏠 Inici":
    home_page.home_page()


# -------------------------------------------------------------------
# PAGE 1 — ADD PARTITURE
# -------------------------------------------------------------------
if page == "➕ Afegir partitura":
    upload_page.upload_page(conn=conn)


# -------------------------------------------------------------------
# PAGE 2 — SHOW PARTITURES
# -------------------------------------------------------------------
elif page == "📄 Veure partitures":
    st.title("Llista de partitures")
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM partitures")
        rows = cursor.fetchall()

        if rows:
            df = pd.DataFrame(rows, columns=partitures_columns_names)
            st.dataframe(df, use_container_width=True)
        else:
            st.info("No hi ha partitures.")

    else:
        st.error("No es pot connectar a la base de dades.")


# -------------------------------------------------------------------
# PAGE 3 — SHOW ARRANGEMENTS
# -------------------------------------------------------------------
elif page == "🎼 Veure arranjaments":
    st.title("Llista d'arranjaments")
    st.write("Escull una peça per veure els arranjaments disponibles.")
    
    # Load partitures in the selectbox
    partitures = conn.execute("SELECT id, title FROM partitures").fetchall()
    partiture_selected = st.selectbox(
        "Selecciona la partitura",
        options=[p[0] for p in partitures],
        format_func=lambda id: next(t for (pid, t) in partitures if pid == id)
    )

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM arrangements WHERE partiture_id = ?", (partiture_selected,))
    rows = cursor.fetchall()
    title_selected = next((t for (pid, t) in partitures if pid == partiture_selected), "Desconegut")

    if rows:
        st.subheader(f"Arranjaments disponibles per a : {title_selected}")
        for row in rows:
            arrangement_id, partiture_id, ensemble, file_path = row
            
            col1, col2 = st.columns([4, 1])

            with col1:
                st.markdown(f"""
                **ID:** {arrangement_id}  
                **Conjunt:** {ensemble}  
                **Fitxer:** `{file_path.split('/')[-1]}`  
                """)

            with col2:
                with open(file_path, "rb") as f:
                    st.download_button(
                        label="⬇️ PDF",
                        data=f,
                        file_name=file_path.split("/")[-1],
                        mime="application/pdf",
                        key=f"download_{arrangement_id}"
                    )

    else:
        st.info("No hi ha arranjaments.")

# -------------------------------------------------------------------
# PAGE 4 — ADMIN CLEAN DATABASE
# -------------------------------------------------------------------
elif page == "⚠️ Admin: Neteja BD":
    st.title("⚠️ Neteja de la base de dades")
    st.warning("Aquesta acció és irreversible.")

    if st.button("Esborra TOTA la base de dades"):
        cursor = conn.cursor()
        cursor.execute("DELETE FROM arrangements")
        cursor.execute("DELETE FROM partitures")
        conn.commit()
        st.success("Base de dades netejada correctament.")
    
    if st.button("Esborra fitxers PDF"):
        import os
        import shutil

        pdf_folder = "partitures/pdf"
        if os.path.exists(pdf_folder):
            shutil.rmtree(pdf_folder)
            os.makedirs(pdf_folder)
            st.success("Tots els fitxers PDF han estat esborrats.")
        else:
            st.info("No hi ha cap carpeta de fitxers PDF per esborrar.")
