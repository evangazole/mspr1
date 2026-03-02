#!/usr/bin/env python3
"""
Extract AURA-only 2017 election data and enrich with commune names
"""

import pandas as pd
import numpy as np

# AURA departments
AURA_DEPTS = [1, 3, 7, 15, 26, 38, 42, 43, 63, 69, 73, 74]

print("="*100)
print("CRÉATION DONNÉES ÉLECTIONS 2017 - RÉGION AURA")
print("="*100)

# Load 2017 data (all France)
print("\n1️⃣  Chargement données 2017 (France entière)...")
df_2017 = pd.read_csv(
    "data/processed/elections_2017_by_bloc_commune.csv",
    sep=';',
    dtype={'commune_code': 'str', 'dep_code': 'int'}
)

print(f"   Chargé: {len(df_2017):,} communes")

# Filter for AURA only
print("\n2️⃣  Filtrage pour région AURA...")
df_aura = df_2017[df_2017['dep_code'].isin(AURA_DEPTS)].copy()

print(f"   ✅ {len(df_aura):,} communes AURA")

# Save AURA version
output_file = "data/processed/elections_2017_by_bloc_commune_AURA.csv"
df_aura.to_csv(output_file, sep=';', index=False)

print(f"\n✅ Sauvegardé: {output_file}")

# Summary
print(f"\n" + "="*100)
print("RÉSUMÉ - ÉLECTIONS 2017")
print("="*100)

print(f"\nCommunes AURA: {len(df_aura):,}")

print(f"\nVotes par bloc (AURA):")
vote_totals = df_aura[['vote_G', 'vote_C', 'vote_D', 'vote_ED']].sum()
print(f"  Gauche:           {vote_totals['vote_G']:,}")
print(f"  Centre:           {vote_totals['vote_C']:,}")
print(f"  Droite:           {vote_totals['vote_D']:,}")
print(f"  Extrême-Droite:   {vote_totals['vote_ED']:,}")
print(f"  TOTAL:            {vote_totals.sum():,}")

print(f"\nDépartements AURA couverts:")
for dept in sorted(df_aura['dep_code'].unique()):
    communes = len(df_aura[df_aura['dep_code'] == dept])
    dept_name = df_aura[df_aura['dep_code'] == dept]['dep_name'].iloc[0]
    print(f"  Dpt {dept:2d} ({dept_name:20s}): {communes:4d} communes")

print(f"\n📋 EXEMPLE (10 communes AURA):")
print(df_aura.head(10)[['commune_name', 'dep_code', 'dep_name', 'vote_G', 'vote_C', 'vote_D', 'vote_ED']].to_string(index=False))
