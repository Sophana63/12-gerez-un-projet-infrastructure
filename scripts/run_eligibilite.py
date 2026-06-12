from app.repositories.sqlite_repository import (
    get_connection
)

from app.services.eligibilite_service import (
    creer_tables,
    calculer_eligibilite_salarie
)

# ============================================
# TABLES
# ============================================

creer_tables()

# ============================================
# LOAD EMPLOYEES
# ============================================

conn = get_connection()

cursor = conn.cursor()

cursor.execute("""
SELECT *
FROM employes
""")

employees = cursor.fetchall()

conn.close()

print(f"{len(employees)} salariés trouvés")

# ============================================
# PROCESS
# ============================================

for employee in employees:

    calculer_eligibilite_salarie(
        employee
    )

print("Calcul terminé")