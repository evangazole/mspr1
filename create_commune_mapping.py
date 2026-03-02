#!/usr/bin/env python3
"""
Créer une table de correspondance communes: code_local → code_INSEE
Utiliser elections_2022_2017.csv qui a les vrais codes INSEE dans id_brut_miom
"""

import pandas as pd
import re

print("Création table de correspondance communes...")

# Charger elections_2022_2017.csv
df = pd.read_csv(
    "data/raw/elections_2022_2017.csv",
    sep=';',
    usecols=['code_commune', 'libelle_commune', 'id_brut_miom'],
    dtype={'code_commune': 'str'}
)

print(f"Total records: {len(df):,}")

# Extraire code INSEE du id_brut_miom (ex: '01001_0001' → '01001')
df['insee_code'] = df['id_brut_miom'].str.split('_').str[0]

# Créer mapping: code_local → (commune_name, insee_code)
# Garder un seul record par commune (grouper par code_local)
mapping = df.groupby('code_commune').agg({
    'libelle_commune': 'first',
    'insee_code': 'first'
}).reset_index()

mapping.columns = ['code_local', 'commune_name', 'insee_code']

print(f"\nCommunes mappées: {len(mapping):,}")
print("\nExemples:")
print(mapping.head(15))

# Sauvegarder
mapping.to_csv("data/processed/commune_code_mapping.csv", index=False)
print(f"\n✅ Fichier de correspondance: data/processed/commune_code_mapping.csv")

# Vérifier qu'on a des codes INSEE complets
print(f"\nVérification codes INSEE:")
print(f"  Format: {mapping['insee_code'].iloc[0]}")
print(f"  Codes uniques: {mapping['insee_code'].nunique():,}")
print(f"  Codes = '1': {(mapping['insee_code'] == '1').sum()}")
print(f"  Codes = '0': {(mapping['insee_code'] == '0').sum()}")
