#!/usr/bin/env python3
"""
Parse 2017 presidential election results and aggregate votes by political bloc
Similar to parse_elections_by_bloc.py but for 2017
"""

import pandas as pd
import numpy as np

# 2017 Presidential Candidates Mapping
candidates_to_bloc_2017 = {
    # Extrême Droite (vote_ED)
    'LE PEN': 'ED',        # Marine Le Pen - FN
    
    # Droite (vote_D)
    'FILLON': 'D',         # François Fillon - LR
    'ASSELINEAU': 'D',     # François Asselineau - UPR (independent right)
    'DUPONT-AIGNAN': 'D',  # Dupont-Aignan - Independent right-wing
    'LASSALLE': 'D',       # Jean Lassalle - Independent (center-right/rural)
    
    # Centre (vote_C)
    'MACRON': 'C',         # Emmanuel Macron - En Marche/LREM
    'BAYROU': 'C',         # François Bayrou - Modem
    'CHEMINADE': 'C',      # Jacques Cheminade - Independent (esoteric)
    
    # Gauche (vote_G)  
    'MÉLENCHON': 'G',      # Jean-Luc Mélenchon - LFI (was earlier)
    'HAMON': 'G',          # Benoît Hamon - PS
    'JADOT': 'G',          # Yannick Jadot - EELV
    'POUTOU': 'G',         # Philippe Poutou - NPA
    'ARTHAUD': 'G',        # Nathalie Arthaud - LO
}

# Load 2017 data
print("Loading 2017 election data...")
df_2017 = pd.read_excel(
    "data/raw/Presidentielle_2017_Resultats_Communes_Tour_1_c(1).xls",
    sheet_name=0,
    header=3
)

print(f"Loaded {len(df_2017):,} rows")
print(f"\nColumns sample (0-30):")
for i in range(min(30, len(df_2017.columns))):
    print(f"  {i}: {df_2017.columns[i]}")

# Extract candidate names from "Nom" columns
print(f"\n" + "="*100)
print("EXTRACTING CANDIDATES")
print("="*100)

# Find all "Nom" columns (candidate names)
nom_cols = [i for i, col in enumerate(df_2017.columns) if col == 'Nom' or 'Nom' in str(col)]
voix_cols = [i for i, col in enumerate(df_2017.columns) if col == 'Voix' or 'Voix' in str(col)]

print(f"\nFound {len(nom_cols)} candidate slots")
print(f"Nom columns: {nom_cols}")
print(f"Voix columns: {voix_cols}")

# Get unique candidates
candidates_2017 = set()
for col_idx in nom_cols:
    col_name = df_2017.columns[col_idx]
    candidates = df_2017[col_name].dropna().unique()
    candidates_2017.update(candidates)

print(f"\nUnique candidates ({len(candidates_2017)}):")
for cand in sorted(candidates_2017):
    print(f"  - {cand}")

# Map candidates to blocs
print(f"\n" + "="*100)
print("MAPPING CANDIDATES TO BLOCS")
print("="*100)

# Create long format: one row per candidate per commune
records = []

# Iterate through nom/voix column pairs
for nom_idx, voix_idx in zip(nom_cols, voix_cols):
    nom_col = df_2017.columns[nom_idx]
    voix_col = df_2017.columns[voix_idx]
    
    for idx, row in df_2017.iterrows():
        if pd.notna(row[nom_col]) and pd.notna(row[voix_col]):
            records.append({
                'commune_code': row['Code de la commune'],
                'commune_name': row['Libellé de la commune'],
                'dep_code': row['Code du département'],
                'dep_name': row['Libellé du département'],
                'cand_nom': str(row[nom_col]).upper(),
                'cand_nb_voix': row[voix_col],
                'exprimes_nb': row['Exprimés']
            })

df_long = pd.DataFrame(records)
print(f"\nCreated {len(df_long):,} candidate vote records")

# Map to blocs
df_long['bloc'] = df_long['cand_nom'].map(candidates_to_bloc_2017)

# Check unmapped
unmapped = df_long[df_long['bloc'].isna()]['cand_nom'].unique()
if len(unmapped) > 0:
    print(f"\n⚠️  UNMAPPED CANDIDATES: {len(unmapped)}")
    for cand in sorted(unmapped):
        print(f"  - {cand}")

print(f"\nMapped candidates:")
for cand, bloc in candidates_to_bloc_2017.items():
    count = (df_long['cand_nom'] == cand).sum()
    if count > 0:
        print(f"  ✅ {cand:20s} → {bloc} ({count:,} rows)")

# Aggregate by commune and bloc
print(f"\n" + "="*100)
print("AGGREGATION PAR COMMUNE ET BLOC")
print("="*100)

agg = df_long[df_long['bloc'].notna()].groupby(
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

# Ensure all bloc columns exist (fill with 0 if missing)
for col in ['vote_C', 'vote_D', 'vote_ED', 'vote_G']:
    if col not in pivot.columns:
        pivot[col] = 0
    else:
        pivot[col] = pivot[col].fillna(0).astype(int)

# Convert dep_code to int for sorting
pivot['dep_code'] = pd.to_numeric(pivot['dep_code'], errors='coerce').fillna(0).astype(int)

print(f"\nCommunes par département:")
for dept in sorted(pivot['dep_code'].unique()):
    communes = pivot[pivot['dep_code'] == dept].shape[0]
    dept_name = pivot[pivot['dep_code'] == dept]['dep_name'].iloc[0] if len(pivot[pivot['dep_code'] == dept]) > 0 else "?"
    print(f"  Dpt {int(dept)} ({dept_name}): {communes} communes")

print(f"\n\n📊 RÉSUMÉ VOTES PAR BLOC (2017):")
print(pivot[['vote_G', 'vote_C', 'vote_D', 'vote_ED']].sum())

print(f"\n\n📋 EXEMPLE (10 COMMUNES):")
print(pivot.head(10).to_string())

# Save
output_file = "data/processed/elections_2017_by_bloc_commune.csv"
pivot.to_csv(output_file, sep=';', index=False)
print(f"\n✅ Sauvegardé: {output_file}")
