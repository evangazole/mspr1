import pandas as pd

print("Cleaning master file from duplicates...")

# Load current master
df = pd.read_csv('data/processed/colonnes-mspr_AURA.csv', sep=';')
print(f"Current shape: {df.shape}")
print(f"Duplicates by Code_geo: {df.duplicated(subset=['Code_geo']).sum()}")

# Remove duplicates, keep first occurrence
df_clean = df.drop_duplicates(subset=['Code_geo'], keep='first')
print(f"After cleaning: {df_clean.shape}")

# Reset revenus_median_today to empty for re-enrichment
df_clean['revenus_median_today'] = None

# Save
df_clean.to_csv('data/processed/colonnes-mspr_AURA.csv', sep=';', index=False, na_rep='')
print(f"✅ Cleaned and saved master file")
print(f"   - Removed {len(df) - len(df_clean):,} duplicate rows")
print(f"   - Reset revenus_median_today column")
