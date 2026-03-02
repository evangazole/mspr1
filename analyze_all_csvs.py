#!/usr/bin/env python3
"""Analyse complète de tous les fichiers CSV/Excel dans data/raw"""

import pandas as pd
import os
from pathlib import Path

raw_dir = Path("data/raw")
files = sorted([f for f in os.listdir(raw_dir) if f.endswith(('.csv', '.xlsx', '.xls', '.CSV'))])

AURA = {"01", "03", "07", "15", "26", "38", "42", "43", "63", "69", "73", "74"}

print("=" * 130)
print("ANALYSE COMPLÈTE - TOUS LES FICHIERS data/raw")
print("=" * 130)
print()

keep = []
delete = []
new_indicators = []

for fname in files:
    fpath = raw_dir / fname
    size_mb = fpath.stat().st_size / (1024 * 1024)
    
    print(f"📄 {fname:<50} {size_mb:>7.2f} MB", end="")
    
    try:
        # Charger CSV or Excel
        if fname.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(fpath, nrows=500)
            file_type = f"Excel: {df.shape[0]:>6,} rows × {df.shape[1]:>3} cols"
        else:
            try:
                df = pd.read_csv(fpath, encoding='utf-8', nrows=500, low_memory=False)
            except:
                df = pd.read_csv(fpath, encoding='latin-1', nrows=500, low_memory=False)
            file_type = f"CSV:   {df.shape[0]:>6,} rows × {df.shape[1]:>3} cols"
        
        print(f" | {file_type:<40}", end=" | ")
        
        # Identifier le type
        cols_lower = ' '.join([c.lower() for c in df.columns])
        
        verdict = ""
        category = ""
        action = ""
        
        # Checker contenu
        if any(x in cols_lower for x in ['diplom', 'bac', 'cap', 'scol', 'nscol']):
            verdict = "DIPLÔMES"
            category = "✅ ESSENTIEL"
            action = "GARDER"
            keep.append((fname, size_mb, "Niveau diplôme"))
            
        elif any(x in cols_lower for x in ['pop', 'age', 'pmen', 'iris', 'poph']):
            verdict = "POPULATION"
            category = "✅ ESSENTIEL"
            action = "GARDER"
            keep.append((fname, size_mb, "Âge, population"))
            
        elif any(x in cols_lower for x in ['chomage', 'emploi', 'demande', 'actif', 'dares']):
            verdict = "CHÔMAGE 🆕"
            category = "✅ ESSENTIEL"
            action = "GARDER"
            keep.append((fname, size_mb, "Taux chômage"))
            new_indicators.append("Chômage")
            
        elif any(x in cols_lower for x in ['revenu', 'salaire', 'impot', 'fiscal', 'revenu']):
            verdict = "REVENU 🆕"
            category = "✅ ESSENTIEL"
            action = "GARDER"
            keep.append((fname, size_mb, "Revenu médian"))
            new_indicators.append("Revenu médian")
            
        elif any(x in cols_lower for x in ['agricol', 'surface', 'sauterra', 'agricole']):
            verdict = "AGRICULTURE 🆕"
            category = "✅ ESSENTIEL"
            action = "GARDER"
            keep.append((fname, size_mb, "Terres agricoles"))
            new_indicators.append("Terres agricoles")
            
        elif any(x in cols_lower for x in ['logement', 'residen', 'habitation', 'secondaire', 'principal']):
            verdict = "LOGEMENTS"
            category = "🔍 À VÉRIFIER"
            action = "VÉRIFIER"
            keep.append((fname, size_mb, "Logements (détail TBD)"))
            
        elif 'rpls' in fname.lower() or 'social' in cols_lower:
            verdict = "LOG.SOCIAUX"
            category = "✅ ESSENTIEL"
            action = "GARDER"
            keep.append((fname, size_mb, "Logements sociaux"))
            
        elif 'delits' in fname.lower() or 'cambriol' in fname.lower():
            verdict = "CRIMINALITÉ"
            category = "✅ ESSENTIEL"
            action = "GARDER"
            keep.append((fname, size_mb, "Cambriolages"))
            
        elif 'election' in fname.lower() or 'presiden' in fname.lower():
            verdict = "ÉLECTIONS"
            category = "✅ ESSENTIEL"
            action = "GARDER"
            if '2017' not in fname.lower():
                keep.append((fname, size_mb, "Votes (2022 et/ou 2017)"))
            else:
                keep.append((fname, size_mb, "Votes 2017 (potentiel dupe)"))
            
        elif 'meta' in fname.lower() or 'prec' in fname.lower() or 'documentation' in fname.lower():
            verdict = "MÉTADONNÉES"
            category = "❌ NON ESSENTIEL"
            action = "SUPPRIMER"
            delete.append((fname, size_mb))
        
        else:
            verdict = "INCONNU"
            category = "❓ À VÉRIFIER"
            action = "CHECK"
            print(f"Cols: {df.columns[:3].tolist()}")
            
        print(f"{verdict:<20} {category:<25} [{action}]")
            
    except Exception as e:
        print(f" | [ERREUR LECTURE] {str(e)[:60]}")

print()
print("=" * 130)
print("RÉSUMÉ - RECOMMANDATIONS")
print("=" * 130)
print()

print(f"✅ À GARDER ({len(keep)} fichiers):")
total_keep = 0
for fname, size_mb, desc in keep:
    print(f"   • {fname:<50} {size_mb:>7.2f} MB  →  {desc}")
    total_keep += size_mb
print(f"   TOTAL: {total_keep:.2f} MB")

print()
print(f"❌ À SUPPRIMER ({len(delete)} fichier(s)):")
total_delete = 0
for fname, size_mb in delete:
    print(f"   • {fname:<50} {size_mb:>7.2f} MB")
    total_delete += size_mb
print(f"   TOTAL LIBÉRÉ: {total_delete:.2f} MB")

print()
print("🎉 DÉCOUVERTES - NOUVEAUX INDICATEURS TROUVÉS:")
for indicator in set(new_indicators):
    print(f"   ✅ {indicator}")

print()
print("=" * 130)
