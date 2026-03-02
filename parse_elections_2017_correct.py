#!/usr/bin/env python3
"""
Créer elections_2017_by_bloc_commune avec vraiscodes communes INSEE
Approche: joindre les données 2017 avec les codes communes du fichier 2022
"""

import pandas as pd
import numpy as np

print("Création élections 2017 with vrais codes communes INSEE...")

# 1. Charger 2017 avec données de base
df_2017 = pd.read_excel(
    "data/raw/Presidentielle_2017_Resultats_Communes_Tour_1_c(1).xls",
    sheet_name=0,
    header=3
)

# 2. Charger 2022 pour avoir les codes communes INSEE par nom
df_2022 = pd.read_csv(
    "data/processed/elections_2022_by_bloc_commune.csv",
    sep=';',
    usecols=['commune_code', 'commune_name'],
    dtype={'commune_code': 'str'}
).drop_duplicates('commune_name')

print(f"2017 Excel: {len(df_2017):,} rows")
print(f"2022 codes: {len(df_2022):,} communes")

# 3. Nettoyer les noms des communes pour la jointure
# Normaliser les noms (accents, casse, etc.)
def normalize_name(s):
    if pd.isna(s):
        return ""
    s = str(s).strip().upper()
   # Remplacer les caractères accentués
    replacements = {
        'É': 'E', 'È': 'E', 'Ê': 'E', 'Ë': 'E',
        'À': 'A', 'Â': 'A', 'Ä': 'A',
        'Ô': 'O', 'Ö': 'O',
        'Ù': 'U', 'Û': 'U', 'Ü': 'U',
        'Ç': 'C', 'Ï': 'I'
    }
    for old, new in replacements.items():
        s = s.replace(old, new).replace(old.lower(), new.lower())
    return s

df_2017['commune_name_norm'] = df_2017['Libellé de la commune'].apply(normalize_name)
df_2022['commune_name_norm'] = df_2022['commune_name'].apply(normalize_name)

# 4. Joindre 2017 avec codes communes
df_2017_with_codes = df_2017.merge(
    df_2022[['commune_code', 'commune_name_norm']],
    on='commune_name_norm',
    how='left'
)

matched = df_2017_with_codes['commune_code'].notna().sum()
print(f"\nCode communes matchés: {matched:,}/{len(df_2017):,} ({matched/len(df_2017)*100:.1f}%)")

# 5. Mapper candidats aux blocs
candidates_to_bloc_2017 = {
    'LE PEN': 'ED', 'FILLON': 'D', 'ASSELINEAU': 'D', 'DUPONT-AIGNAN': 'D', 
    'LASSALLE': 'D', 'MACRON': 'C', 'CHEMINADE': 'C', 'MÉLENCHON': 'G', 
    'HAMON': 'G', 'POUTOU': 'G', 'ARTHAUD': 'G'
}

# 6. Créer records pour agrégation
records = []
nom_cols = [i for i, col in enumerate(df_2017_with_codes.columns) if col == 'Nom' or 'Nom' in str(col)]
voix_cols = [i for i, col in enumerate(df_2017_with_codes.columns) if col == 'Voix' or 'Voix' in str(col)]

for idx, row in df_2017_with_codes.iterrows():
    commune_code = row['commune_code']
    commune_name = row['Libellé de la commune']
    
    if pd.isna(commune_code):
        continue
    
    for nom_idx, voix_idx in zip(nom_cols, voix_cols):
        nom_col = df_2017_with_codes.columns[nom_idx]
        voix_col = df_2017_with_codes.columns[voix_idx]
        
        if pd.notna(row[nom_col]) and pd.notna(row[voix_col]):
            records.append({
                'commune_code': str(commune_code),
                'commune_name': commune_name,
                'cand_nom': str(row[nom_col]).upper(),
                'cand_nb_voix': row[voix_col],
                'exprimes_nb': row['Exprimés']
            })

df_long = pd.DataFrame(records)
df_long['bloc'] = df_long['cand_nom'].map(candidates_to_bloc_2017)

print(f"\nRecords candidats: {len(df_long):,}")
print(f"Blocs mappés: {df_long['bloc'].notna().sum():,}")

# 7. Agréger par commune et bloc
agg = df_long[df_long['bloc'].notna()].groupby(
    ['commune_code', 'commune_name', 'bloc']
).agg({
    'cand_nb_voix': 'sum',
    'exprimes_nb': 'first'
}).reset_index()

# Pivot
pivot = agg.pivot_table(
    index=['commune_code', 'commune_name', 'exprimes_nb'],
    columns='bloc',
    values='cand_nb_voix',
    fill_value=0
).reset_index()

pivot.columns.name = None
pivot.columns = ['commune_code', 'commune_name', 'exprimes_nb', 'vote_C', 'vote_D', 'vote_ED', 'vote_G']

# Ajouter colonne bloc gagnant
pivot['resultat_election_2017'] = pivot[['vote_G', 'vote_C', 'vote_D', 'vote_ED']].idxmax(axis=1).map({
    'vote_G': 'Gauche', 'vote_C': 'Centre', 'vote_D': 'Droite', 'vote_ED': 'Extrême-Droite'
})

print(f"\n✅ Communes avec votes agrégés: {len(pivot):,}")
print(f"Exemple:")
print(pivot.head(5))

# 8. Sauvegarder FICHIER COMPLET
output_file_all = "data/processed/elections_2017_by_bloc_commune.csv"
pivot.to_csv(output_file_all, sep=';', index=False)
print(f"\n✅ Fichier all-France: {output_file_all}")

# 9. Sauvegarder VERSION AURA
AURA_DEPTS = ['01', '03', '07', '15', '26', '38', '42', '43', '63', '69', '73', '74']
df_aura = pivot[pivot['commune_code'].str[:2].isin(AURA_DEPTS)].copy()

output_file_aura = "data/processed/elections_2017_by_bloc_commune_AURA.csv"
df_aura.to_csv(output_file_aura, sep=';', index=False)
print(f"✅ Fichier AURA: {output_file_aura}")
print(f"   {len(df_aura):,} communes AURA")
