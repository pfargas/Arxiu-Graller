import sqlite3
import os
from const import PDF_UPLOAD_FOLDER

eliminate_words = {"la", "el", "les", "els", "de", "del", "i", "a", "en", "per", "pel", "un", "una", "uns", "unes"}

create_table_partitures_query = """
CREATE TABLE IF NOT EXISTS partitures (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    composer TEXT,
    arranger TEXT,
    genre TEXT,
    year INTEGER,
    difficulty INTEGER,
    repertoire BOOLEAN,
    tags TEXT
);
"""

create_table_arrangements_query = """
CREATE TABLE IF NOT EXISTS arrangements (
    id INTEGER PRIMARY KEY,
    partiture_id INTEGER NOT NULL,
    ensemble TEXT NOT NULL,
    file_path TEXT NOT NULL,
    FOREIGN KEY (partiture_id) REFERENCES partitures(id)
);
"""

def refactor_title(title):
    return title.strip().lower().replace(" ", "_")


def tokenize_title(title):
    splitted_words = [word.strip().lower() for word in title.replace("-", " ").split(" ") if word]
    filtered_words = [word for word in splitted_words if word not in eliminate_words]
    # eliminate l'
    filtered_words = [word[2:] if word.startswith("l'") else word for word in filtered_words]
    return filtered_words
    

def insert_partiture(conn, title, ensemble, file_pdf,
                     composer=None, arranger=None, genre=None,
                     year=None, difficulty=None, repertoire=None, tags=None):

    if file_pdf is None:
        raise ValueError("file_pdf cannot be None")

    if file_pdf.name.split(".")[-1].lower() != "pdf":
        raise ValueError("Only PDF files allowed")

    cursor = conn.cursor()

    # ---------- 1. Check if partiture exists ----------
    cursor.execute("SELECT id FROM partitures WHERE title=?", (title,))
    row = cursor.fetchone()

    if row:
        partiture_id = row[0]
        print(f"Using existing partiture ID {partiture_id}")
    else:
        insert_partitures_query = """
            INSERT INTO partitures (title, composer, arranger, genre, year, difficulty, repertoire, tags)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
        """
        cursor.execute(insert_partitures_query,
            (title, composer, arranger, genre, year, difficulty, repertoire, tags))
        partiture_id = cursor.lastrowid
        print(f"Created new partiture ID {partiture_id}")

    # ---------- 2. Compute version number ----------
    cursor.execute("""
        SELECT file_path FROM arrangements
        WHERE partiture_id=? AND ensemble=?
    """, (partiture_id, ensemble))

    existing_versions = cursor.fetchall()
    version = len(existing_versions) + 1

    # ---------- 3. Create filename ----------
    safe_title = title.replace(" ", "_")
    safe_ensemble = ensemble.replace(" ", "_").replace("+", "plus")
    ext = "pdf"

    filename = f"{safe_title}__{safe_ensemble}_v{version}.{ext}"
    filepath = os.path.join(PDF_UPLOAD_FOLDER, filename)

    os.makedirs(PDF_UPLOAD_FOLDER, exist_ok=True)

    # ---------- 4. Save file ----------
    with open(filepath, "wb") as f:
        f.write(file_pdf.getbuffer())

    # ---------- 5. Insert arrangement ----------
    insert_arrangement_query = """
        INSERT INTO arrangements (partiture_id, ensemble, file_path)
        VALUES (?, ?, ?)
    """
    cursor.execute(insert_arrangement_query, (partiture_id, ensemble, filepath))

    conn.commit()

    return partiture_id, filepath

    
def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()
        cursor.execute(create_table_partitures_query)
        cursor.execute(create_table_arrangements_query)
        conn.commit()
        return conn
    except sqlite3.Error as e:
        print(e)

    return conn





# if __name__ == "__main__":
    
    
#     print(
#     tokenize_title("El recluta del barret blau")
#     )
#     print(
#     tokenize_title("La la la de l'amor")
#     )
    
#     os.remove("my.db") if os.path.exists("my.db") else None

#     try:
#         with sqlite3.connect("my.db") as conn:
#             print(f"Opened SQLite database with version {sqlite3.sqlite_version} successfully.")
#             cursor = conn.cursor()
#             cursor.execute(create_table_partitures_query)
#             cursor.execute(create_table_arrangements_query)
#             conn.commit()
#             insert_partiture(conn, "Febrer", "2 veus")
#             insert_partiture(conn, "El recluta", "2 veus")
#             insert_partiture(conn, "El recluta", "2 veus i baixa")
#     except sqlite3.OperationalError as e:
#         print("Failed to open database:", e)
