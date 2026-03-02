import pandas as pd

df = pd.read_csv('data/processed/colonnes-mspr_AURA.csv', sep=';')

print(f'Total rows: {len(df)}')
print(f'Duplicates by Code_geo: {df.duplicated(subset=["Code_geo"]).sum()}')
print(f'\nRevenue column stats:')
print(f'  Non-null count: {df["revenus_median_today"].notna().sum()}')
if df["revenus_median_today"].notna().any():
    print(f'  Min: {df["revenus_median_today"].min():,.0f}€')
    print(f'  Max: {df["revenus_median_today"].max():,.0f}€')

print(f'\nFirst 5 rows with revenue:')
sample = df[df['revenus_median_today'].notna()][['Code_geo', 'commune_name', 'revenus_median_today']].head(10)
for idx, row in sample.iterrows():
    print(f"  {row['Code_geo']}: {row['commune_name']}: {row['revenus_median_today']:,.0f}€")
