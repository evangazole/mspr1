import subprocess
import pandas as pd

# Get original file from git
result = subprocess.run(
    [r'C:\Program Files\Git\bin\git.exe', 'show', 'HEAD:data/processed/colonnes-mspr_AURA.csv'],
    capture_output=True, 
    text=True, 
    cwd='c:\\Users\\Evan\\Documents\\sujet mspr1\\project'
)

if result.returncode == 0:
    # Write to a backup, then restore
    with open('data/processed/colonnes-mspr_AURA_original.csv', 'w', encoding='utf-8') as f:
        f.write(result.stdout)
    
    # Read both and verify
    df_orig = pd.read_csv('data/processed/colonnes-mspr_AURA_original.csv', sep=';')
    print(f"Original shape: {df_orig.shape}")
    print(f"Original duplicates: {df_orig.duplicated(subset=['Code_geo']).sum()}")
    
    # Make it active
    import shutil
    shutil.copy('data/processed/colonnes-mspr_AURA_original.csv', 'data/processed/colonnes-mspr_AURA.csv')
    print("Restored original master file")
else:
    print(f"Git error: {result.stderr}")
    print("Will proceed with fixed script instead")
