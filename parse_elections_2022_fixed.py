#!/usr/bin/env python3
"""
Parse 2022 elections with code_local + dep_code to get INSEE codes
"""

import pandas as pd

print("Parsing 2022 elections with proper code mapping...")

# Load mapping - code_local is actually the INSEE code
mapping = pd.read_csv("data/processed/commune_code_mapping.csv")
# Extract dept and local from code_local
mapping['dept'] = mapping['code_local'].str[:2]
mapping['local'] = mapping['code_local'].str[2:].astype(int)

print(f"Mapping: {len(mapping):,} communes")

# Load 2022 source
df_2022 = pd.read_csv(
    "data/raw/04-resultats-par-commune(1).csv",
    dtype={'dep_code': 'str'}
)
print(f"2022 source: {len(df_2022):,} records")

# Merge: join on dep_code + commune_code
df_2022['comm_code_int'] = pd.to_numeric(df_2022['commune_code'], errors='coerce')
df_2022 = df_2022[df_2022['comm_code_int'].notna()].copy()  # Filter out non-numeric codes

df_2022 = df_2022.merge(
    mapping[['dept', 'local', 'insee_code']],
    left_on=['dep_code', 'comm_code_int'],
    right_on=['dept', 'local'],
    how='left'
)

matched = df_2022['insee_code'].notna().sum()
print(f"Codes matched: {matched:,}/{len(df_2022):,} ({matched/len(df_2022)*100:.1f}%)")

# Drop rows without code
df_2022 = df_2022[df_2022['insee_code'].notna()].copy()

# Map candidates to blocs
candidates_2022 = {
    'ARTHAUD': 'G', 'ROUSSEL': 'G', 'MÉLENCHON': 'G', 'HIDALGO': 'G', 'POUTOU': 'G',
    'MACRON': 'C', 'LASSALLE': 'C', 'JADOT': 'C',
    'PÉCRESSE': 'D', 'DUPONT-AIGNAN': 'D',
    'LE PEN': 'ED', 'ZEMMOUR': 'ED'
}

df_2022['bloc'] = df_2022['cand_nom'].map(candidates_2022)
mapped_blocs = df_2022['bloc'].notna().sum()
print(f"Blocs mapped: {mapped_blocs:,}/{len(df_2022):,}")

# Aggregate
agg = df_2022[df_2022['bloc'].notna()].groupby(
    ['insee_code', 'bloc']
).agg({
    'cand_nb_voix': 'sum',
    'exprimes_nb': 'first',
    'commune_name': 'first'
}).reset_index()

# Pivot
pivot = agg.pivot_table(
    index=['insee_code', 'commune_name', 'exprimes_nb'],
    columns='bloc',
    values='cand_nb_voix',
    fill_value=0
).reset_index()

pivot.columns.name = None
pivot.columns = ['commune_code', 'commune_name', 'exprimes_nb', 'vote_C', 'vote_D', 'vote_ED', 'vote_G']

# Add winning bloc
pivot['resultat_election_2022'] = pivot[['vote_G', 'vote_C', 'vote_D', 'vote_ED']].idxmax(axis=1).map({
    'vote_G': 'Gauche', 'vote_C': 'Centre', 'vote_D': 'Droite', 'vote_ED': 'Extrême-Droite'
})

print(f"\n✅ 2022: {len(pivot):,} communes")
print("Sample:")
print(pivot[['commune_code', 'commune_name', 'resultat_election_2022']].head(10))

# Save all-France
pivot.to_csv("data/processed/elections_2022_by_bloc_commune.csv", sep=';', index=False)
print(f"✅ Saved: data/processed/elections_2022_by_bloc_commune.csv")

# Verify codes
print(f"\nCode verification:")
print(f"  Unique: {pivot['commune_code'].nunique():,}")
print(f"  Sample: {pivot['commune_code'].unique()[:5].tolist()}")
print(f"  Bad (='1'): {(pivot['commune_code']=='1').sum()}")
print(f"  Format example: {pivot['commune_code'].iloc[0]}")
