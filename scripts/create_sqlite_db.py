
import pandas as pd
import sqlite3
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent

RH_FILE = ROOT_DIR / "data" / "Données_RH.xlsx"
SPORT_FILE = ROOT_DIR / "data" / "Données_Sportive.xlsx"

# Fichiers source
RH_FILE = ROOT_DIR / "data" / "Données_RH.xlsx"
SPORT_FILE = ROOT_DIR / "data" / "Données_Sportive.xlsx"
DB_FILE = ROOT_DIR / "data" / "avantages_sportifs.db"

def normalize_columns(df):
    """Nettoie les noms de colonnes pour SQLite."""
    df.columns = [
        c.lower()
         .replace(" ", "_")
         .replace("'", "")
         .replace("é", "e")
         .replace("è", "e")
         .replace("ê", "e")
         .replace("à", "a")
         .replace("ç", "c")
        for c in df.columns
    ]
    return df

def main():
    # base_path = "./data/"

    # Lecture des fichiers Excel
    df_rh = pd.read_excel(RH_FILE)
    df_sport = pd.read_excel(SPORT_FILE)

    # Normalisation des colonnes
    df_rh = normalize_columns(df_rh)
    df_sport = normalize_columns(df_sport)

    # Connexion SQLite
    conn = sqlite3.connect(DB_FILE)

    # Création des tables
    df_rh.to_sql("employes", conn, if_exists="replace", index=False)
    df_sport.to_sql("sports_employes", conn, if_exists="replace", index=False)

    # Création d'une vue métier
    conn.execute("""
    CREATE VIEW IF NOT EXISTS v_employes_sport AS
    SELECT
        e.id_salarie,
        e.nom,
        e.prenom,
        e.bu,
        e.salaire_brut,
        e.adresse_du_domicile,
        e.moyen_de_deplacement,
        s.pratique_dun_sport
    FROM employes e
    LEFT JOIN sports_employes s
        ON e.id_salarie = s.id_salarie
    """)

    conn.commit()
    conn.close()

    print(f"Base SQLite créée : {DB_FILE}")

if __name__ == "__main__":
    main()
