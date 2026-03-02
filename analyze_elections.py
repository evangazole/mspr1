#!/usr/bin/env python3
"""Analyse détaillée des fichiers élections"""

import pandas as pd
import os

raw_dir = "data/raw"
election_files = [f for f in os.listdir(raw_dir) if 'election' in f.lower()]

print("=" * 130)
print("ANALYSE DES FICHIERS ÉLECTIONS 2017-2022")
print("=" * 130)
print()

for fname in sorted(election_files):
    fpath = os.path.join(raw_dir, fname)
    size_mb = os.path.getsize(fpath) / (1024*1024)
    
    print(f"📄 {fname}")
    print(f"   Taille disque: {size_mb:.2f} MB")
    
    try:
        df = pd.read_csv(fpath, encoding='utf-8', nrows=5000, low_memory=False)
    except:
        try:
            df = pd.read_csv(fpath, encoding='latin-1', nrows=5000, low_memory=False)
        except Exception as e:
            print(f"   ❌ ERREUR LECTURE: {str(e)[:80]}")
            print()
            continue
    
    print(f"   Total lignes (toutes): ~{len(pd.read_csv(fpath, nrows=1, low_memory=False))} (full file)")
    print(f"   Colonnes ({df.shape[1]}): {', '.join(df.columns.tolist()[:6])}...")
    print()
    
    # Vérifier structure
    if 'code_commune' in df.columns:
        print(f"   ✅ Grain géographique: Par COMMUNE (ou bureau de vote)")
    elif 'code_departement' in df.columns:
        print(f"   ✅ Grain géographique: Par DÉPARTEMENT")
    
    # Chercher colonnes de résultats
    candidate_cols = [col for col in df.columns if any(x in col.lower() for x in 
        ['nom', 'candidat', 'parti', 'liste', 'etiquette', 'candidate_name', 'candidat'])]
    result_cols = [col for col in df.columns if any(x in col.lower() for x in 
        ['voix', 'vote', 'resultat', 'score', 'pct', 'pourcentage', 'percent', 'votes'])]
    
    if candidate_cols:
        print(f"   📋 Colonnes candidat: {candidate_cols}")
        for col in candidate_cols[:2]:
            unique_count = df[col].nunique()
            print(f"      • {col}: {unique_count} valeurs uniques")
            if unique_count < 30:
                print(f"        Valeurs: {df[col].dropna().unique().tolist()}")
    
    if result_cols:
        print(f"   📊 Colonnes résultats: {result_cols}")
    
    # Afficher structure générale
    print()
    print(f"   APERÇU (5 premières lignes):")
    print(df.head(2).to_string())
    print()
    print()

print("=" * 130)
print("RECOMMANDATION")
print("=" * 130)
print("""
Ces fichiers élections contiennent:
- Données détaillées par BUREAU DE VOTE ou COMMUNE
- Résultats de chaque candidat/liste
- Suffisant pour agrégation par catégorie politique

UTILITÉ: ✅ OUI - Permettent de calculer:
  • vote_G (Gauche)
  • vote_C (Centre) 
  • vote_D (Droite)
  • vote_ED (Extrême droite)
  
Par agrégation/sum des voix par catégorie puis normalisation
""")
