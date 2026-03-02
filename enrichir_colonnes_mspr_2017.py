#!/usr/bin/env python3
"""
Ajouter les données élections 2017 au fichier colonnes-mspr_AURA.csv
"""

import pandas as pd
import numpy as np

print("="*100)
print("ENRICHISSEMENT colonnes-mspr_AURA.csv AVEC DONNÉES ÉLECTIONS 2017")
print("="*100)

# 1. Charger colonnes-mspr actuel
print("\n1️⃣  Chargement colonnes-mspr_AURA.csv...")
df_mspr = pd.read_csv(
    "data/processed/colonnes-mspr_AURA.csv",
    dtype={'Code_geo': 'str'}
)
print(f"   ✅ {len(df_mspr):,} communes")

# 2. Charger élections 2017 AURA
print("\n2️⃣  Chargement élections 2017 AURA...")
df_2017 = pd.read_csv(
    "data/processed/elections_2017_by_bloc_commune_AURA.csv",
    sep=';',
    dtype={'commune_code': 'str'}
)
print(f"   ✅ {len(df_2017):,} communes")

# 3. Joindre les données
print("\n3️⃣  Jointure données 2017 avec colonnes-mspr...")

# Créer colonne de bloc gagnant 2017
df_2017['resultat_election_2017'] = df_2017[['vote_G', 'vote_C', 'vote_D', 'vote_ED']].idxmax(axis=1).map({
    'vote_G': 'Gauche',
    'vote_C': 'Centre',
    'vote_D': 'Droite',
    'vote_ED': 'Extrême-Droite'
})

# Joindre
df_2017_extract = df_2017[['commune_code', 'resultat_election_2017', 'vote_G', 'vote_C', 'vote_D', 'vote_ED']].copy()
df_2017_extract.columns = ['Code_geo', 'resultat_election_2017', 'vote_G_2017', 'vote_C_2017', 'vote_D_2017', 'vote_ED_2017']

# Vérifier les codes communes
print(f"   Code_geo types in mspr: {df_mspr['Code_geo'].dtype}")
print(f"   Code_geo types in 2017: {df_2017_extract['Code_geo'].dtype}")
print(f"   Sample codes mspr: {df_mspr['Code_geo'].head(3).tolist()}")
print(f"   Sample codes 2017: {df_2017_extract['Code_geo'].head(3).tolist()}")

df_merged = df_mspr.merge(
    df_2017_extract,
    on='Code_geo',
    how='left'
)

print(f"   Commune avec données 2017: {df_merged['resultat_election_2017'].notna().sum():,}/{len(df_merged):,}")

# 4. Réorganiser les colonnes (années: 2017 avant 2022)
print("\n4️⃣  Réorganisation des colonnes...")

output = pd.DataFrame()
output['Code_geo'] = df_merged['Code_geo']

# Revenus
output['revenus_median_1'] = np.nan
output['revenus_median_2'] = np.nan
output['revenus_median_today'] = df_merged['revenus_median_today']

# Chômage
output['chomage_1'] = np.nan
output['chomage_2'] = np.nan
output['chomage_today'] = df_merged['chomage_today']

# Délinquance
output['delinquance_1'] = np.nan
output['delinquance_2'] = np.nan
output['delinquance_today'] = df_merged['delinquance_today']

# Diplômed
output['diplome_moyen_1'] = np.nan
output['diplome_moyen_2'] = np.nan
output['diplome_moyen_today'] = df_merged['diplome_moyen_today']

# Population
output['population_1'] = np.nan
output['population_2'] = np.nan
output['population_today'] = df_merged['population_today']

# Âge moyen
output['age_moyen_1'] = np.nan
output['age_moyen_2'] = np.nan
output['age_moyen_today'] = df_merged['age_moyen_today']

# Surface agricole
output['surface_agricole_utilisable_1'] = np.nan
output['surface_agricole_utilisable_2'] = np.nan
output['surface_agricole_utilisable_today'] = df_merged['surface_agricole_utilisable_today']

# Logements sociaux
output['logement_sociaux_1'] = np.nan
output['logement_sociaux_2'] = np.nan
output['logement_sociaux_today'] = df_merged['logement_sociaux_today']

# Parc locatif (résidences secondaires)
output['parc_locatif_1'] = np.nan
output['parc_locatif_2'] = np.nan
output['parc_locatif_today'] = df_merged['parc_locatif_today']

# Résultats élections (2017 avant 2022)
output['resultat_election_2017'] = df_merged['resultat_election_2017']
output['resultat_election_2022'] = df_merged['resultat_election_2022']

# Votes par bloc 2017
output['vote_G_2017'] = df_merged['vote_G_2017']
output['vote_C_2017'] = df_merged['vote_C_2017']
output['vote_D_2017'] = df_merged['vote_D_2017']
output['vote_ED_2017'] = df_merged['vote_ED_2017']

# Votes par bloc 2022 (charger à partir de elections_2022)
print("\n5️⃣  Ajout votes par bloc 2022...")
df_2022 = pd.read_csv(
    "data/processed/elections_2022_by_bloc_commune.csv",
    sep=';',
    dtype={'commune_code': 'str'}
)

# Filtrer AURA
AURA_DEPTS = ['01', '03', '07', '15', '26', '38', '42', '43', '63', '69', '73', '74']
df_2022_aura = df_2022[df_2022['commune_code'].str[:2].isin(AURA_DEPTS)].copy()

df_2022_extract = df_2022_aura[['commune_code', 'vote_G', 'vote_C', 'vote_D', 'vote_ED']].copy()
df_2022_extract.columns = ['Code_geo', 'vote_G_2022', 'vote_C_2022', 'vote_D_2022', 'vote_ED_2022']

# Joindre avec output
output = output.merge(df_2022_extract, on='Code_geo', how='left')

print(f"   Communes avec votes 2022: {output['vote_G_2022'].notna().sum():,}/{len(output):,}")

# 5. Sauvegarder
print("\n6️⃣  Sauvegarde...")
output_file = "data/processed/colonnes-mspr_AURA.csv"
output.to_csv(output_file, sep=',', index=False)

print(f"\n✅ Fichier mis à jour: {output_file}")

# Afficher résumé
print(f"\n" + "="*100)
print("RÉSUMÉ")
print("="*100)

print(f"\nColonnes remplies:")
print(f"  Code_geo: {output['Code_geo'].notna().sum():,}/{len(output):,}")
print(f"  resultat_election_2017: {output['resultat_election_2017'].notna().sum():,}/{len(output):,}")
print(f"  resultat_election_2022: {output['resultat_election_2022'].notna().sum():,}/{len(output):,}")
print(f"  vote_G_2017: {output['vote_G_2017'].notna().sum():,}/{len(output):,}")
print(f"  vote_G_2022: {output['vote_G_2022'].notna().sum():,}/{len(output):,}")
print(f"  parc_locatif_today: {output['parc_locatif_today'].notna().sum():,}/{len(output):,}")

print(f"\n📋 COLONNES DU FICHIER:")
print(output.columns.tolist())

print(f"\n📊 EXEMPLE (5 lignes):")
sample_cols = ['Code_geo', 'resultat_election_2017', 'resultat_election_2022', 
               'vote_G_2017', 'vote_ED_2017', 'vote_G_2022', 'vote_ED_2022', 'parc_locatif_today']
print(output[sample_cols].head(5).to_string(index=False))
