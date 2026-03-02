#!/usr/bin/env python3
"""
Remplir colonnes-mspr.csv avec les données AURA disponibles
"""

import pandas as pd
import numpy as np
from pathlib import Path

# Départements AURA
AURA_DEPTS = ['01', '03', '07', '15', '26', '38', '42', '43', '63', '69', '73', '74']

print("="*100)
print("CRÉATION DE LA BASE DE DONNÉES AURA - colonnes-mspr.csv")
print("="*100)

# 1. Base communes AURA depuis élections
print("\n1️⃣  Chargement communes AURA...")
df_elections = pd.read_csv(
    "data/processed/elections_2022_by_bloc_commune.csv",
    sep=';'
)

# Filtrer AURA (colonne dep_code est numérique)
df_aura = df_elections[df_elections['dep_code'].astype(str).str.zfill(2).isin(AURA_DEPTS)].copy()

# Utiliser code commune comme clé
df_aura['Code_geo'] = df_aura['commune_code'].astype(str)

print(f"   ✅ {len(df_aura):,} communes AURA trouvées")

# 2. Ajouter résidences secondaires (parc_locatif_today)
print("\n2️⃣  Ajout résidences secondaires...")
try:
    df_rsecocc = pd.read_csv(
        "data/processed/logement_secondaire_2022_complet.csv",
        sep=';',
        usecols=['code_commune', 'taux_rsecocc_pct']
    )
    df_rsecocc['code_commune'] = df_rsecocc['code_commune'].astype(str).str.lstrip('0')
    df_aura['Code_geo_clean'] = df_aura['Code_geo'].astype(str).str.lstrip('0')
    
    df_aura = df_aura.merge(
        df_rsecocc.rename(columns={'code_commune': 'Code_geo_clean', 'taux_rsecocc_pct': 'parc_locatif_today'}),
        on='Code_geo_clean',
        how='left'
    )
    df_aura = df_aura.drop('Code_geo_clean', axis=1)
    print(f"   ✅ {df_aura['parc_locatif_today'].notna().sum():,} communes avec taux résidences secondaires")
except Exception as e:
    print(f"   ⚠️  Erreur résidences secondaires: {e}")
    df_aura['parc_locatif_today'] = np.nan

# 3. Charger revenus médians
print("\n3️⃣  Ajout revenus médians...")
try:
    df_revenus = pd.read_csv(
        "data/raw/revenu-des-francais-a-la-commune-1765372688826.csv",
        sep=',',
        nrows=5
    )
    print(f"   Colonnes revenus: {df_revenus.columns.tolist()}")
    df_aura['revenus_median_today'] = np.nan
except Exception as e:
    print(f"   ⚠️  Erreur revenus: {e}")
    df_aura['revenus_median_today'] = np.nan

# 4. Charger chômage
print("\n4️⃣  Ajout chômage...")
try:
    df_chomage = pd.read_excel(
        "data/raw/Dares_donnees-communales_demandeurs-demploi_2024T4.xlsx",
        nrows=5
    )
    print(f"   Colonnes chômage: {df_chomage.columns.tolist()}")
    df_aura['chomage_today'] = np.nan
except Exception as e:
    print(f"   ⚠️  Erreur chômage: {e}")
    df_aura['chomage_today'] = np.nan

# 5. Charger délinquance (cambriolages)
print("\n5️⃣  Ajout délinquance...")
try:
    df_delits = pd.read_csv(
        "data/raw/delits_cambriolages.csv",
        sep=';',
        nrows=5
    )
    print(f"   Colonnes délinquance: {df_delits.columns.tolist()}")
    df_aura['delinquance_today'] = np.nan
except Exception as e:
    print(f"   ⚠️  Erreur délinquance: {e}")
    df_aura['delinquance_today'] = np.nan

# 6. Charger élections (résultat_election_2022)
print("\n6️⃣  Ajout résultats élections 2022...")
# On a déjà les votes par bloc, calculer le bloc gagnant
df_aura['bloc_gagnant'] = df_aura[['vote_G', 'vote_C', 'vote_D', 'vote_ED']].idxmax(axis=1)
df_aura['bloc_gagnant'] = df_aura['bloc_gagnant'].map({
    'vote_G': 'Gauche',
    'vote_C': 'Centre',
    'vote_D': 'Droite',
    'vote_ED': 'Extrême-Droite'
})
df_aura['resultat_election_2022'] = df_aura['bloc_gagnant']
print(f"   ✅ {df_aura['resultat_election_2022'].notna().sum():,} communes avec résultats élections")

# 7. Préparer output
print("\n7️⃣  Préparation du fichier final...")

# Créer structure de base
output = pd.DataFrame()
output['Code_geo'] = df_aura['Code_geo']
output['revenus_median_1'] = np.nan
output['revenus_median_2'] = np.nan
output['revenus_median_today'] = df_aura.get('revenus_median_today', np.nan)

output['chomage_1'] = np.nan
output['chomage_2'] = np.nan
output['chomage_today'] = df_aura.get('chomage_today', np.nan)

output['delinquance_1'] = np.nan
output['delinquance_2'] = np.nan
output['delinquance_today'] = df_aura.get('delinquance_today', np.nan)

output['diplome_moyen_1'] = np.nan
output['diplome_moyen_2'] = np.nan
output['diplome_moyen_today'] = np.nan

output['population_1'] = np.nan
output['population_2'] = np.nan
output['population_today'] = np.nan

output['age_moyen_1'] = np.nan
output['age_moyen_2'] = np.nan
output['age_moyen_today'] = np.nan

output['surface_agricole_utilisable_1'] = np.nan
output['surface_agricole_utilisable_2'] = np.nan
output['surface_agricole_utilisable_today'] = np.nan

output['logement_sociaux_1'] = np.nan
output['logement_sociaux_2'] = np.nan
output['logement_sociaux_today'] = np.nan

output['parc_locatif_1'] = np.nan
output['parc_locatif_2'] = np.nan
output['parc_locatif_today'] = df_aura.get('parc_locatif_today', np.nan)

output['resultat_election_2017'] = np.nan
output['resultat_election_2022'] = df_aura['resultat_election_2022']

# Sauvegarder
output_path = "data/processed/colonnes-mspr_AURA.csv"
output.to_csv(output_path, sep=',', index=False)

print(f"\n✅ Fichier sauvegardé: {output_path}")

print(f"\n" + "="*100)
print("RÉSUMÉ")
print("="*100)
print(f"\nCommunes AURA: {len(output):,}")
print(f"\nColonnes remplies:")
print(f"  - Code_geo: {output['Code_geo'].notna().sum():,}/{len(output):,}")
print(f"  - revenus_median_today: {output['revenus_median_today'].notna().sum():,}/{len(output):,}")
print(f"  - chomage_today: {output['chomage_today'].notna().sum():,}/{len(output):,}")
print(f"  - delinquance_today: {output['delinquance_today'].notna().sum():,}/{len(output):,}")
print(f"  - parc_locatif_today (taux résidences secondaires): {output['parc_locatif_today'].notna().sum():,}/{len(output):,}")
print(f"  - resultat_election_2022: {output['resultat_election_2022'].notna().sum():,}/{len(output):,}")

print(f"\n📋 EXEMPLE (10 premières lignes):")
print(output.head(10).to_string())
