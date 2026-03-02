#!/usr/bin/env python3
"""
Create master AURA dataset file with 2017 and 2022 elections + secondary residences
Using corrected election files with proper INSEE codes
"""

import pandas as pd
import numpy as np

print("Building master AURA dataset: colonnes-mspr_AURA.csv")
print("=" * 70)

# 1. Load election data (use 2017 as base, then add 2022)
df_2017 = pd.read_csv("data/processed/elections_2017_by_bloc_commune_AURA.csv", sep=';', 
                      dtype={'commune_code': 'str'})
df_2022 = pd.read_csv("data/processed/elections_2022_by_bloc_commune_AURA.csv", sep=';',
                      dtype={'commune_code': 'str'})

print(f"\n1️⃣ Elections loaded:")
print(f"   2017: {len(df_2017):,} communes")
print(f"   2022: {len(df_2022):,} communes")

# 2. Load secondary residence data
df_logement = pd.read_csv("data/processed/logement_secondaire_2022_complet.csv",
                          dtype={'code_commune': 'str'}, sep=';')
print(f"✅ Secondary residences: {len(df_logement):,} communes")

# 3. Start with 2017 as base (larger dataset)
master = df_2017[['commune_code', 'commune_name', 'exprimes_nb']].copy()
master.columns = ['Code_geo', 'commune_name', 'exprimes_nb_2017']

# Rename 2017 election columns
for col in ['resultat_election_2017', 'vote_G', 'vote_C', 'vote_D', 'vote_ED']:
    if col in df_2017.columns:
        master[col] = df_2017[col].values

print(f"\n   Base dataset: {len(master):,} communes from 2017")

# 4. Left-join 2022 data (will add NaN for communes not in 2022)
df_2022_renamed = df_2022.copy()
df_2022_renamed.columns = ['commune_code', 'commune_name_2022', 'exprimes_nb_2022', 'vote_C_2022', 
                           'vote_D_2022', 'vote_ED_2022', 'vote_G_2022', 'resultat_election_2022']

master = master.merge(df_2022_renamed[['commune_code', 'exprimes_nb_2022', 'resultat_election_2022', 
                                        'vote_G_2022', 'vote_C_2022', 'vote_D_2022', 'vote_ED_2022']],
                     left_on='Code_geo', right_on='commune_code', how='left')

matched_2022 = master['resultat_election_2022'].notna().sum()
print(f"   2022 added: {matched_2022:,} communes matched ({matched_2022/len(master)*100:.1f}%)")

# 5. Add secondary residence data
df_logement_renamed = df_logement.copy()
df_logement_renamed.columns = ['code_commune', 'commune_name_logement', 'total_logements', 
                               'residences_principales', 'residences_secondaires', 'taux_rsecocc_pct', 
                               'classe_rsecocc']

master = master.merge(df_logement_renamed[['code_commune', 'taux_rsecocc_pct']],
                     left_on='Code_geo', right_on='code_commune', how='left')

matched_logement = master['taux_rsecocc_pct'].notna().sum()
print(f"   Residences: {matched_logement:,} communes matched ({matched_logement/len(master)*100:.1f}%)")

# 6. Create final structure with all columns
final_columns = ['Code_geo', 'commune_name']

# Election 2017
final_columns.extend(['resultat_election_2017', 'exprimes_nb_2017',
                     'vote_G_2017', 'vote_C_2017', 'vote_D_2017', 'vote_ED_2017'])

# Election 2022
final_columns.extend(['resultat_election_2022', 'exprimes_nb_2022',
                     'vote_G_2022', 'vote_C_2022', 'vote_D_2022', 'vote_ED_2022'])

# Socioeconomic indicators
final_columns.extend(['revenus_median_today', 'popup_density_today', 'chomage_rate_today',
                     'parc_locatif_today', 'surface_agri_today', 'criminalite_today',
                     'pop_age_0_14_today', 'pop_age_15_64_today', 'pop_age_65plus_today',
                     'diploma_bac_today', 'diploma_sup_today'])

# Create empty dataframe with correct columns
result = pd.DataFrame(columns=final_columns)

# Copy available data
result['Code_geo'] = master['Code_geo']
result['commune_name'] = master['commune_name']

# Elections
if 'resultat_election_2017' in master.columns:
    result['resultat_election_2017'] = master['resultat_election_2017']
if 'vote_G' in master.columns:
    result['vote_G_2017'] = master['vote_G']
    result['vote_C_2017'] = master['vote_C']
    result['vote_D_2017'] = master['vote_D']
    result['vote_ED_2017'] = master['vote_ED']
if 'exprimes_nb_2017' in master.columns:
    result['exprimes_nb_2017'] = master['exprimes_nb_2017']

if 'resultat_election_2022' in master.columns:
    result['resultat_election_2022'] = master['resultat_election_2022']
if 'vote_G_2022' in master.columns:
    result['vote_G_2022'] = master['vote_G_2022']
    result['vote_C_2022'] = master['vote_C_2022']
    result['vote_D_2022'] = master['vote_D_2022']
    result['vote_ED_2022'] = master['vote_ED_2022']
if 'exprimes_nb_2022' in master.columns:
    result['exprimes_nb_2022'] = master['exprimes_nb_2022']

# Secondary residences (rename to parc_locatif_today)
if 'taux_rsecocc_pct' in master.columns:
    result['parc_locatif_today'] = master['taux_rsecocc_pct']

# 7. Save
result.to_csv("data/processed/colonnes-mspr_AURA.csv", sep=';', index=False, na_rep='')

print(f"\n✅ Master file created: {len(result):,} communes")
print("\n📊 Data Summary:")
print(f"  Code_geo: {result['Code_geo'].notna().sum():,}/{len(result)}")
print(f"  Elections 2017: {result['resultat_election_2017'].notna().sum():,}/{len(result)}")
print(f"  Elections 2022: {result['resultat_election_2022'].notna().sum():,}/{len(result)}")
print(f"  Secondary residences: {result['parc_locatif_today'].notna().sum():,}/{len(result)}")

print(f"\n📈 2017 Election Distribution:")
print(result['resultat_election_2017'].value_counts())
print(f"\n📈 2022 Election Distribution:")
print(result['resultat_election_2022'].value_counts())

print(f"\n✅ File saved: data/processed/colonnes-mspr_AURA.csv")
print(f"\nExample rows:")
print(result[['Code_geo', 'commune_name', 'resultat_election_2017', 'resultat_election_2022', 'parc_locatif_today']].head(10))
