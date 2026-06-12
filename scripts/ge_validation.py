import sqlite3
import pandas as pd
import great_expectations as gx
from pathlib import Path

import os

print("PWD =", os.getcwd())

ROOT_DIR = Path(__file__).resolve().parent.parent

DB_PATH = ROOT_DIR / "data" / "avantages_sportifs.db"

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql_query("SELECT * FROM activites_sportives", conn)
df_employes = pd.read_sql_query("SELECT id_salarie FROM employes", conn)
conn.close()

context = gx.get_context(mode="file", project_root_dir=ROOT_DIR)

print("ROOT_DIR =", ROOT_DIR)
print("GX ROOT =", context.root_directory)

import os

print("===== GX DOCS =====")

gx_docs_path = "/project/app/static/gx_docs"

import os
from datetime import datetime

index_file = "/project/app/static/gx_docs/index.html"

print(
    "Derniere modification :",
    datetime.fromtimestamp(
        os.path.getmtime(index_file)
    )
)

# =====================================================
# DATASOURCE + ASSETS
# =====================================================

data_source = context.data_sources.add_or_update_pandas(name="sqlite_pandas_source")

data_asset = data_source.add_dataframe_asset(name="activites_asset")
batch_definition = data_asset.add_batch_definition_whole_dataframe("activites_batch")

df_distance = df[df["type_activite"].isin(["Course à pied", "Vélo", "Marche", "Randonnée"])]
distance_asset = data_source.add_dataframe_asset(name="distance_asset")
distance_batch_definition = distance_asset.add_batch_definition_whole_dataframe("distance_batch")

# =====================================================
# EXPECTATION SUITES
# =====================================================

suite = context.suites.add_or_update(gx.ExpectationSuite(name="activites_suite"))

sports_valides = ["Course à pied", "Vélo", "Marche", "Natation", "Randonnée", "Escalade"]
ids_employes = df_employes["id_salarie"].dropna().tolist()

suite.add_expectation(gx.expectations.ExpectColumnValuesToBeUnique(column="id"))
suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="id_salarie"))
suite.add_expectation(gx.expectations.ExpectColumnValuesToBeBetween(column="distance_m", min_value=0))
suite.add_expectation(gx.expectations.ExpectColumnValuesToBeInSet(column="type_activite", value_set=sports_valides))
suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="date_debut"))
suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="date_fin"))
suite.add_expectation(gx.expectations.ExpectColumnPairValuesAToBeGreaterThanB(column_A="date_fin", column_B="date_debut", or_equal=True))
suite.add_expectation(gx.expectations.ExpectColumnValuesToBeInSet(column="id_salarie", value_set=ids_employes))

distance_suite = context.suites.add_or_update(gx.ExpectationSuite(name="distance_suite"))
distance_suite.add_expectation(gx.expectations.ExpectColumnValuesToNotBeNull(column="distance_m"))

# =====================================================
# VALIDATION DEFINITIONS
# =====================================================

validation_activites = context.validation_definitions.add_or_update(
    gx.ValidationDefinition(
        name="validation_activites",
        data=batch_definition,
        suite=suite,
    )
)

validation_distance = context.validation_definitions.add_or_update(
    gx.ValidationDefinition(
        name="validation_distance",
        data=distance_batch_definition,
        suite=distance_suite,
    )
)

# =====================================================
# CHECKPOINTS SÉPARÉS (un par dataframe)
# =====================================================

checkpoint_activites = context.checkpoints.add_or_update(
    gx.Checkpoint(
        name="checkpoint_activites",
        validation_definitions=[validation_activites],
    )
)

checkpoint_distance = context.checkpoints.add_or_update(
    gx.Checkpoint(
        name="checkpoint_distance",
        validation_definitions=[validation_distance],
    )
)

# =====================================================
# RUN
# =====================================================

result_activites = checkpoint_activites.run(
    batch_parameters={"dataframe": df}
)

result_distance = checkpoint_distance.run(
    batch_parameters={"dataframe": df_distance}
)

# =====================================================
# RÉSUMÉ CONSOLE
# =====================================================

print("\n" + "=" * 60)
print("GLOBAL SUMMARY")
print("=" * 60)

for result in [result_activites, result_distance]:
    for vr in result.run_results.values():
        # vr est directement un ExpectationSuiteValidationResult
        stats = vr.statistics
        suite_name = vr.suite_name
        print(f"\nSuite : {suite_name}")
        print(f"  Tests total   : {stats['evaluated_expectations']}")
        print(f"  Tests réussis : {stats['successful_expectations']}")
        print(f"  Tests échoués : {stats['unsuccessful_expectations']}")

# =====================================================
# DATA DOCS
# =====================================================

context.build_data_docs()
context.open_data_docs()

site_urls = context.build_data_docs()

print(site_urls)