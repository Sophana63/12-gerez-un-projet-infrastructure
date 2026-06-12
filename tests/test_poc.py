import pytest
from app import create_app, db
from app.models.models import Salarie, Activite, Eligibilite
from datetime import datetime, timezone


@pytest.fixture
def app():
    app = create_app("testing")
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def salarie_fixture(app):
    with app.app_context():
        s = Salarie(
            id_salarie=99001,
            nom="Test",
            prenom="Alice",
            email="alice.test@sportdata.fr",
            salaire_annuel_brut=50000.0,
            adresse_domicile="10 rue du Test, 34000 Montpellier",
            mode_deplacement="vélo",
            declaration_valide=True,
        )
        db.session.add(s)
        db.session.commit()
        return s


class TestSante:
    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json["status"] == "ok"


class TestActivites:
    def test_injection_sans_salarie(self, client):
        r = client.post("/api/activites/inject", json={"id_salarie": 99999})
        assert r.status_code == 404

    def test_injection_sans_id(self, client):
        r = client.post("/api/activites/inject", json={})
        assert r.status_code == 400

    def test_injection_valide(self, client, app, salarie_fixture):
        with app.app_context():
            r = client.post("/api/activites/inject", json={"id_salarie": 99001})
            assert r.status_code == 201
            data = r.json
            assert "activite" in data
            assert data["activite"]["id_salarie"] == 99001

    def test_historique_vide(self, client):
        r = client.get("/api/activites/historique")
        assert r.status_code == 200
        assert r.json["total"] == 0

    def test_historique_filtre_annee(self, client, app, salarie_fixture):
        with app.app_context():
            client.post("/api/activites/inject", json={"id_salarie": 99001})
            annee = datetime.now().year
            r = client.get(f"/api/activites/historique?annee={annee}")
            assert r.status_code == 200
            assert r.json["total"] >= 1


class TestQualite:
    def test_distance_negative_rejetee(self, client, app, salarie_fixture):
        with app.app_context():
            r = client.post("/api/activites/inject", json={
                "id_salarie": 99001,
                "type_sport": "Course à pied",
                "distance_metres": -500,
                "temps_secondes": 1800,
                "date_debut": datetime.now(timezone.utc).isoformat(),
            })
            assert r.status_code == 422
            assert any(a["type_alerte"] == "distance_negative" for a in r.json["alertes"])

    def test_temps_invalide_rejete(self, client, app, salarie_fixture):
        with app.app_context():
            r = client.post("/api/activites/inject", json={
                "id_salarie": 99001,
                "type_sport": "Course à pied",
                "distance_metres": 5000,
                "temps_secondes": 0,
                "date_debut": datetime.now(timezone.utc).isoformat(),
            })
            assert r.status_code == 422

    def test_activite_valide_acceptee(self, client, app, salarie_fixture):
        with app.app_context():
            r = client.post("/api/activites/inject", json={
                "id_salarie": 99001,
                "type_sport": "Course à pied",
                "distance_metres": 8000,
                "temps_secondes": 2400,
                "date_debut": datetime.now(timezone.utc).isoformat(),
            })
            assert r.status_code == 201


class TestEligibilite:
    def test_eligibilite_prime_velo(self, app, salarie_fixture):
        with app.app_context():
            from app.services.eligibilite_service import calculer_eligibilite_salarie
            s = Salarie.query.filter_by(id_salarie=99001).first()
            s.mode_deplacement = "vélo"
            s.declaration_valide = True
            db.session.commit()
            elig = calculer_eligibilite_salarie(s)
            assert elig.eligible_prime is True
            assert elig.montant_prime == pytest.approx(2500.0)  # 5% de 50000

    def test_pas_eligible_prime_voiture(self, app, salarie_fixture):
        with app.app_context():
            from app.services.eligibilite_service import calculer_eligibilite_salarie
            s = Salarie.query.filter_by(id_salarie=99001).first()
            s.mode_deplacement = "voiture"
            s.declaration_valide = False
            db.session.commit()
            elig = calculer_eligibilite_salarie(s)
            assert elig.eligible_prime is False
            assert elig.montant_prime == 0.0

    def test_bien_etre_seuil(self, app, salarie_fixture):
        """Un salarié avec 15+ activités est éligible aux jours bien-être."""
        with app.app_context():
            from app.services.eligibilite_service import calculer_eligibilite_salarie
            s = Salarie.query.filter_by(id_salarie=99001).first()
            annee = datetime.now().year
            for _ in range(16):
                a = Activite(
                    id_salarie=99001,
                    date_debut=datetime(annee, 6, 1, tzinfo=timezone.utc),
                    type_sport="Course à pied",
                    distance_metres=5000,
                    temps_secondes=1800,
                    source="test",
                )
                db.session.add(a)
            db.session.commit()
            elig = calculer_eligibilite_salarie(s)
            assert elig.eligible_bien_etre is True
            assert elig.nb_jours_bien_etre == 5

    def test_bien_etre_sous_seuil(self, app, salarie_fixture):
        with app.app_context():
            from app.services.eligibilite_service import calculer_eligibilite_salarie
            s = Salarie.query.filter_by(id_salarie=99001).first()
            elig = calculer_eligibilite_salarie(s)
            assert elig.eligible_bien_etre is False


class TestRH:
    def test_liste_salaries_vide(self, client):
        r = client.get("/api/rh/salaries")
        assert r.status_code == 200
        assert r.json["total"] == 0

    def test_import_csv(self, client):
        csv_content = (
            "id_salarie,nom,prenom,email,salaire_annuel_brut,adresse_domicile,mode_deplacement\n"
            "88001,Dupont,Paul,paul@test.fr,40000,1 rue Test 34000 Montpellier,vélo\n"
        )
        data = {"file": (csv_content.encode(), "test.csv")}
        r = client.post("/api/rh/import-csv", data=data, content_type="multipart/form-data")
        assert r.status_code == 201
        assert r.json["inseres"] == 1

    def test_impact_financier_structure(self, client):
        r = client.get("/api/rh/impact-financier")
        assert r.status_code == 200
        data = r.json
        assert "prime" in data
        assert "bien_etre" in data
        assert "cout_total_eur" in data
