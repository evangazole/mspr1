#!/usr/bin/env python3
"""
Remplir colonnes-mspr.csv avec les données AURA disponibles - VERSION CORRIGÉE
Utiliser les VRAIS codes communes INSEE
"""

import pandas as pd
import numpy as np

# Départements AURA
AURA_DEPTS = ['01', '03', '07', '15', '26', '38', '42', '43', '63', '69', '73', '74']

print("="*100)
print("CRÉATION DE LA BASE DE DONNÉES AURA - AVEC VRAIS CODES COMMUNES INSEE")
print("="*100)

# 1. Charger communes AURA depuis élections (avec vrais codes communes)
print("\n1️⃣  Chargement communes AURA avec vrais codes communes...")
df_elections_raw = pd.read_csv(
    "data/raw/elections_2022_2017.csv",
    sep=';',
    usecols=['code_commune', 'libelle_commune', 'id_election'],
    dtype={'code_commune': 'str'}
)

# Filtrer pour seulement 2022 et communes AURA
df_elections_raw = df_elections_raw[
    (df_elections_raw['id_election'] == '2022_pres_t1') &
    (df_elections_raw['code_commune'].str[:2].isin(AURA_DEPTS))
].drop_duplicates('code_commune')

print(f"   ✅ {len(df_elections_raw):,} communes AURA trouvées")

# 2. Charger élections par bloc (créé par parse_elections_by_bloc.py)
print("\n2️⃣  Chargement résultats élections par bloc...")
df_blocs = pd.read_csv(
    "data/processed/elections_2022_by_bloc_commune.csv",
    sep=';'
)

# Matcher par nom de commune et filtrer AURA
df_blocs = df_blocs.merge(
    df_elections_raw.rename(columns={'code_commune': 'code_commune_insee'}),
    left_on='commune_name',
    right_on='libelle_commune',
    how='inner'
)

print(f"   ✅ {len(df_blocs):,} communes matchées")

# 3. Charger résidences secondaires
print("\n3️⃣  Chargement résidences secondaires...")
try:
    df_rsecocc = pd.read_csv(
        "data/processed/logement_secondaire_2022_complet.csv",
        sep=';',
        usecols=['code_commune', 'commune_name', 'taux_rsecocc_pct'],
        dtype={'code_commune': 'str'}
    )
    
    df_blocs = df_blocs.merge(
        df_rsecocc[['code_commune', 'taux_rsecocc_pct']],
        left_on='code_commune_insee',
        right_on='code_commune',
        how='left'
    )
    print(f"   ✅ {df_blocs['taux_rsecocc_pct'].notna().sum():,} communes avec résidences secondaires")
except Exception as e:
    print(f"   ⚠️  Erreur: {e}")
    df_blocs['taux_rsecocc_pct'] = np.nan

# 4. Préparer output
print("\n4️⃣  Préparation output...")

output = pd.DataFrame()
output['Code_geo'] = df_blocs['code_commune_insee']
output['commune_name'] = df_blocs['commune_name']

# Colonnes de revenus
output['revenus_median_1'] = np.nan
output['revenus_median_2'] = np.nan
output['revenus_median_today'] = np.nan

# Colonnes de chômage
output['chomage_1'] = np.nan
output['chomage_2'] = np.nan
output['chomage_today'] = np.nan

# Colonnes de délinquance
output['delinquance_1'] = np.nan
output['delinquance_2'] = np.nan
output['delinquance_today'] = np.nan

# Colonnes de diplômes
output['diplome_moyen_1'] = np.nan
output['diplome_moyen_2'] = np.nan
output['diplome_moyen_today'] = np.nan

# Colonnes de population
output['population_1'] = np.nan
output['population_2'] = np.nan
output['population_today'] = np.nan

# Colonnes d'âge
output['age_moyen_1'] = np.nan
output['age_moyen_2'] = np.nan
output['age_moyen_today'] = np.nan

# Colonnes de surface agricole
output['surface_agricole_utilisable_1'] = np.nan
output['surface_agricole_utilisable_2'] = np.nan
output['surface_agricole_utilisable_today'] = np.nan

# Colonnes de logements sociaux
output['logement_sociaux_1'] = np.nan
output['logement_sociaux_2'] = np.nan
output['logement_sociaux_today'] = np.nan

# Colonnes parc locatif (utiliser taux résidences secondaires)
output['parc_locatif_1'] = np.nan
output['parc_locatif_2'] = np.nan
output['parc_locatif_today'] = df_blocs['taux_rsecocc_pct']

# Résultats élections
output['resultat_election_2017'] = np.nan
output['resultat_election_2022'] = df_blocs[['vote_G', 'vote_C', 'vote_D', 'vote_ED']].idxmax(axis=1).map({
    'vote_G': 'Gauche',
    'vote_C': 'Centre',
    'vote_D': 'Droite',
    'vote_ED': 'Extrême-Droite'
})

# Sauvegarder (sans la colonne commune_name)
output_no_name = output.drop('commune_name', axis=1)
output_path = "data/processed/colonnes-mspr_AURA.csv"
output_no_name.to_csv(output_path, sep=',', index=False)

print(f"\n✅ Fichier sauvegardé: {output_path}")

print(f"\n" + "="*100)
print("RÉSUMÉ")
print("="*100)
print(f"\nCommunes AURA: {len(output):,}")
print(f"\nColonnes remplies:")
print(f"  - Code_geo: {output['Code_geo'].notna().sum():,}/{len(output):,}")
print(f"  - parc_locatif_today (taux résidences secondaires): {output['parc_locatif_today'].notna().sum():,}/{len(output):,}")
print(f"  - resultat_election_2022: {output['resultat_election_2022'].notna().sum():,}/{len(output):,}")

# Afficher exemple avec noms pour vérif
sample = output[['Code_geo', 'commune_name', 'parc_locatif_today', 'resultat_election_2022']].head(20)
print(f"\n📋 EXEMPLE (20 premières communes):")
print(sample.to_string(index=False))

print(f"\n\n✅ Distribution des résultats élections 2022:")
print(output['resultat_election_2022'].value_counts())
