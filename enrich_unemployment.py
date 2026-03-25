#!/usr/bin/env python3
"""
Enrich colonnes-mspr_AURA.csv with unemployment rates
Data from Pole Emploi (2015-2024)
Adds:
- chomage_rate_today: 2024 data (most recent)
- chomage_rate_old1: 2017 data (historical baseline)
- chomage_rate_old2: 2022 data (recent past)
"""

import pandas as pd
import numpy as np

print("Processing unemployment data...")

# Load unemployment data (commune-level)
df_chom = pd.read_csv('data/raw/inscrit-pole-emploi-2015-2024.csv', sep=';', 
                        dtype={'Code Insee de la commune': str}, low_memory=False)

print(f"Unemployment data shape: {df_chom.shape}")
print(f"Unique communes: {df_chom['Code Insee de la commune'].nunique():,}")

# Select relevant columns
df_chom = df_chom[['Code Insee de la commune', 'Libellé de la commune', '2017', '2022', '2024']].copy()
df_chom = df_chom.rename(columns={'Code Insee de la commune': 'code_insee'})

# Clean and convert data
for year_col in ['2017', '2022', '2024']:
    # Replace commas with dots for decimal separator (French format)
    df_chom[year_col] = df_chom[year_col].astype(str).str.replace(',', '.')
    # Convert to float, NaN for invalid values
    df_chom[year_col] = pd.to_numeric(df_chom[year_col], errors='coerce')

print(f"\nData after cleaning:")
print(f"  2024 non-null: {df_chom['2024'].notna().sum():,}")
print(f"  2022 non-null: {df_chom['2022'].notna().sum():,}")
print(f"  2017 non-null: {df_chom['2017'].notna().sum():,}")

# Ensure 5-digit commune codes
df_chom['code_insee'] = df_chom['code_insee'].astype(str).str.zfill(5)

# Rename for merging
chom_merge = df_chom[['code_insee', '2024', '2022', '2017']].copy()
chom_merge.columns = ['code_insee_str', 'chomage_rate_today', 'chomage_rate_old2', 'chomage_rate_old1']

print(f"\nMerge data prepared: {len(chom_merge):,} communes")

# Load master AURA file
df_master = pd.read_csv('data/processed/colonnes-mspr_AURA.csv', sep=';')
print(f"Master AURA shape: {df_master.shape}")

# Convert Code_geo to 5-digit format
df_master['code_geo_str'] = df_master['Code_geo'].astype(str).str.zfill(5)

# Merge on commune code
df_merged = df_master.merge(
    chom_merge,
    left_on='code_geo_str',
    right_on='code_insee_str',
    how='left',
    suffixes=('_old', '_new')
)

# Replace old empty columns with new data
if 'chomage_rate_today_new' in df_merged.columns:
    df_merged['chomage_rate_today'] = df_merged['chomage_rate_today_new'].fillna(df_merged['chomage_rate_today_old'])
    df_merged = df_merged.drop(['chomage_rate_today_old', 'chomage_rate_today_new'], axis=1)
    
if 'chomage_rate_old1_new' in df_merged.columns:
    df_merged['chomage_rate_old1'] = df_merged['chomage_rate_old1_new'].fillna(df_merged['chomage_rate_old1_old'])
    df_merged = df_merged.drop(['chomage_rate_old1_old', 'chomage_rate_old1_new'], axis=1)
    
if 'chomage_rate_old2_new' in df_merged.columns:
    df_merged['chomage_rate_old2'] = df_merged['chomage_rate_old2_new'].fillna(df_merged['chomage_rate_old2_old'])
    df_merged = df_merged.drop(['chomage_rate_old2_old', 'chomage_rate_old2_new'], axis=1)

# Clean up temporary columns
if 'code_geo_str' in df_merged.columns:
    df_merged = df_merged.drop('code_geo_str', axis=1)
if 'code_insee_str' in df_merged.columns:
    df_merged = df_merged.drop('code_insee_str', axis=1)

matched_today = df_merged['chomage_rate_today'].notna().sum()
matched_old1 = df_merged['chomage_rate_old1'].notna().sum()
matched_old2 = df_merged['chomage_rate_old2'].notna().sum()

print(f"\nMatched:")
print(f"  chomage_rate_today (2024): {matched_today:,}/{len(df_merged):,} communes")
print(f"  chomage_rate_old1 (2017): {matched_old1:,}/{len(df_merged):,} communes")
print(f"  chomage_rate_old2 (2022): {matched_old2:,}/{len(df_merged):,} communes")

# Save
df_merged.to_csv('data/processed/colonnes-mspr_AURA.csv', sep=';', index=False, na_rep='')
print(f"\n✅ Updated: data/processed/colonnes-mspr_AURA.csv")

# Statistics
for col, label, year in [('chomage_rate_today', 'Unemployment rate 2024', 2024), 
                          ('chomage_rate_old1', 'Unemployment rate 2017', 2017), 
                          ('chomage_rate_old2', 'Unemployment rate 2022', 2022)]:
    vals = df_merged[col].dropna()
    if len(vals) > 0:
        print(f"\n{label} ({len(vals)} communes):")
        print(f"  Min: {vals.min():.2f}%")
        print(f"  Max: {vals.max():.2f}%")
        print(f"  Mean: {vals.mean():.2f}%")
        print(f"  Median: {vals.median():.2f}%")
