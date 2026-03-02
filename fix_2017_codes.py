#!/usr/bin/env python3
"""
Corriger les codes communes dans elections_2017_by_bloc_commune_AURA.csv
"""

import pandas as pd

print("Correction codes communes 2017...")

# Charger le fichier all-France avec codes corrects
df_2017_all = pd.read_csv("data/processed/elections_2017_by_bloc_commune.csv", sep=';',
                           dtype={'commune_code': 'str', 'dep_code': 'int'})

# Filtrer pour AURA
AURA_DEPTS = [1, 3, 7, 15, 26, 38, 42, 43, 63, 69, 73, 74]
df_2017_aura = df_2017_all[df_2017_all['dep_code'].isin(AURA_DEPTS)].copy()

print(f"Communes AURA: {len(df_2017_aura):,}")
print(f"Exemples de codes communes:")
print(df_2017_aura['commune_code'].head(10))

# Recalculer le fichier AURA
output_file = "data/processed/elections_2017_by_bloc_commune_AURA.csv"
df_2017_aura.to_csv(output_file, sep=';', index=False)

print(f"\n✅ Fichier corrigé: {output_file}")
