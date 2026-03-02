"""
SCRIPT 03 - ANALYSE EXPLORATOIRE ET VISUALISATIONS
==================================================

Exploration visuelle et statistique des données nettoyées :
- Statistiques descriptives
- Matrice corrélations
- Visualisations : histogrammes, boxplots, heatmaps
- Détection outliers
- Tendances temporelles

Données : data/processed/mspr1_aura_clean.csv
Visualisations exportées : rapports/

Exécution : python scripts/03_exploration.py
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Import config
from config import PATH_DATA_PROCESSED, PATH_RAPPORTS

# Créer dossier rapports si n'existe pas
os.makedirs(PATH_RAPPORTS, exist_ok=True)

print("=" * 70)
print("SCRIPT 03 - ANALYSE EXPLORATOIRE (EDA)")
print("=" * 70)
print()

# ============================================================================
# ÉTAPE 1 : CHARGER DONNÉES NETTOYÉES
# ============================================================================
def load_clean_data():
    """Charger fichier nettoyé."""
    print("[1] Chargement données nettoyées...")
    
    df = pd.read_csv(f"{PATH_DATA_PROCESSED}mspr1_aura_clean.csv")
    
    print(f"  ✓ Fichier chargé : {df.shape[0]} lignes x {df.shape[1]} colonnes")
    
    return df


# ============================================================================
# ÉTAPE 2 : STATISTIQUES DESCRIPTIVES GÉNÉRALES
# ============================================================================
def descriptive_statistics(df):
    """Afficher statistiques descriptives."""
    print("[2] Statistiques descriptives...")
    
    print("\n=== RÉSUMÉ DONNÉES ===")
    print(df.describe().round(2))
    
    print("\n=== TYPES COLONNES ===")
    print(df.dtypes)
    
    print("\n=== VALEURS MANQUANTES ===")
    print(df.isnull().sum())
    
    return df


# ============================================================================
# ÉTAPE 3 : MATRICE CORRÉLATIONS
# ============================================================================
def correlation_analysis(df):
    """Analyser corrélations entre variables numériques."""
    print("[3] Analyse corrélations...")
    
    # Sélectionner colonnes numériques
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    # Matrice corrélation
    corr_matrix = df[numeric_cols].corr()
    
    # Afficher corrélations fortes (>0.5) avec vote
    if 'vote_majoritaire' in corr_matrix.columns:
        strong_corr = corr_matrix['vote_majoritaire'].abs().sort_values(ascending=False)
        print("\n=== CORRÉLATIONS AVEC VOTE ===")
        print(strong_corr[strong_corr > 0.3].round(3))
    
    # Visualiser heatmap corrélation
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0, 
                square=True, linewidths=1, cbar_kws={"shrink": 0.8})
    plt.title("Matrice de Corrélation - Variables AURA")
    plt.tight_layout()
    plt.savefig(f"{PATH_RAPPORTS}01_matrice_correlation.png", dpi=300)
    print("  ✓ Heatmap corrélation sauvegardée")
    plt.close()
    
    return corr_matrix


# ============================================================================
# ÉTAPE 4 : HISTOGRAMMES INDICATEURS
# ============================================================================
def histogram_indicators(df):
    """Créer histogrammes pour chaque indicateur."""
    print("[4] Création histogrammes indicateurs...")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    # Subplot 2x5 pour 10 indicateurs
    fig, axes = plt.subplots(5, 2, figsize=(15, 20))
    axes = axes.flatten()
    
    for idx, col in enumerate(numeric_cols[:10]):
        axes[idx].hist(df[col].dropna(), bins=20, color='steelblue', edgecolor='black', alpha=0.7)
        axes[idx].set_title(f"Distribution - {col}", fontsize=10, fontweight='bold')
        axes[idx].set_xlabel(col)
        axes[idx].set_ylabel("Fréquence")
        axes[idx].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{PATH_RAPPORTS}02_histogrammes_indicateurs.png", dpi=300)
    print("  ✓ Histogrammes sauvegardés")
    plt.close()


# ============================================================================
# ÉTAPE 5 : BOXPLOTS (DÉTECTION OUTLIERS)
# ============================================================================
def boxplots_outliers(df):
    """Créer boxplots pour détecter outliers."""
    print("[5] Création boxplots (outliers)...")
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    fig, axes = plt.subplots(5, 2, figsize=(15, 20))
    axes = axes.flatten()
    
    for idx, col in enumerate(numeric_cols[:10]):
        axes[idx].boxplot(df[col].dropna(), vert=True)
        axes[idx].set_title(f"Boxplot - {col}", fontsize=10, fontweight='bold')
        axes[idx].set_ylabel(col)
        axes[idx].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{PATH_RAPPORTS}03_boxplots_outliers.png", dpi=300)
    print("  ✓ Boxplots sauvegardés")
    plt.close()


# ============================================================================
# ÉTAPE 6 : ANALYSE TEMPORELLE (2017-2022)
# ============================================================================
def temporal_analysis(df):
    """Analyser tendances temporelles."""
    print("[6] Analyse temporelle (2017-2022)...")
    
    # Vérifier si colonne 'annee' existe
    if 'annee' not in df.columns:
        print("  ⚠ Pas de colonne 'annee' - analyse temporelle ignorée")
        return
    
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    
    # Évolution temporelle par indicateur
    fig, axes = plt.subplots(5, 2, figsize=(15, 20))
    axes = axes.flatten()
    
    for idx, col in enumerate(numeric_cols[:10]):
        temporal_data = df.groupby('annee')[col].mean()
        axes[idx].plot(temporal_data.index, temporal_data.values, marker='o', linewidth=2, markersize=6)
        axes[idx].set_title(f"Évolution temporelle - {col}", fontsize=10, fontweight='bold')
        axes[idx].set_xlabel("Année")
        axes[idx].set_ylabel(col)
        axes[idx].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{PATH_RAPPORTS}04_evolution_temporelle.png", dpi=300)
    print("  ✓ Analyse temporelle sauvegardée")
    plt.close()


# ============================================================================
# ÉTAPE 7 : COMPARAISON PAR DÉPARTEMENT
# ============================================================================
def comparison_by_dept(df):
    """Comparer indicateurs clés par département."""
    print("[7] Comparaison par département...")
    
    if 'code_dept' not in df.columns:
        print("  ⚠ Pas de colonne 'code_dept' - comparaison ignorée")
        return
    
    # Moyenne par département
    dept_stats = df.groupby('code_dept').agg({
        'revenu_median': 'mean',
        'taux_chomage': 'mean',
        'age_moyen': 'mean'
    }).round(2)
    
    print("\n=== MOYENNES PAR DÉPARTEMENT ===")
    print(dept_stats)
    
    # Visualiser écarts
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    
    dept_stats['revenu_median'].plot(kind='bar', ax=axes[0], color='steelblue')
    axes[0].set_title("Revenu Médian par Département")
    axes[0].set_ylabel("€")
    axes[0].tick_params(axis='x', rotation=45)
    
    dept_stats['taux_chomage'].plot(kind='bar', ax=axes[1], color='coral')
    axes[1].set_title("Taux Chômage par Département")
    axes[1].set_ylabel("%")
    axes[1].tick_params(axis='x', rotation=45)
    
    dept_stats['age_moyen'].plot(kind='bar', ax=axes[2], color='lightgreen')
    axes[2].set_title("Âge Moyen par Département")
    axes[2].set_ylabel("Ans")
    axes[2].tick_params(axis='x', rotation=45)
    
    plt.tight_layout()
    plt.savefig(f"{PATH_RAPPORTS}05_comparaison_departements.png", dpi=300)
    print("  ✓ Comparaison par département sauvegardée")
    plt.close()


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    try:
        # Charger données
        df = load_clean_data()
        
        # Descriptive stats
        df = descriptive_statistics(df)
        
        # Corrélations
        corr = correlation_analysis(df)
        
        # Visualisations
        histogram_indicators(df)
        boxplots_outliers(df)
        temporal_analysis(df)
        comparison_by_dept(df)
        
        print()
        print("=" * 70)
        print("✓ ANALYSE EXPLORATOIRE TERMINÉE")
        print("=" * 70)
        print()
        print(f"Visualisations sauvegardées dans : {PATH_RAPPORTS}")
        print()
        print("Prochaine étape : python scripts/04_modeles.py")
        print()
        
    except Exception as e:
        print(f"❌ ERREUR : {e}")
        raise
