import pandas as pd
import subprocess

# Check git history
try:
    result = subprocess.run(['"C:\\Program Files\\Git\\bin\\git.exe"', 'show', 'HEAD:data/processed/colonnes-mspr_AURA.csv'], 
                          capture_output=True, text=True, cwd='.')
    if result.returncode == 0:
        lines = len(result.stdout.strip().split('\n'))
        print(f"Original file size: {lines} lines")
        
        # Count duplicates in original
        from io import StringIO
        df_orig = pd.read_csv(StringIO(result.stdout), sep=';')
        dups_orig = df_orig.duplicated(subset=['Code_geo']).sum()
        print(f"Duplicates originally: {dups_orig}")
        print(f"Original shape: {df_orig.shape}")
except Exception as e:
    print(f"Error checking git: {e}")

# Check current file
df_current = pd.read_csv('data/processed/colonnes-mspr_AURA.csv', sep=';')
print(f"\nCurrent file size: {len(df_current)} lines")
dups_current = df_current.duplicated(subset=['Code_geo']).sum()
print(f"Duplicates now: {dups_current}")
print(f"Current shape: {df_current.shape}")
