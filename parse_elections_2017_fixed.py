#!/usr/bin/env python3
"""
Parse 2017 elections with proper INSEE codes using mapping table
"""

import pandas as pd

print("Parsing 2017 elections with proper code mapping...")

# Load mapping
mapping = pd.read_csv("data/processed/commune_code_mapping.csv")
print(f"Mapping: {len(mapping):,} communes")

# Load 2017 source
df_2017 = pd.read_excel(
    "data/raw/Presidentielle_2017_Resultats_Communes_Tour_1_c(1).xls",
    sheet_name=0,
    header=3
)
print(f"2017 source: {len(df_2017):,} rows")

# Create mapping dict for quick lookup: (dep_code, local_code) -> insee_code
mapping['dept'] = mapping['code_local'].str[:2]
mapping['local'] = mapping['code_local'].str[2:].astype(str)
mapping_lookup = {}
for _, row in mapping.iterrows():
    key = (row['dept'], int(row['local']))
    mapping_lookup[key] = row['code_local']

# Process 2017 data
records = []

for idx, row in df_2017.iterrows():
    dept_code = str(row['Code du département']).zfill(2)
    local_code = int(row['Code de la commune'])
    commune_name = row['Libellé de la commune']
    exprimes = row['Exprimés']
    
    # Look up INSEE code
    key = (dept_code, local_code)
    if key not in mapping_lookup:
        continue
    
    insee_code = mapping_lookup[key]
    
    # Extract all candidates - they're in repeating pattern: Nom, Prénom, Voix with numeric suffixes
    # Columns: Nom (20), Voix (22), Nom.1 (27), Voix.1 (29), Nom.2 (34), Voix.2 (36), ...
    nom_cols = [col for col in df_2017.columns if 'Nom' in col and col != 'Libellé de la commune']
    
    for nom_col in nom_cols:
        if pd.isna(row[nom_col]):
            continue
        
        # Find corresponding Voix column
        # Nom -> Voix, Nom.1 -> Voix.1, etc.
        if nom_col == 'Nom':
            voix_col = 'Voix'
        else:
            suffix = nom_col.replace('Nom', '')
            voix_col = f'Voix{suffix}'
        
        if voix_col not in df_2017.columns or pd.isna(row[voix_col]):
            continue
        
        cand_nom = str(row[nom_col]).upper().strip()
        cand_voix = row[voix_col]
        
        if cand_voix > 0:  # Only include candidates with votes
            records.append({
                'insee_code': insee_code,
                'commune_name': commune_name,
                'cand_nom': cand_nom,
                'cand_nb_voix': cand_voix,
                'exprimes_nb': exprimes
            })

df_long = pd.DataFrame(records)
print(f"\nRecords created: {len(df_long):,}")

# Map candidates to blocs
candidates_2017 = {
    'ARTHAUD': 'G', 'MÉLENCHON': 'G', 'HAMON': 'G', 'POUTOU': 'G',
    'MACRON': 'C', 'CHEMINADE': 'C', 'BAYROU': 'C',
    'ASSELINEAU': 'D', 'FILLON': 'D', 'DUPONT-AIGNAN': 'D', 'LASSALLE': 'D',
    'LE PEN': 'ED'
}

df_long['bloc'] = df_long['cand_nom'].map(candidates_2017)
mapped = df_long['bloc'].notna().sum()
print(f"Blocs mapped: {mapped:,}/{len(df_long):,}")

# Show candidates found
print(f"\nCandidates found:")
for cand in sorted(df_long['cand_nom'].unique()):
    bloc = candidates_2017.get(cand, '?')
    print(f"  {cand}: {bloc}")

# Aggregate
agg = df_long[df_long['bloc'].notna()].groupby(
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
pivot['resultat_election_2017'] = pivot[['vote_G', 'vote_C', 'vote_D', 'vote_ED']].idxmax(axis=1).map({
    'vote_G': 'Gauche', 'vote_C': 'Centre', 'vote_D': 'Droite', 'vote_ED': 'Extrême-Droite'
})

print(f"\n✅ 2017: {len(pivot):,} communes")
print("Sample:")
print(pivot[['commune_code', 'commune_name', 'resultat_election_2017']].head(10))

# Save all-France
pivot.to_csv("data/processed/elections_2017_by_bloc_commune.csv", sep=';', index=False)
print(f"✅ Saved: data/processed/elections_2017_by_bloc_commune.csv")

# Extract AURA and save
AURA_DEPTS = ['01', '03', '07', '15', '26', '38', '42', '43', '63', '69', '73', '74']
pivot_aura = pivot[pivot['commune_code'].str[:2].isin(AURA_DEPTS)].copy()
pivot_aura.to_csv("data/processed/elections_2017_by_bloc_commune_AURA.csv", sep=';', index=False)
print(f"✅ AURA version: {len(pivot_aura):,} communes in data/processed/elections_2017_by_bloc_commune_AURA.csv")

# Verify codes
print(f"\nCode verification:")
print(f"  Unique: {pivot['commune_code'].nunique():,}")
print(f"  Sample: {pivot['commune_code'].unique()[:5].tolist()}")
print(f"  Bad (='1'): {(pivot['commune_code']=='1').sum()}")

