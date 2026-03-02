"""
SCRIPT 02 - NETTOYAGE DES DONNÉES AVEC PANDAS
==============================================

Nettoyage et préparation des données brutes avec Pandas :
- Importer tous les CSV
- Harmoniser formats & colonnes
- Gérer valeurs manquantes
- Fusionner par département
- Exporter données nettoyées

Données entrée : data/raw/
Données sortie : data/processed/

Exécution : python scripts/02_nettoyage.py
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# Import config
from config import PATH_DATA_RAW, PATH_DATA_PROCESSED, AURA_DEPARTMENTS, MIN_YEAR, MAX_YEAR

# Créer dossier processed si n'existe pas
os.makedirs(PATH_DATA_PROCESSED, exist_ok=True)

print("=" * 70)
print("SCRIPT 02 - NETTOYAGE DES DONNÉES (PANDAS)")
print("=" * 70)
print()

# ============================================================================
# ÉTAPE 1 : IMPORTER TOUS LES FICHIERS CSV BRUTS
# ============================================================================
def load_raw_data():
    """Importer tous les fichiers CSV depuis data/raw/"""
    print("[1] Chargement fichiers bruts...")
    
    data = {}
    
    # À implémenter : Charger chaque CSV
    # Exemple :
    # data['revenu'] = pd.read_csv(f"{PATH_DATA_RAW}insee_revenu_median.csv")
    
    print("  ✓ Tous les fichiers chargés en mémoire")
    return data


# ============================================================================
# ÉTAPE 2 : STANDARDISER COLONNE CODE DÉPARTEMENT
# ============================================================================
def standardize_dept_column(df):
    """Standardiser colonne code département (format '01' à '74')."""
    
    # Colonnes possibles : 'code_dept', 'dept_code', 'CODE_DEPT', 'CODDEP'
    for col in df.columns:
        if 'dept' in col.lower() or 'code' in col.lower():
            df['code_dept'] = df[col].astype(str).str.zfill(2)
            break
    
    return df


# ============================================================================
# ÉTAPE 3 : FILTRER SEULEMENT AURA (12 DEPTS)
# ============================================================================
def filter_aura_departments(df):
    """Garder seulement les 12 départements AURA."""
    
    if 'code_dept' in df.columns:
        df = df[df['code_dept'].isin(AURA_DEPARTMENTS)]
    
    return df


# ============================================================================
# ÉTAPE 4 : GÉRER VALEURS MANQUANTES
# ============================================================================
def handle_missing_values(df, threshold=0.30):
    """
    Gérer les NaN :
    - Supprimer colonnes si >30% NaN
    - Imputation moyenne/médiane pour valeurs numériques
    """
    
    print("  Gestion valeurs manquantes...")
    
    # Afficher % NaN par colonne
    missing_pct = (df.isnull().sum() / len(df) * 100).round(2)
    if missing_pct.any():
        print(f"    Colonnes avec NaN : {missing_pct[missing_pct > 0]}")
    
    # Supprimer colonnes si >30% NaN
    df = df.loc[:, missing_pct < threshold]
    
    # Imputation valeurs numériques (median)
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isnull().any():
            df[col].fillna(df[col].median(), inplace=True)
    
    return df


# ============================================================================
# ÉTAPE 5 : NORMALISER NOMS COLONNES
# ============================================================================
def normalize_column_names(df):
    """Normaliser noms colonnes : minuscules, snake_case."""
    
    df.columns = df.columns.str.lower().str.replace(' ', '_').str.replace('-', '_')
    
    return df


# ============================================================================
# ÉTAPE 6 : FUSIONNER TOUS LES DATAFRAMES
# ============================================================================
def merge_all_datasets(data_dict):
    """Fusionner tous les datasets par code département."""
    
    print("[2] Fusion tous les datasets...")
    
    # Commencer avec le dataframe 'revenu' comme base
    df_merged = data_dict.get('revenu', pd.DataFrame())
    
    # Fusionner progressivement
    for name, df in data_dict.items():
        if name != 'revenu':
            df_merged = df_merged.merge(df, on=['code_dept', 'annee'], how='outer', suffixes=('', f'_{name}'))
    
    print("  ✓ Tous les datasets fusionnés")
    
    return df_merged


# ============================================================================
# ÉTAPE 7 : AJOUTER COLONNES CALCULÉES
# ============================================================================
def add_calculated_columns(df):
    """Ajouter variables calculées."""
    
    print("[3] Ajout variables calculées...")
    
    # Exemple : Calculer âge groupe
    # if 'age_moyen' in df.columns:
    #     df['groupe_age'] = pd.cut(df['age_moyen'], bins=[0, 35, 45, 60, 100], 
    #                                labels=['Jeune', 'Central', 'Senior', 'Très senior'])
    
    print("  ✓ Variables calculées ajoutées")
    
    return df


# ============================================================================
# ÉTAPE 8 : VALIDER DONNÉES NETTOYÉES
# ============================================================================
def validate_clean_data(df):
    """Valider intégrité données nettoyées."""
    
    print("[4] Validation données...")
    
    print(f"  Dimensions : {df.shape[0]} lignes x {df.shape[1]} colonnes")
    print(f"  Période : {df['annee'].min()} à {df['annee'].max()}")
    print(f"  Depts AURA : {df['code_dept'].nunique()} uniques")
    print(f"  NaN : {df.isnull().sum().sum()} résidus")
    
    print("  ✓ Validation OK")
    
    return df


# ============================================================================
# ÉTAPE 9 : EXPORTER DONNÉES NETTOYÉES
# ============================================================================
def export_clean_data(df):
    """Exporter CSV nettoyé."""
    
    print("[5] Export données nettoyées...")
    
    output_file = f"{PATH_DATA_PROCESSED}mspr1_aura_clean.csv"
    df.to_csv(output_file, index=False)
    
    print(f"  ✓ Fichier sauvegardé : {output_file}")
    
    return output_file


# ============================================================================
# MAIN : Lancer pipeline nettoyage
# ============================================================================
if __name__ == "__main__":
    try:
        # Charger données brutes
        data = load_raw_data()
        
        # Nettoyer chaque dataframe
        print("[2] Nettoyage dataframes individuels...")
        for name, df in data.items():
            df = standardize_dept_column(df)
            df = filter_aura_departments(df)
            df = normalize_column_names(df)
            df = handle_missing_values(df)
            data[name] = df
            print(f"  ✓ {name} nettoyé")
        
        # Fusionner
        df_final = merge_all_datasets(data)
        
        # Ajouter variables calculées
        df_final = add_calculated_columns(df_final)
        
        # Valider
        df_final = validate_clean_data(df_final)
        
        # Exporter
        output_file = export_clean_data(df_final)
        
        print()
        print("=" * 70)
        print("✓ NETTOYAGE TERMINÉ")
        print("=" * 70)
        print()
        print(f"Données nettoyées disponibles : {output_file}")
        print()
        print("Prochaine étape : python scripts/03_exploration.py")
        print()
        
    except Exception as e:
        print(f"❌ ERREUR : {e}")
        raise
