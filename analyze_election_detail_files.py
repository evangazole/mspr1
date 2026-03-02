#!/usr/bin/env python3
"""Analyze detailed election files with candidate/party data"""

import pandas as pd
import os

files_to_check = [
    "data/raw/04-resultats-par-commune(1).csv",
    "data/raw/Presidentielle_2017_Resultats_Communes_Tour_1_c(1).xls"
]

for filepath in files_to_check:
    if not os.path.exists(filepath):
        print(f"❌ {filepath} not found")
        continue
    
    print("=" * 130)
    print(f"FICHIER: {filepath}")
    print("=" * 130)
    
    file_size = os.path.getsize(filepath) / (1024**2)
    print(f"Taille: {file_size:.2f} MB")
    print()
    
    try:
        # Try different separators
        if filepath.endswith('.csv'):
            # Test both separators
            for sep in [',', ';']:
                try:
                    df = pd.read_csv(filepath, sep=sep, nrows=100, low_memory=False)
                    print(f"✅ Chargé avec séparateur '{sep}'")
                    break
                except:
                    continue
        else:  # Excel
            df = pd.read_excel(filepath, nrows=100)
            print(f"✅ Chargé (fichier Excel)")
        
        print(f"\nDimensions: {df.shape[0]} lignes × {df.shape[1]} colonnes")
        print(f"\nColonnes:")
        for i, col in enumerate(df.columns, 1):
            print(f"  {i:2d}. {col}")
        
        print(f"\n📊 EXEMPLE (3 premières lignes):")
        print(df.head(3).to_string())
        
        # Check for candidate/party columns
        cols_lower = [str(c).lower() for c in df.columns]
        if any(['candidat' in c or 'parti' in c or 'voix' in c for c in cols_lower]):
            print("\n✅ CONTIENT LES DONNÉES PAR CANDIDAT/PARTI!")
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
    
    print("\n\n")
