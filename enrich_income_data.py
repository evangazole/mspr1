#!/usr/bin/env python3
"""
Enrich colonnes-mspr_AURA.csv with median income from revenu file
Rules:
1. Use median if available
2. Else calculate from quartiles if available
3. Else leave empty
"""

import pandas as pd

print("Enriching AURA master file with income data...")

# Load income data
df_income = pd.read_csv(
    "data/raw/revenu-des-francais-a-la-commune-1765372688826.csv",
    sep=';',
    usecols=['Libellé géographique', '[DISP] Médiane (€)', '[DISP] 1ᵉʳ quartile (€)', '[DISP] 3ᵉ quartile (€)']
)

print(f"Income data: {len(df_income):,} communes")
print(f"  Median available: {df_income['[DISP] Médiane (€)'].notna().sum():,}")

# Rename and normalize
df_income = df_income.rename(columns={
    'Libellé géographique': 'commune_name',
    '[DISP] Médiane (€)': 'median',
    '[DISP] 1ᵉʳ quartile (€)': 'q1',
    '[DISP] 3ᵉ quartile (€)': 'q3'
})

df_income['commune_name_norm'] = df_income['commune_name'].str.upper().str.strip()

# Prepare median column
df_income['revenus_median_today'] = df_income['median']

# Estimate missing medians from quartiles
mask_estimate = df_income['revenus_median_today'].isna() & df_income['q1'].notna() & df_income['q3'].notna()
df_income.loc[mask_estimate, 'revenus_median_today'] = (df_income.loc[mask_estimate, 'q1'] + df_income.loc[mask_estimate, 'q3']) / 2
print(f"  Estimated from Q1/Q3: {mask_estimate.sum():,}")
print(f"  Total with data: {df_income['revenus_median_today'].notna().sum():,}")

# Deduplicate income data - keep first occurrence by commune name
df_income_dedup = df_income.drop_duplicates(subset=['commune_name_norm'], keep='first')
print(f"  After deduplication: {len(df_income_dedup):,} communes")

# Load master
df_master = pd.read_csv("data/processed/colonnes-mspr_AURA.csv", sep=';')
df_master['commune_name_norm'] = df_master['commune_name'].str.upper().str.strip()

print(f"\nMaster AURA: {len(df_master):,} communes")

# Prepare for merge - only use necessary columns
df_income_merge = df_income_dedup[['commune_name_norm', 'revenus_median_today']].copy()

# Use merge with suffixes to handle existing column
df_merged = df_master.merge(
    df_income_merge,
    on='commune_name_norm',
    how='left',
    suffixes=('_old', '_new')
)

# Replace old column with new data, keep non-matched rows' old data
if 'revenus_median_today_new' in df_merged.columns:
    df_merged['revenus_median_today'] = df_merged['revenus_median_today_new'].fillna(df_merged['revenus_median_today_old'])
    df_merged = df_merged.drop(['revenus_median_today_old', 'revenus_median_today_new'], axis=1)

matched = df_merged['revenus_median_today'].notna().sum()
print(f"Matched: {matched:,}/{len(df_merged):,} communes")

# Save
df_merged = df_merged.drop('commune_name_norm', axis=1)
df_merged.to_csv("data/processed/colonnes-mspr_AURA.csv", sep=';', index=False, na_rep='')

print(f"\n✅ Updated: data/processed/colonnes-mspr_AURA.csv")
print(f"\nRevenue stats:")
vals = df_merged['revenus_median_today'].dropna()
print(f"  Count: {len(vals):,}")
print(f"  Min: {vals.min():,.0f}€")
print(f"  Max: {vals.max():,.0f}€") 
print(f"  Mean: {vals.mean():,.0f}€")
print(f"  Median: {vals.median():,.0f}€")

print(f"\nSample:")
sample = df_merged[df_merged['revenus_median_today'].notna()][['Code_geo', 'commune_name', 'revenus_median_today']].head(5)
for idx, row in sample.iterrows():
    print(f"  {row['Code_geo']}: {row['commune_name']}: {row['revenus_median_today']:,.0f}€")
