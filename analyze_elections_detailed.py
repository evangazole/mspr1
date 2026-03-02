#!/usr/bin/env python3
"""Analyse élections avec bon séparateur"""

import pandas as pd

# Charger avec le bon séparateur (;)
df = pd.read_csv("data/raw/elections_2022_2017.csv", sep=";", nrows=1000, low_memory=False)

print("=" * 130)
print("STRUCTURE DU FICHIER ÉLECTIONS_2022_2017.CSV")
print("=" * 130)
print()

print(f"Dimensions: {df.shape[0]:,} lignes (batch) × {df.shape[1]} colonnes")
print()

print("COLONNES:")
for i, col in enumerate(df.columns, 1):
    print(f"  {i:2d}. {col:<50} ({df[col].dtype})")

print()
print("=" * 130)

# Afficher quelques lignes
print()
print("PREMIERS RÉSULTATS (3 lignes):")
print(df.head(3).to_string())

print()
print("=" * 130)
print("ANALYSE")
print("=" * 130)
print()

# Vérifier années
print(f"Années couverte:")
elections = df['id_election'].unique()
print(f"  Élections uniques: {elections}")

print()
print("Grain géographique:")
print(f"  - Départements uniques: {df['code_departement'].nunique()}")
print(f"  - Communes uniques: {df['code_commune'].nunique()}")
print(f"  - Bureaux de vote uniques: {df['code_bv'].nunique()}")

print()
print("⚠️ OBSERVATION IMPORTANTE:")
print("""
Le fichier contient SEULEMENT les statistiques agrégées au niveau bureau de vote:
- Nombre d'inscrits, abstentions, votants
- Blancs, nuls, exprimés
- Rapports (%) 

❌ Il N'Y A PAS les noms des candidats ou résultats par candidat!
❌ Pas de colonnes "parti", "candidat", "voix_LFI", "voix_PS", etc.

➜ CONSÉQUENCE:
   Ce fichier seul ne suffit PAS pour créer les colonnes vote_G, vote_C, vote_D, vote_ED
   qui nécessitent de savoir combien de voix chaque parti a reçu.

➜ SOLUTIONS POSSIBLES:
   1. Chercher un autre fichier avec résultats par candidat/parti
   2. Chercher données élections aggrégées par commune sur data.gouv
   3. Utiliser une approche indirecte (ex: résultat du candidat arrivé 1er)
""")
