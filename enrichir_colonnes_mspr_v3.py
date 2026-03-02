#!/usr/bin/env python3
"""
Enrichir colonnes-mspr_AURA.csv avec données élections 2017 et 2022
Jointure basée sur les noms de communes
"""

import pandas as pd
import numpy as np

print("="*100)
print("ENRICHISSEMENT colonnes-mspr_AURA.csv (v2 - jointure par commune_name)")
print("="*100)

# 1. Charger colonnes-mspr + élections 2022 pour avoir les noms
print("\n1️⃣  Chargement fichiers...")
df_mspr = pd.read_csv("data/processed/colonnes-mspr_AURA.csv", dtype={'Code_geo': 'str'})

df_2022 = pd.read_csv("data/processed/elections_2022_by_bloc_commune.csv", sep=';',
                       usecols=['commune_code', 'commune_name', 'vote_G', 'vote_C', 'vote_D', 'vote_ED'],
                       dtype={'commune_code': 'str'})
AURA_DEPTS = ['01', '03', '07', '15', '26', '38', '42', '43', '63', '69', '73', '74']
df_2022 = df_2022[df_2022['commune_code'].str[:2].isin(AURA_DEPTS)]

df_2017 = pd.read_csv("data/processed/elections_2017_by_bloc_commune_AURA.csv", sep=';',
                       usecols=['commune_code', 'commune_name', 'vote_G', 'vote_C', 'vote_D', 'vote_ED'],
                       dtype={'commune_code': 'str'})

print(f"   colonnes-mspr: {len(df_mspr):,} communes")
print(f"   élections 2022: {len(df_2022):,} communes")
print(f"   élections 2017: {len(df_2017):,} communes")

# 2. Ajouter noms de communes à mspr via 2022
print("\n2️⃣  Ajout noms de communes...")
df_2022_names = df_2022[['commune_code', 'commune_name']].copy()
df_2022_names.columns = ['Code_geo', 'commune_name']

df_mspr = df_mspr.merge(df_2022_names, on='Code_geo', how='left')
print(f"   Communes avec noms: {df_mspr['commune_name'].notna().sum():,}/{len(df_mspr):,}")

# 3. Créer colonnes bloc gagnant pour 2017 et 2022
print("\n3️⃣  Création colonnes bloc gagnant...")
df_2017['resultat_election_2017'] = df_2017[['vote_G', 'vote_C', 'vote_D', 'vote_ED']].idxmax(axis=1).map({
    'vote_G': 'Gauche', 'vote_C': 'Centre', 'vote_D': 'Droite', 'vote_ED': 'Extrême-Droite'
})
df_2017 = df_2017[['commune_name', 'resultat_election_2017', 'vote_G', 'vote_C', 'vote_D', 'vote_ED']]
df_2017.columns = ['commune_name', 'resultat_election_2017', 'vote_G_2017', 'vote_C_2017', 'vote_D_2017', 'vote_ED_2017']

df_2022['resultat_election_2022'] = df_2022[['vote_G', 'vote_C', 'vote_D', 'vote_ED']].idxmax(axis=1).map({
    'vote_G': 'Gauche', 'vote_C': 'Centre', 'vote_D': 'Droite', 'vote_ED': 'Extrême-Droite'
})
df_2022 = df_2022[['commune_name', 'resultat_election_2022', 'vote_G', 'vote_C', 'vote_D', 'vote_ED']]
df_2022.columns = ['commune_name', 'resultat_election_2022', 'vote_G_2022', 'vote_C_2022', 'vote_D_2022', 'vote_ED_2022']

# 4. Joindre par commune_name
print("\n4️⃣  Jointure par commune_name...")
df_result = df_mspr.merge(df_2017, on='commune_name', how='left')
df_result = df_result.merge(df_2022, on='commune_name', how='left')

print(f"   2017 matchées: {df_result['resultat_election_2017'].notna().sum():,}/{len(df_result):,}")
print(f"   2022 matchées: {df_result['resultat_election_2022'].notna().sum():,}/{len(df_result):,}")

