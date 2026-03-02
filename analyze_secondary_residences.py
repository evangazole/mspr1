#!/usr/bin/env python3
"""
Extract and analyze P22_RSECOCC (Secondary residences) from base-cc-logement-2022
"""

import pandas as pd
import numpy as np

# Load data with proper separator
print("Chargement des données de logement...")
df = pd.read_csv(
    "data/raw/base-cc-logement-2022.CSV",
    sep=";",
    usecols=['CODGEO', 'P22_LOG', 'P22_RP', 'P22_RSECOCC'],
    dtype={'CODGEO': 'str', 'P22_LOG': 'float64', 'P22_RP': 'float64', 'P22_RSECOCC': 'float64'}
)

print(f"✅ Chargé: {len(df):,} communes\n")

print("=" * 100)
print("COLONNE P22_RSECOCC - DÉFINITION")
print("=" * 100)
print("""
P22_RSECOCC = Nombre de résidences SECONDAIRES (2022 Recensement)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Définition INSEE:
  - Résidence secondaire = logement utilisé pour vacances, week-end, où la 
    personne n'habite pas à titre principal
  - Inclut: résidences de vacances, maisons de campagne, studios de ski, etc.
  - Exclut: logements vacants, logements sociaux, résidences principales

Indicateur économique & social:
  ✓ Taux de secondarité = (P22_RSECOCC / P22_LOG) × 100
  ✓ Plus élevé en zones touristiques (littoral, montagne)
  ✓ Réfère à: richesse, destinations touristiques, gentrification rurales
  ✓ Corollaire: proportion des habitants permanents ↓, services saisonniers ↑
""")

print("\n" + "=" * 100)
print("DONNÉES DISPONIBLES")
print("=" * 100)

# Check data quality
print(f"\nColonnes: {df.columns.tolist()}")
print(f"\nStatut des données:")
print(f"  P22_RSECOCC: {df['P22_RSECOCC'].notna().sum():,} communes avec données")
print(f"  P22_LOG: {df['P22_LOG'].notna().sum():,} communes avec données")

# Calculate secondary residence rate
df['taux_rsecocc'] = (df['P22_RSECOCC'] / df['P22_LOG'] * 100).replace(
    [np.inf, -np.inf], np.nan
)

print(f"\n" + "=" * 100)
print("STATISTIQUES - TAUX DE RÉSIDENCES SECONDAIRES (%)")
print("=" * 100)

print(f"\nGlobales (France entière):")
print(f"  Moyenne:    {df['taux_rsecocc'].mean():.2f}%")
print(f"  Médiane:    {df['taux_rsecocc'].median():.2f}%")
print(f"  Min:        {df['taux_rsecocc'].min():.2f}%")
print(f"  Max:        {df['taux_rsecocc'].max():.2f}%")
print(f"  Écart-type: {df['taux_rsecocc'].std():.2f}%")

# Quartiles
q1 = df['taux_rsecocc'].quantile(0.25)
q3 = df['taux_rsecocc'].quantile(0.75)
print(f"\nQuartiles:")
print(f"  Q1 (25%):   {q1:.2f}%")
print(f"  Q3 (75%):   {q3:.2f}%")
print(f"  IQR:        {q3 - q1:.2f}%")

print(f"\n" + "=" * 100)
print("CLASSIFICATION DU TAUX")
print("=" * 100)

# Create categories based on distribution
df['classe_rsecocc'] = pd.cut(
    df['taux_rsecocc'],
    bins=[0, 5, 10, 20, 40, 100],
    labels=['Très faible (0-5%)', 'Faible (5-10%)', 'Moyen (10-20%)', 
            'Élevé (20-40%)', 'Très élevé (40%+)'],
    include_lowest=True
)

print(f"\nDistribution par classe:")
for classe, count in df['classe_rsecocc'].value_counts().sort_index().items():
    pct = count / len(df) * 100
    print(f"  {classe:25s}: {count:5,} communes ({pct:5.1f}%)")

print(f"\n" + "=" * 100)
print("CAS EXTRÊMES - COMMUNES avec taux TRÈS ÉLEVÉ (>40%)")
print("=" * 100)

top = df.nlargest(10, 'taux_rsecocc')[['CODGEO', 'P22_RSECOCC', 'P22_LOG', 'taux_rsecocc']]
print(f"\nTop 10 communes - Taux de résidences secondaires les plus élevés:")
for idx, row in top.iterrows():
    print(f"  Code {row['CODGEO']:6s}: {row['taux_rsecocc']:6.1f}% " +
          f"({int(row['P22_RSECOCC']):,} / {int(row['P22_LOG']):,} logements)")

print(f"\n" + "=" * 100)
print("CRÉATION DES DONNÉES DE SORTIE")
print("=" * 100)

# Merge with commune names from other files - need IRIS to commune mapping
# For now, save this as intermediate data
output = df[['CODGEO', 'P22_LOG', 'P22_RP', 'P22_RSECOCC', 'taux_rsecocc', 'classe_rsecocc']].copy()
output.columns = ['code_commune', 'total_logements', 'residences_principales', 
                  'residences_secondaires', 'taux_rsecocc_pct', 'classe_rsecocc']

output_file = "data/processed/logement_secondaire_2022.csv"
output.to_csv(output_file, sep=';', index=False)
print(f"\n✅ Sauvegardé: {output_file}")

# Show sample
print(f"\n📋 EXEMPLE (10 premières communes):")
print(output.head(10).to_string(index=False))

print(f"\n\n⚠️ NOTE: Pour lier à des noms de communes, il faudra joindre avec:")
print(f"   - base-ic-evol-struct-pop-2022.CSV (a CODGEO)")
print(f"   - ou créer un fichier de mapping CODGEO → commune_name")
