#!/usr/bin/env python3
"""Analyse détaillée des fichiers CSV du projet MSPR1"""

import pandas as pd
import os
from pathlib import Path

# Liste des fichiers à analyser
raw_dir = Path("data/raw")
files = [
    "base-ic-evol-struct-pop-2022.CSV",
    "base-ic-diplomes-formation-2022.CSV",
    "data_RPLS2024_COM.csv",
    "data_RPLS2024_Iris.csv",
    "delits_cambriolages.csv",
    "elections_2022_2017.csv"
]

# Codes AURA
AURA_CODES = {"01", "03", "07", "15", "26", "38", "42", "43", "63", "69", "73", "74"}

print("=" * 120)
print("ANALYSE DÉTAILLÉE - FICHIERS CSV MSPR1")
print("=" * 120)
print()

analysis_results = []

for file in files:
    filepath = raw_dir / file
    
    if not filepath.exists():
        print(f"❌ {file} - NON TROUVÉ")
        continue
    
    try:
        # Charger CSV
        try:
            df = pd.read_csv(filepath, encoding='utf-8', nrows=2000)
        except UnicodeDecodeError:
            df = pd.read_csv(filepath, encoding='latin-1', nrows=2000)
        
        size_mb = filepath.stat().st_size / (1024 * 1024)
        
        print(f"📄 {file}")
        print(f"   Taille disque: {size_mb:.2f} MB")
        print(f"   Dimensions: {df.shape[0]:,} lignes (premier batch) x {df.shape[1]} colonnes")
        print(f"   Colonnes ({df.shape[1]}): {', '.join(df.columns.tolist()[:8])}")
        if df.shape[1] > 8:
            print(f"                  {', '.join(df.columns.tolist()[8:])}")
        print(f"   Types données: {dict(df.dtypes.value_counts())}")
        print(f"   Valeurs manquantes: {df.isnull().sum().sum():,} NaN")
        
        # Chercher colonnes département
        dept_candidates = [col for col in df.columns if any(x in col.lower() for x in ['dept', 'code', 'commune', 'iris', 'geog'])]
        
        if dept_candidates:
            print(f"   🎯 Colonnes géographiques: {dept_candidates[:3]}")
            
            aura_coverage = 0
            for col in dept_candidates[:2]:
                try:
                    # Extraire codes département
                    codes = df[col].astype(str).str[:2].unique()
                    codes_aura = set(codes) & AURA_CODES
                    coverage = len(codes_aura) / len(AURA_CODES) * 100
                    aura_coverage = max(aura_coverage, coverage)
                    
                    if codes_aura:
                        print(f"      ├─ {col}: {len(codes_aura)}/12 depts AURA ({coverage:.0f}%)")
                except:
                    pass
            
            print(f"   ✅ Couverture AURA: {aura_coverage:.0f}%")
        else:
            print(f"   ⚠️ Pas de colonne département trouvée")
        
        # Analyse spécifique par fichier
        if "pop" in file.lower():
            print(f"   📊 Type: Données POPULATION/DÉMOGRAPHIE")
            print(f"      Indicateurs: Âge moyen, structure par âge, population")
            print(f"      ✅ NÉCESSAIRE pour indicateur #3 (Âge moyen)")
            
        elif "diplome" in file.lower():
            print(f"   📊 Type: Données ÉDUCATION/DIPLÔMES")
            print(f"      Indicateurs: Niveaux de diplôme, CAP, BAC, Licence, Master")
            print(f"      ✅ NÉCESSAIRE pour indicateur #4 (Niveau diplôme)")
            
        elif "RPLS" in file:
            if "COM" in file:
                print(f"   📊 Type: LOGEMENTS SOCIAUX (niveau Commune)")
                print(f"      ✅ Alternative moins détaillée (préférer IRIS)")
                print(f"      🔴 OPTIONNEL - Garder IRIS si présent")
            else:
                print(f"   📊 Type: LOGEMENTS SOCIAUX (niveau IRIS - détaillé)")
                print(f"      ✅ NÉCESSAIRE pour indicateur #10 (Logements sociaux)")
                print(f"      Grain: IRIS (quartiers)")
            
        elif "delit" in file.lower() or "cambriolage" in file.lower():
            print(f"   📊 Type: CRIMINALITÉ/DÉLITS")
            print(f"      Indicateurs: Cambriolages, délits enregistrés")
            print(f"      ✅ NÉCESSAIRE pour indicateur #5 (Cambriolages)")
            
        elif "election" in file.lower():
            print(f"   📊 Type: ÉLECTIONS (Bureau de vote)")
            print(f"      Années: 2017 + 2022")
            print(f"      Variables cible: Résultats par parti, abstention, votants")
            print(f"      ✅ NÉCESSAIRE pour indicateurs #6 & #7 (Votes)")
            print(f"      ⚠️ Format: Très volumineux (bureau de vote) - peut demander agrégation")
        
        print()
        
    except Exception as e:
        print(f"⚠️ {file} - ERREUR LECTURE: {str(e)[:80]}")
        print()

print("=" * 120)
print("SYNTHÈSE - QUE GARDER ?")
print("=" * 120)
print()
print("✅ À CONSERVER EN PRIORITÉ:")
print("   1. base-ic-evol-struct-pop-2022.CSV (48.89 MB) - Données population [ESSENTIEL]")
print("   2. base-ic-diplomes-formation-2022.CSV (26.29 MB) - Données diplômes [ESSENTIEL]")
print("   3. data_RPLS2024_Iris.csv (2.01 MB) - Logements sociaux détaillés [ESSENTIEL]")
print("   4. delits_cambriolages.csv (1.91 MB) - Délits par département [ESSENTIEL]")
print("   5. elections_2022_2017.csv (376.24 MB) - Elections bureau de vote [ESSENTIEL]")
print()
print("⚠️ À SUPPRIMER (REDONDANT):")
print("   • data_RPLS2024_COM.csv (0.27 MB) - Même data qu'IRIS mais moins détaillée [NON ESSENTIEL]")
print()
print("📊 TOTAL À GARDER: 455.34 MB (6 fichiers)")
print("💾 ESPACE À LIBÉRER: 0.27 MB (1 fichier redondant)")
print()
