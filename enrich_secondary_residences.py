#!/usr/bin/env python3
"""
Enrichir logement_secondaire_2022.csv avec noms de communes
"""

import pandas as pd

print("Chargement des données...")

# Load secondary residence data
df_rsecocc = pd.read_csv("data/processed/logement_secondaire_2022.csv", sep=';')

# Load election data to get commune names (elections have communal-level detail with names)
df_elections = pd.read_csv(
    "data/raw/elections_2022_2017.csv",
    sep=';',
    usecols=['code_commune', 'libelle_commune'],
    dtype={'code_commune': 'str'}
).drop_duplicates('code_commune')

print(f"  - Résidences secondaires: {len(df_rsecocc):,} communes")
print(f"  - Noms de communes: {len(df_elections):,} communes")

# Convert code_commune to string for merge
df_rsecocc['code_commune'] = df_rsecocc['code_commune'].astype(str)

# Merge
result = df_rsecocc.merge(
    df_elections.rename(columns={'libelle_commune': 'commune_name'}),
    on='code_commune',
    how='left'
)

print(f"\n✅ Jointure: {result['commune_name'].notna().sum():,} communes avec noms")

# Reorder columns
result = result[['code_commune', 'commune_name', 'total_logements', 'residences_principales',
                 'residences_secondaires', 'taux_rsecocc_pct', 'classe_rsecocc']]

# Save
output_file = "data/processed/logement_secondaire_2022_complet.csv"
result.to_csv(output_file, sep=';', index=False)

print(f"\n✅ Sauvegardé: {output_file}")

print(f"\n" + "="*120)
print("EXEMPLE - Top 20 communes avec PLUS de résidences secondaires")
print("="*120 + "\n")

top20 = result.nlargest(20, 'taux_rsecocc_pct')[
    ['code_commune', 'commune_name', 'residences_secondaires', 'total_logements', 'taux_rsecocc_pct']
]

for idx, row in top20.iterrows():
    print(f"{row['commune_name']:45s} | Taux: {row['taux_rsecocc_pct']:6.1f}% | "
          f"{int(row['residences_secondaires']):,} / {int(row['total_logements']):,}")

print(f"\n" + "="*120)
print("EXEMPLE - Communes AURA (Ain, Allier, Ardèche, etc.)")
print("="*120 + "\n")

aura_depts = ['01', '03', '07', '15', '26', '38', '42', '43', '63', '69', '73', '74']
df_aura = result[result['code_commune'].str[:2].isin(aura_depts)].nlargest(15, 'taux_rsecocc_pct')

for idx, row in df_aura.iterrows():
    print(f"{row['commune_name']:45s} | Taux: {row['taux_rsecocc_pct']:6.1f}% | "
          f"{int(row['residences_secondaires']):,} / {int(row['total_logements']):,}")

print(f"\n\n📊 Statistiques AURA:")
print(f"  Communes: {len(result[result['code_commune'].str[:2].isin(aura_depts)])}")
print(f"  Taux moyen: {result[result['code_commune'].str[:2].isin(aura_depts)]['taux_rsecocc_pct'].mean():.2f}%")
print(f"  Somme résidences secondaires: {result[result['code_commune'].str[:2].isin(aura_depts)]['residences_secondaires'].sum():,.0f}")
