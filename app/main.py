from flask import Flask, render_template
from flask_restx import Api

from app.routes.eligibilite_routes import (
    api as eligibilite_ns
)

from app.routes.employes_routes import (
    api as employes_ns
)

from app.routes.activites_routes import (
    api as activites_ns
)

from app.routes.kpis_routes import (
    api as kpis_ns
)

from app.routes.dashboard_routes import (
    dashboardResource
)

# ============================================
# FLASK
# ============================================

app = Flask(__name__)

# ============================================
# HOME
# ============================================

@app.route("/")
def home():

    data = dashboardResource()

    return render_template(
        "dashboard/dashboard.html",
        nb_salaries =  data["nb_salaries"],
        nb_sportifs = data["nb_sportifs"],
        labels = data["labels"],
        values = data["values"],
        jours_bien_etre = data["jours_bien_etre"],
        couts = data["couts"],
        mois_labels = data["mois_labels"],
        mois_values = data["mois_values"],
        salaries_bien_etre = data["salaries_bien_etre"],
        dernieres_activites = data["dernieres_activites"]
    )

# ============================================
# API / SWAGGER
# ============================================

api = Api(
    app,
    version="1.0",
    title="API Avantages Sportifs",
    description="""
    API RH permettant :
    - le suivi des activités sportives
    - le calcul des primes
    - les jours bien-être
    - les contrôles qualité
    """,
    doc="/swagger"
)

# ============================================
# NAMESPACES
# ============================================

api.add_namespace(
    eligibilite_ns
)

api.add_namespace(
    employes_ns
)

api.add_namespace(
    activites_ns
)

api.add_namespace(
    kpis_ns
)


# ============================================
# MAIN
# ============================================

if __name__ == "__main__":

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )