#!/usr/bin/env python3
"""
Reconstruire colonnes-mspr_AURA.csv complètement avec données 2017 et 2022
Base: élections qui ont les vrais codes communes et noms
"""

import pandas as pd
import numpy as np

print("="*100)
print("RECONSTRUCTION colonnes-mspr_AURA.csv - APPROCHE ÉLECTIONS")
print("="*100)

# Charger élections
print("\n1️⃣  Chargement élections...")
df_2017 = pd.read_csv("data/processed/elections_2017_by_bloc_commune_AURA.csv", sep=';',
                       usecols=['commune_code', 'commune_name', 'vote_G', 'vote_C', 'vote_D', 'vote_ED'],
                       dtype={'commune_code': 'str'})
df_2022 = pd.read_csv("data/processed/elections_2022_by_bloc_commune.csv", sep=';',
                       usecols=['commune_code', 'commune_name', 'vote_G', 'vote_C', 'vote_D', 'vote_ED'],
                       dtype={'commune_code': 'str'})

# Filtrer 2022 pour AURA
AURA_DEPTS = ['01', '03', '07', '15', '26', '38', '42', '43', '63', '69', '73', '74']
df_2022 = df_2022[df_2022['commune_code'].str[:2].isin(AURA_DEPTS)]

print(f"   2017: {len(df_2017):,} communes")
print(f"   2022: {len(df_2022):,} communes")

# Créer colonnes bloc gagnant
df_2017['resultat_election_2017'] = df_2017[['vote_G', 'vote_C', 'vote_D', 'vote_ED']].idxmax(axis=1).map({
    'vote_G': 'Gauche', 'vote_C': 'Centre', 'vote_D': 'Droite', 'vote_ED': 'Extrême-Droite'
})
df_2022['resultat_election_2022'] = df_2022[['vote_G', 'vote_C', 'vote_D', 'vote_ED']].idxmax(axis=1).map({
    'vote_G': 'Gauche', 'vote_C': 'Centre', 'vote_D': 'Droite', 'vote_ED': 'Extrême-Droite'
})

# Charger résidences secondaires
print("\n2️⃣  Chargement résidences secondaires...")
df_rsecocc = pd.read_csv("data/processed/logement_secondaire_2022_complet.csv", sep=';',
                          usecols=['code_commune', 'taux_rsecocc_pct'],
                          dtype={'code_commune': 'str'})

# Fusion des données
print("\n3️⃣  Fusion des données...")
# Commencer par 2017 (plus complet: 4095 communes)
# NOTE: élections_2017_by_bloc_commune_AURA.csv contient déjà des agrégations par commune
df_base = df_2017[['commune_code', 'commune_name', 'resultat_election_2017', 
                     'vote_G', 'vote_C', 'vote_D', 'vote_ED']].copy()
df_base.columns = ['Code_geo', 'commune_name', 'resultat_election_2017',  
                    'vote_G_2017', 'vote_C_2017', 'vote_D_2017', 'vote_ED_2017']

print(f"   Base 2017: {len(df_base):,} communes")

# Ajouter données élections 2022 (jointure sur commune_code)
# Mais d'abord enlever les doublons potentiels
df_2022_unique = df_2022[['commune_code', 'resultat_election_2022', 'vote_G', 'vote_C', 'vote_D', 'vote_ED']].copy()
df_2022_unique.columns = ['Code_geo', 'resultat_election_2022', 'vote_G_2022', 'vote_C_2022', 'vote_D_2022', 'vote_ED_2022']

# Remolure: pas de doublons si on fait .drop_duplicates sur Code_geo (garder première occurrence)
df_2022_unique = df_2022_unique.drop_duplicates('Code_geo', keep='first')

df_base = df_base.merge(df_2022_unique, on='Code_geo', how='left')

print(f"   Après ajout 2022: {len(df_base):,} communes")

# Ajouter résidences secondaires
df_base = df_base.merge(df_rsecocc.rename(columns={'code_commune': 'Code_geo'}), 
                         on='Code_geo', how='left')

print(f"   Résidences secondaires: {df_base['taux_rsecocc_pct'].notna().sum():,} remplies")

# Préparer colonnes finales
print("\n4️⃣  Préparation colonnes finales...")
output = pd.DataFrame()
output['Code_geo'] = df_base['Code_geo']

# Revenus
output['revenus_median_1'] = np.nan
output['revenus_median_2'] = np.nan
output['revenus_median_today'] = np.nan

# Chômage
output['chomage_1'] = np.nan
output['chomage_2'] = np.nan
output['chomage_today'] = np.nan

# Délinquance
output['delinquance_1'] = np.nan
output['delinquance_2'] = np.nan
output['delinquance_today'] = np.nan

# Diplômes
output['diplome_moyen_1'] = np.nan
output['diplome_moyen_2'] = np.nan
output['diplome_moyen_today'] = np.nan

# Population
output['population_1'] = np.nan
output['population_2'] = np.nan
output['population_today'] = np.nan

# Âge moyen
output['age_moyen_1'] = np.nan
output['age_moyen_2'] = np.nan
output['age_moyen_today'] = np.nan

# Surface agricole
output['surface_agricole_utilisable_1'] = np.nan
output['surface_agricole_utilisable_2'] = np.nan
output['surface_agricole_utilisable_today'] = np.nan

# Logements sociaux
output['logement_sociaux_1'] = np.nan
output['logement_sociaux_2'] = np.nan
output['logement_sociaux_today'] = np.nan

# Parc locatif (résidences secondaires)
output['parc_locatif_1'] = np.nan
output['parc_locatif_2'] = np.nan
output['parc_locatif_today'] = df_base['taux_rsecocc_pct']

# Elections
output['resultat_election_2017'] = df_base['resultat_election_2017']
output['resultat_election_2022'] = df_base['resultat_election_2022']

# Votes par bloc 2017
output['vote_G_2017'] = df_base['vote_G_2017']
output['vote_C_2017'] = df_base['vote_C_2017']
output['vote_D_2017'] = df_base['vote_D_2017']
output['vote_ED_2017'] = df_base['vote_ED_2017']

# Votes par bloc 2022
output['vote_G_2022'] = df_base['vote_G_2022']
output['vote_C_2022'] = df_base['vote_C_2022']
output['vote_D_2022'] = df_base['vote_D_2022']
output['vote_ED_2022'] = df_base['vote_ED_2022']

# Sauvegarder
print("\n5️⃣  Sauvegarde...")
output_path = "data/processed/colonnes-mspr_AURA.csv"
output.to_csv(output_path, sep=',', index=False)

print(f"\n✅ Fichier créé: {output_path}")

print(f"\n" + "="*100)
print("RÉSUMÉ")
print("="*100)

print(f"\nCommunes: {len(output):,}")
print(f"\nColonnes remplies:")
print(f"  Code_geo: {output['Code_geo'].notna().sum():,}/{len(output):,} (100%)")
print(f"  parc_locatif_today: {output['parc_locatif_today'].notna().sum():,}/{len(output):,} ({output['parc_locatif_today'].notna().sum()/len(output)*100:.1f}%)")
print(f"  resultat_election_2017: {output['resultat_election_2017'].notna().sum():,}/{len(output):,} ({output['resultat_election_2017'].notna().sum()/len(output)*100:.1f}%)")
print(f"  resultat_election_2022: {output['resultat_election_2022'].notna().sum():,}/{len(output):,} ({output['resultat_election_2022'].notna().sum()/len(output)*100:.1f}%)")
print(f"  vote_G_2017: {output['vote_G_2017'].notna().sum():,}/{len(output):,}")
print(f"  vote_G_2022: {output['vote_G_2022'].notna().sum():,}/{len(output):,}")

print(f"\n📊 DISTRIBUTION ÉLECTIONS 2017:")
print(output['resultat_election_2017'].value_counts())

print(f"\n📊 DISTRIBUTION ÉLECTIONS 2022:")
print(output['resultat_election_2022'].value_counts())

print(f"\n📋 EXEMPLE (10 premiers lignes):")
sample_cols = ['Code_geo', 'resultat_election_2017', 'resultat_election_2022', 
               'vote_G_2017', 'vote_ED_2017', 'vote_G_2022', 'vote_ED_2022', 'parc_locatif_today']
print(output[sample_cols].head(10).to_string(index=False))
