#!/usr/bin/env python3
"""
Enrich colonnes-mspr_AURA.csv with agricultural surface area
Data available for 2020 and 2010 from INSEE
Adds:
- surface_agri_today: 2020 data (most recent)
- surface_agri_old1: 2010 data (historical baseline)
- surface_agri_old2: 2010 data (only historical data available before 2020)
"""

import pandas as pd
import numpy as np

print("Processing agricultural surface data...")

# Load agricultural data (commune-level, already aggregated)
df_agri = pd.read_csv('data/raw/surface-agricole-utile-totale-commune.csv', sep=',')

print(f"Agriculture data shape: {df_agri.shape}")

# Parse date to extract year
df_agri['year'] = pd.to_datetime(df_agri['date_mesure']).dt.year

# Clean geocode_commune (remove leading zeros shouldn't be there, but verify)
df_agri['geocode_commune'] = df_agri['geocode_commune'].astype(str).str.zfill(5)

print(f"Available years: {sorted(df_agri['year'].unique())}")
print(f"Unique communes: {df_agri['geocode_commune'].nunique():,}")

# Pivot by year
agri_pivot = df_agri.pivot_table(
    index='geocode_commune',
    columns='year',
    values='valeur',
    aggfunc='first'
).reset_index()

print(f"\nPivoted agriculture data shape: {agri_pivot.shape}")
print(f"Columns: {agri_pivot.columns.tolist()}")

# Prepare data for merging
agri_merge = agri_pivot.copy()
agri_merge.columns.name = None

# Create columns for each year if they don't exist
if 2020 not in agri_merge.columns:
    agri_merge[2020] = np.nan
if 2010 not in agri_merge.columns:
    agri_merge[2010] = np.nan

# Rename columns to match master structure
agri_merge['surface_agri_today'] = agri_merge[2020]  # 2020 as today
agri_merge['surface_agri_old1'] = agri_merge[2010]   # 2010 as old1
agri_merge['surface_agri_old2'] = agri_merge[2010]   # 2010 as old2

# Keep only needed columns
agri_merge = agri_merge[['geocode_commune', 'surface_agri_today', 'surface_agri_old1', 'surface_agri_old2']].copy()
agri_merge['geocode_commune'] = agri_merge['geocode_commune'].astype(str).str.zfill(5)
agri_merge = agri_merge.rename(columns={'geocode_commune': 'code_geo_str'})

print(f"\nMerge data prepared: {len(agri_merge):,} communes")

# Load master AURA file
df_master = pd.read_csv('data/processed/colonnes-mspr_AURA.csv', sep=';')
print(f"Master AURA shape: {df_master.shape}")

# Convert Code_geo to 5-digit format
df_master['code_geo_str'] = df_master['Code_geo'].astype(str).str.zfill(5)

# Merge on commune code
df_merged = df_master.merge(
    agri_merge,
    on='code_geo_str',
    how='left',
    suffixes=('_old', '_new')
)

print(f"After merge, shape: {df_merged.shape}")

# Replace old empty columns with new data
if 'surface_agri_today_new' in df_merged.columns:
    df_merged['surface_agri_today'] = df_merged['surface_agri_today_new'].fillna(df_merged['surface_agri_today_old'])
    df_merged = df_merged.drop(['surface_agri_today_old', 'surface_agri_today_new'], axis=1)
    
if 'surface_agri_old1_new' in df_merged.columns:
    df_merged['surface_agri_old1'] = df_merged['surface_agri_old1_new'].fillna(df_merged['surface_agri_old1_old'])
    df_merged = df_merged.drop(['surface_agri_old1_old', 'surface_agri_old1_new'], axis=1)
    
if 'surface_agri_old2_new' in df_merged.columns:
    df_merged['surface_agri_old2'] = df_merged['surface_agri_old2_new'].fillna(df_merged['surface_agri_old2_old'])
    df_merged = df_merged.drop(['surface_agri_old2_old', 'surface_agri_old2_new'], axis=1)

# Clean up temporary column
if 'code_geo_str' in df_merged.columns:
    df_merged = df_merged.drop('code_geo_str', axis=1)

matched_today = df_merged['surface_agri_today'].notna().sum()
matched_old1 = df_merged['surface_agri_old1'].notna().sum()
matched_old2 = df_merged['surface_agri_old2'].notna().sum()

print(f"\nMatched:")
print(f"  surface_agri_today (2020): {matched_today:,}/{len(df_merged):,} communes")
print(f"  surface_agri_old1 (2010): {matched_old1:,}/{len(df_merged):,} communes")
print(f"  surface_agri_old2 (2010): {matched_old2:,}/{len(df_merged):,} communes")

# Save
df_merged.to_csv('data/processed/colonnes-mspr_AURA.csv', sep=';', index=False, na_rep='')
print(f"\n✅ Updated: data/processed/colonnes-mspr_AURA.csv")

# Statistics
for col, label, year in [('surface_agri_today', 'Agricultural surface 2020', 2020), 
                          ('surface_agri_old1', 'Agricultural surface 2010', 2010), 
                          ('surface_agri_old2', 'Agricultural surface 2010', 2010)]:
    vals = df_merged[col].dropna()
    if len(vals) > 0:
        print(f"\n{label} ({len(vals)} communes):")
        print(f"  Total: {vals.sum():,.0f} hectares")
        print(f"  Min: {vals.min():,.1f} ha")
        print(f"  Max: {vals.max():,.1f} ha")
        print(f"  Mean: {vals.mean():,.1f} ha")
        print(f"  Median: {vals.median():,.1f} ha")
