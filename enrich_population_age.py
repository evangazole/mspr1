#!/usr/bin/env python3
"""
Enrich colonnes-mspr_AURA.csv with population by age brackets
Aggregates IRIS-level data to commune level and adds:
- pop_age_0_14_today
- pop_age_15_64_today
- pop_age_65plus_today
"""

import pandas as pd
import numpy as np

print("Processing population by age data...")

# Load population data (IRIS-level)
df_pop = pd.read_csv('data/raw/base-ic-evol-struct-pop-2022.CSV', sep=';', low_memory=False)

print(f"Population IRIS data shape: {df_pop.shape}")
print(f"Unique communes: {df_pop['COM'].nunique():,}")

# Extract needed columns and handle missing values
cols_needed = ['COM', 'P22_POP', 'P22_POP0014', 'P22_POP65P']
df_pop = df_pop[cols_needed].copy()

# Replace NaN with 0 for aggregation
df_pop = df_pop.fillna(0)

# Aggregate by commune (COM)
pop_by_commune = df_pop.groupby('COM').agg({
    'P22_POP': 'sum',
    'P22_POP0014': 'sum',
    'P22_POP65P': 'sum'
}).reset_index()

pop_by_commune.columns = ['COM', 'total_pop', 'pop_0_14', 'pop_65plus']

# Calculate 15-64 age group (total - 0_14 - 65+)
pop_by_commune['pop_15_64'] = pop_by_commune['total_pop'] - pop_by_commune['pop_0_14'] - pop_by_commune['pop_65plus']

print(f"\nAggregated communes: {len(pop_by_commune):,}")
print(f"Total population: {pop_by_commune['total_pop'].sum():,.0f}")

# Convert COM to string with leading zeros (5 digits)
pop_by_commune['COM'] = pop_by_commune['COM'].astype(str).str.zfill(5)

# Load master AURA file
df_master = pd.read_csv('data/processed/colonnes-mspr_AURA.csv', sep=';')
print(f"\nMaster AURA shape: {df_master.shape}")

# Convert Code_geo to 5-digit format for merging
df_master['code_geo_str'] = df_master['Code_geo'].astype(str).str.zfill(5)

# Merge on commune code
df_merged = df_master.merge(
    pop_by_commune[['COM', 'pop_0_14', 'pop_15_64', 'pop_65plus']],
    left_on='code_geo_str',
    right_on='COM',
    how='left'
)

# Rename columns to match master file structure
df_merged['pop_age_0_14_today'] = df_merged['pop_0_14']
df_merged['pop_age_15_64_today'] = df_merged['pop_15_64']
df_merged['pop_age_65plus_today'] = df_merged['pop_65plus']

# Clean up temporary columns
df_merged = df_merged.drop(['pop_0_14', 'pop_15_64', 'pop_65plus', 'code_geo_str', 'COM'], axis=1)

matched = df_merged['pop_age_0_14_today'].notna().sum()
print(f"\nMatched: {matched:,}/{len(df_merged):,} communes")

# Save
df_merged.to_csv('data/processed/colonnes-mspr_AURA.csv', sep=';', index=False, na_rep='')
print(f"\n✅ Updated: data/processed/colonnes-mspr_AURA.csv")

# Statistics
for col, label in [('pop_age_0_14_today', '0-14 ans'), 
                    ('pop_age_15_64_today', '15-64 ans'), 
                    ('pop_age_65plus_today', '65+ ans')]:
    vals = df_merged[col].dropna()
    if len(vals) > 0:
        print(f"\n{label} ({len(vals)} communes):")
        print(f"  Total: {vals.sum():,.0f}")
        print(f"  Min: {vals.min():,.0f}")
        print(f"  Max: {vals.max():,.0f}")
        print(f"  Mean: {vals.mean():,.0f}")
        print(f"  Median: {vals.median():,.0f}")

print(f"\n{matched} communes enrichies avec la population par âge")
