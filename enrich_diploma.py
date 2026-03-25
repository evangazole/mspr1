#!/usr/bin/env python3
"""
Enrich colonnes-mspr_AURA.csv with education/diploma levels
Aggregates IRIS-level data to commune level and adds:
- diploma_bac_today: proportion of population with Bac or higher diploma
- diploma_sup_today: proportion of population with higher education diploma
"""

import pandas as pd
import numpy as np

print("Processing diploma/education data...")

# Load diploma data (IRIS-level)
df_diploma = pd.read_csv('data/raw/base-ic-diplomes-formation-2022.CSV', sep=';', low_memory=False)

print(f"Diploma IRIS data shape: {df_diploma.shape}")
print(f"Unique communes: {df_diploma['COM'].nunique():,}")

# Extract needed columns for total population 15+ and diploma counts
cols_needed = ['COM', 'P22_NSCOL15P', 'P22_NSCOL15P_BAC', 
               'P22_NSCOL15P_SUP2', 'P22_NSCOL15P_SUP34', 'P22_NSCOL15P_SUP5']
df_diploma = df_diploma[cols_needed].copy()

# Replace NaN with 0 for aggregation
df_diploma = df_diploma.fillna(0)

# Aggregate by commune (COM)
diploma_by_commune = df_diploma.groupby('COM').agg({
    'P22_NSCOL15P': 'sum',  # Total non-schooled 15+
    'P22_NSCOL15P_BAC': 'sum',  # With Bac
    'P22_NSCOL15P_SUP2': 'sum',  # Higher ed 2 years
    'P22_NSCOL15P_SUP34': 'sum',  # Higher ed 3-4 years
    'P22_NSCOL15P_SUP5': 'sum'   # Higher ed 5+ years
}).reset_index()

# Calculate totals
diploma_by_commune['bac_or_higher'] = (
    diploma_by_commune['P22_NSCOL15P_BAC'] + 
    diploma_by_commune['P22_NSCOL15P_SUP2'] + 
    diploma_by_commune['P22_NSCOL15P_SUP34'] + 
    diploma_by_commune['P22_NSCOL15P_SUP5']
)

diploma_by_commune['higher_ed'] = (
    diploma_by_commune['P22_NSCOL15P_SUP2'] + 
    diploma_by_commune['P22_NSCOL15P_SUP34'] + 
    diploma_by_commune['P22_NSCOL15P_SUP5']
)

# Calculate proportions (avoid division by zero)
diploma_by_commune['diploma_bac'] = np.where(
    diploma_by_commune['P22_NSCOL15P'] > 0,
    diploma_by_commune['bac_or_higher'] / diploma_by_commune['P22_NSCOL15P'] * 100,
    np.nan
)

diploma_by_commune['diploma_sup'] = np.where(
    diploma_by_commune['P22_NSCOL15P'] > 0,
    diploma_by_commune['higher_ed'] / diploma_by_commune['P22_NSCOL15P'] * 100,
    np.nan
)

print(f"\nAggregated communes: {len(diploma_by_commune):,}")
print(f"Mean Bac+ rate: {diploma_by_commune['diploma_bac'].mean():.1f}%")
print(f"Mean Higher Ed rate: {diploma_by_commune['diploma_sup'].mean():.1f}%")

# Load master AURA file
df_master = pd.read_csv('data/processed/colonnes-mspr_AURA.csv', sep=';')
print(f"\nMaster AURA shape: {df_master.shape}")

# Convert COM to string format for merging
diploma_by_commune['COM_str'] = diploma_by_commune['COM'].astype(str).str.zfill(5)
df_master['code_geo_str'] = df_master['Code_geo'].astype(str).str.zfill(5)

# Merge on commune code
df_merged = df_master.merge(
    diploma_by_commune[['COM_str', 'diploma_bac', 'diploma_sup']],
    left_on='code_geo_str',
    right_on='COM_str',
    how='left'
)

# Rename columns
df_merged['diploma_bac_today'] = df_merged['diploma_bac']
df_merged['diploma_sup_today'] = df_merged['diploma_sup']

# Clean up temporary columns
df_merged = df_merged.drop(['diploma_bac', 'diploma_sup', 'code_geo_str', 'COM_str'], axis=1)

matched_bac = df_merged['diploma_bac_today'].notna().sum()
matched_sup = df_merged['diploma_sup_today'].notna().sum()

print(f"\nMatched:")
print(f"  diploma_bac_today: {matched_bac:,}/{len(df_merged):,} communes")
print(f"  diploma_sup_today: {matched_sup:,}/{len(df_merged):,} communes")

# Save
df_merged.to_csv('data/processed/colonnes-mspr_AURA.csv', sep=';', index=False, na_rep='')
print(f"\n✅ Updated: data/processed/colonnes-mspr_AURA.csv")

# Statistics
for col, label in [('diploma_bac_today', 'Bac or higher (%)'), 
                    ('diploma_sup_today', 'Higher education (%)')]:
    vals = df_merged[col].dropna()
    if len(vals) > 0:
        print(f"\n{label} ({len(vals)} communes):")
        print(f"  Min: {vals.min():.1f}%")
        print(f"  Max: {vals.max():.1f}%")
        print(f"  Mean: {vals.mean():.1f}%")
        print(f"  Median: {vals.median():.1f}%")