# 5. Sauvegarder
print("\n5️⃣  Sauvegarde...")
# Garder le fichier petit - juste les colonnes essentielles
output = pd.DataFrame()
output['Code_geo'] = df_result['Code_geo']
output['commune_name'] = df_result['commune_name']

# Données historiques (qu'on n'a pas)
output['revenus_median_1'] = np.nan
output['revenus_median_2'] = np.nan
output['revenus_median_today'] = df_result['revenus_median_today']

output['chomage_1'] = np.nan
output['chomage_2'] = np.nan
output['chomage_today'] = df_result['chomage_today']

output['delinquance_1'] = np.nan
output['delinquance_2'] = np.nan
output['delinquance_today'] = df_result['delinquance_today']

output['diplome_moyen_1'] = np.nan
output['diplome_moyen_2'] = np.nan
output['diplome_moyen_today'] = df_result['diplome_moyen_today']

output['population_1'] = np.nan
output['population_2'] = np.nan
output['population_today'] = df_result['population_today']

output['age_moyen_1'] = np.nan
output['age_moyen_2'] = np.nan
output['age_moyen_today'] = df_result['age_moyen_today']

output['surface_agricole_utilisable_1'] = np.nan
output['surface_agricole_utilisable_2'] = np.nan
output['surface_agricole_utilisable_today'] = df_result['surface_agricole_utilisable_today']

output['logement_sociaux_1'] = np.nan
output['logement_sociaux_2'] = np.nan
output['logement_sociaux_today'] = df_result['logement_sociaux_today']

# Parc locatif (résidences secondaires)
output['parc_locatif_1'] = np.nan
output['parc_locatif_2'] = np.nan
output['parc_locatif_today'] = df_result['parc_locatif_today']

# Elections: résultats (bloc gagnant) et votes
output['resultat_election_2017'] = df_result['resultat_election_2017']
output['resultat_election_2022'] = df_result['resultat_election_2022']

output['vote_G_2017'] = df_result['vote_G_2017']
output['vote_C_2017'] = df_result['vote_C_2017']
output['vote_D_2017'] = df_result['vote_D_2017']
output['vote_ED_2017'] = df_result['vote_ED_2017']

output['vote_G_2022'] = df_result['vote_G_2022']
output['vote_C_2022'] = df_result['vote_C_2022']
output['vote_D_2022'] = df_result['vote_D_2022']
output['vote_ED_2022'] = df_result['vote_ED_2022']

# Supprimer commune_name de la sortie (garder la structure d'origine)
output = output.drop('commune_name', axis=1)

output_path = "data/processed/colonnes-mspr_AURA.csv"
output.to_csv(output_path, sep=',', index=False)

print(f"\n✅ Fichier enrichi: {output_path}")
print(f"\n📊 RÉSUMÉ")
print(f"   Colonnes: {len(output.columns)}")
print(f"   Communes: {len(output)}")
print(f"\n   Remplissage:")
print(f"     - Code_geo: {output['Code_geo'].notna().sum():,}/{len(output):,} (100%)")
print(f"     - parc_locatif_today: {output['parc_locatif_today'].notna().sum():,}/{len(output):,}")
print(f"     - resultat_election_2017: {output['resultat_election_2017'].notna().sum():,}/{len(output):,}")
print(f"     - resultat_election_2022: {output['resultat_election_2022'].notna().sum():,}/{len(output):,}")
print(f"     - vote_G_2017: {output['vote_G_2017'].notna().sum():,}/{len(output):,}")
print(f"     - vote_G_2022: {output['vote_G_2022'].notna().sum():,}/{len(output):,}")

print(f"\n📋 EXEMPLE (5 communes):")
example_cols = ['Code_geo', 'resultat_election_2017', 'resultat_election_2022', 
                'vote_G_2017', 'vote_ED_2017', 'vote_G_2022', 'vote_ED_2022']
print(output[example_cols].head(5).to_string(index=False))
