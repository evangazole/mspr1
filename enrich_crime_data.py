import pandas as pd
import numpy as np

print("Processing crime data by department and year...")

# Load crime data (department-level)
df_crime = pd.read_csv('data/raw/delits_cambriolages.csv', sep=';')

# Replace comma with dot for float parsing
df_crime['nombre'] = df_crime['nombre'].astype(str).str.replace(',', '.').astype(float)

print(f"Crime data shape: {df_crime.shape}")
print(f"Available years: {sorted(df_crime['annee'].unique())}")
print(f"Crime types: {df_crime['indicateur'].nunique()}")

# Aggregate: sum all crimes by department and year
crime_by_dept_year = df_crime.groupby(['Code_departement', 'annee'])['nombre'].sum().reset_index()
crime_by_dept_year.columns = ['Code_departement', 'year', 'total_crimes']

print(f"\nAggregated crime data shape: {crime_by_dept_year.shape}")
print(f"Sample:\n{crime_by_dept_year.head(10)}")

# Load master AURA file
df_master = pd.read_csv('data/processed/colonnes-mspr_AURA.csv', sep=';')
print(f"\nMaster AURA shape: {df_master.shape}")

# Extract department code from Code_geo (first 2 digits)
df_master['dept_code'] = df_master['Code_geo'].astype(str).str[:2]

# Map crime data for each year
for year, col_name in [(2025, 'criminalite_today'), (2017, 'criminalite_old1'), (2022, 'criminalite_old2')]:
    crime_year = crime_by_dept_year[crime_by_dept_year['year'] == year][['Code_departement', 'total_crimes']].copy()
    crime_year = crime_year.rename(columns={'Code_departement': 'dept_code', 'total_crimes': col_name})
    
    # Merge with master on department code
    df_master = df_master.merge(crime_year, on='dept_code', how='left', suffixes=('_old', '_new'))
    
    # Handle potential duplicate column names
    if col_name + '_new' in df_master.columns:
        df_master[col_name] = df_master[col_name + '_new'].fillna(df_master[col_name + '_old'])
        df_master = df_master.drop([col_name + '_old', col_name + '_new'], axis=1)
    elif col_name + '_old' in df_master.columns:
        df_master = df_master.drop(col_name + '_old', axis=1)
    
    count = df_master[col_name].notna().sum()
    print(f"  {col_name} ({year}): {count:,} communes matched")

# Drop temporary department code column
df_master = df_master.drop('dept_code', axis=1)

# Save
df_master.to_csv('data/processed/colonnes-mspr_AURA.csv', sep=';', index=False, na_rep='')

print(f"\n✅ Updated: data/processed/colonnes-mspr_AURA.csv")
print(f"   Criminalite columns enriched with aggregated crime data")

# Statistics
for col in ['criminalite_today', 'criminalite_old1', 'criminalite_old2']:
    vals = df_master[col].dropna()
    if len(vals) > 0:
        print(f"\n{col} ({len(vals)} communes):")
        print(f"  Min: {vals.min():,.0f}")
        print(f"  Max: {vals.max():,.0f}")
        print(f"  Mean: {vals.mean():,.0f}")
        print(f"  Median: {vals.median():,.0f}")
