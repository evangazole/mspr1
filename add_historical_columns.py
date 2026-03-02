import pandas as pd

print("Adding historical columns (old1, old2) for 'today' indicators...")

# Load master file
df = pd.read_csv('data/processed/colonnes-mspr_AURA.csv', sep=';')
print(f"Original shape: {df.shape}")
print(f"Original columns: {df.columns.tolist()}")

# Find all columns containing "today"
today_columns = [col for col in df.columns if 'today' in col]
print(f"\nColumns with 'today': {today_columns}")

# Create old1 and old2 versions of each today column
for col in today_columns:
    col_old1 = col.replace('today', 'old1')
    col_old2 = col.replace('today', 'old2')
    
    # Add empty columns
    df[col_old1] = None
    df[col_old2] = None
    print(f"  Added: {col_old1}, {col_old2}")

print(f"\nNew shape: {df.shape}")
print(f"New columns: {df.columns.tolist()}")

# Save
df.to_csv('data/processed/colonnes-mspr_AURA.csv', sep=';', index=False, na_rep='')
print(f"\n✅ Updated: data/processed/colonnes-mspr_AURA.csv")
print(f"   Total columns: {len(df.columns)} (added {len(today_columns) * 2})")
