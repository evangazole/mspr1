#!/usr/bin/env python3
"""
Map 2022 presidential candidates to political groupings
and aggregate votes by bloc at commune level
"""

import pandas as pd
import numpy as np

# 2022 Presidential Candidates Mapping
# Source: 2022 French presidential election official results
candidates_to_bloc = {
    # Extrême Droite (vote_ED)
    'LE PEN': 'ED',        # Marine Le Pen - RN
    'ZEMMOUR': 'ED',       # Éric Zemmour - Reconquête
    'DUPONT-AIGNAN': 'ED',  # Dupont-Aignan - Independent right-wing
    
    # Droite (vote_D)
    'PÉCRESSE': 'D',       # Valérie Pécresse - LR
    'LASSALLE': 'D',       # Jean Lassalle - Independent right-wing
    
    # Centre (vote_C)
    'MACRON': 'C',         # Emmanuel Macron - LREM/ENSEMBLE
    'BAYROU': 'C',         # François Bayrou - Modem
    
    # Gauche (vote_G)  
    'MÉLENCHON': 'G',      # Jean-Luc Mélenchon - LFI
    'ROUSSEL': 'G',        # Fabien Roussel - PCF
    'JADOT': 'G',          # Yannick Jadot - EELV
    'HIDALGO': 'G',        # Anne Hidalgo - PS
    'POUTOU': 'G',         # Philippe Poutou - NPA
    'ARTHAUD': 'G',        # Nathalie Arthaud - LO
}

# Load 2022 data
print("Loading 2022 election data...")
df_2022 = pd.read_csv("data/raw/04-resultats-par-commune(1).csv")

print(f"Loaded {len(df_2022):,} rows")
print(f"\nUnique candidates: ")
print(df_2022['cand_nom'].unique())

# Clean numeric columns
df_2022['cand_nb_voix'] = pd.to_numeric(df_2022['cand_nb_voix'], errors='coerce').fillna(0).astype(int)
df_2022['exprimes_nb'] = pd.to_numeric(df_2022['exprimes_nb'], errors='coerce').fillna(0).astype(int)
df_2022['commune_code'] = pd.to_numeric(df_2022['commune_code'], errors='coerce').fillna(0).astype(int)
df_2022['dep_code'] = pd.to_numeric(df_2022['dep_code'], errors='coerce').fillna(0).astype(int)

print("\n" + "="*100)
print("MAPPING CANDIDATES TO BLOCS")
print("="*100)

# Create mapping column
df_2022['bloc'] = df_2022['cand_nom'].str.upper().map(candidates_to_bloc)

# Check unmapped candidates
unmapped = df_2022[df_2022['bloc'].isna()]['cand_nom'].unique()
if len(unmapped) > 0:
    print(f"\n⚠️ ATTENTION: {len(unmapped)} candidats non mappés:")
    for cand in unmapped:
        print(f"  - {cand}")

print(f"\nMappés:")
for cand, bloc in candidates_to_bloc.items():
    count = (df_2022['cand_nom'] == cand).sum()
    if count > 0:
        print(f"  ✅ {cand:20s} → {bloc} ({count:,} lignes)")

print("\n" + "="*100)
print("AGGREGATION PAR COMMUNE ET BLOC")
print("="*100)

# Group by commune and bloc, sum votes
agg = df_2022[df_2022['bloc'].notna()].groupby(
    ['commune_code', 'commune_name', 'dep_code', 'dep_name', 'bloc']
).agg({
    'cand_nb_voix': 'sum',
    'exprimes_nb': 'first'
}).reset_index()

# Pivot to get one row per commune
pivot = agg.pivot_table(
    index=['commune_code', 'commune_name', 'dep_code', 'dep_name', 'exprimes_nb'],
    columns='bloc',
    values='cand_nb_voix',
    fill_value=0
).reset_index()

# Rename columns
pivot.columns.name = None
pivot.columns = ['commune_code', 'commune_name', 'dep_code', 'dep_name', 'exprimes_nb',
                 'vote_C', 'vote_D', 'vote_ED', 'vote_G']

# Fill NaN with 0
for col in ['vote_C', 'vote_D', 'vote_ED', 'vote_G']:
    if col in pivot.columns:
        pivot[col] = pivot[col].fillna(0).astype(int)

print(f"\nCommunes par département:")
for dept in sorted(pivot['dep_code'].unique()):
    communes = pivot[pivot['dep_code'] == dept].shape[0]
    dept_name = pivot[pivot['dep_code'] == dept]['dep_name'].iloc[0]
    print(f"  Dpt {dept} ({dept_name}): {communes} communes")

print(f"\n\n📊 RÉSUMÉ VOTES PAR BLOC (2022):")
print(pivot[['vote_G', 'vote_C', 'vote_D', 'vote_ED']].sum())

print(f"\n\n📋 EXEMPLE (5 COMMUNES):")
print(pivot.head(10).to_string())

# Save
output_file = "data/processed/elections_2022_by_bloc_commune.csv"
pivot.to_csv(output_file, index=False, sep=';')
print(f"\n✅ Sauvegardé: {output_file}")
