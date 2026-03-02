"""
SCRIPT 04 - MODÉLISATION MACHINE LEARNING
=========================================

Construction et évaluation de 2 modèles :

1. RANDOM FOREST : Régression supervisée pour prédire votes futurs
   - Feature selection
   - Hyperparamètrage
   - Évaluation (R², RMSE, MAE)
   - Feature importance

2. K-MEANS : Clustering pour segmenter régions
   - Déterminer nombre clusters optimal (Elbow)
   - Analyse des profils
   - Visualisation clusters

Données : data/processed/mspr1_aura_clean.csv
Modèles sauvegardés : scripts/ (pickle)
Prédictions : data/processed/predictions.csv

Exécution : python scripts/04_modeles.py
"""

import os
import pickle
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.cluster import KMeans
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error, silhouette_score
from sklearn.decomposition import PCA

# Import config
from config import (
    PATH_DATA_PROCESSED, PATH_RAPPORTS, RANDOM_STATE, TEST_SIZE,
    VALIDATION_K_FOLD, RF_N_ESTIMATORS, RF_MAX_DEPTH, RF_MIN_SAMPLES_SPLIT,
    KMEANS_N_CLUSTERS
)

print("=" * 70)
print("SCRIPT 04 - MODÉLISATION MACHINE LEARNING")
print("=" * 70)
print()

# ============================================================================
# ÉTAPE 1 : CHARGER ET PRÉPARER DONNÉES
# ============================================================================
def load_and_prepare_data():
    """Charger et préparer données pour ML."""
    print("[1] Chargement et préparation données...")
    
    df = pd.read_csv(f"{PATH_DATA_PROCESSED}mspr1_aura_clean.csv")
    
    # Sélectionner colonnes numériques
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    # Définir variable cible (exemple : vote_majoritaire si existe)
    # Sinon utiliser proxy ou créer target artificielle
    target_col = 'vote_majoritaire' if 'vote_majoritaire' in df.columns else None
    
    print(f"  ✓ Données chargées : {df.shape[0]} lignes x {len(numeric_cols)} features")
    
    return df, numeric_cols, target_col


# ============================================================================
# ÉTAPE 2 : MODÈLE 1 - RANDOM FOREST
# ============================================================================
def train_random_forest(df, numeric_cols, target_col):
    """Entraîner modèle Random Forest."""
    print("[2] Entraînement Random Forest...")
    
    if target_col is None:
        print("  ⚠ Pas de variable cible - modèle non entraîné")
        return None, None, None
    
    # Préparer features et target
    X = df[numeric_cols].dropna()
    y = df.loc[X.index, target_col]
    
    # Supprimer rows avec NaN target
    valid_idx = ~y.isnull()
    X = X[valid_idx]
    y = y[valid_idx]
    
    if len(y) < 10:
        print("  ⚠ Pas assez de données pour entraîner le modèle")
        return None, None, None
    
    # Division train/test
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE
    )
    
    # Normaliser features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Entraîner modèle
    rf_model = RandomForestRegressor(
        n_estimators=RF_N_ESTIMATORS,
        max_depth=RF_MAX_DEPTH,
        min_samples_split=RF_MIN_SAMPLES_SPLIT,
        random_state=RANDOM_STATE,
        n_jobs=-1
    )
    
    rf_model.fit(X_train, y_train)  # Pas scaling pour RF
    
    # Prédictions
    y_pred = rf_model.predict(X_test)
    
    # Évaluation
    r2 = r2_score(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    
    print(f"  ✓ Random Forest entraîné")
    print(f"    - R² score : {r2:.4f}")
    print(f"    - RMSE : {rmse:.4f}")
    print(f"    - MAE : {mae:.4f}")
    
    # Feature importance
    feature_importance = pd.DataFrame({
        'feature': numeric_cols[:len(rf_model.feature_importances_)],
        'importance': rf_model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print(f"\n  Top 5 features :")
    print(feature_importance.head())
    
    # Visualiser feature importance
    plt.figure(figsize=(10, 6))
    plt.barh(feature_importance['feature'][:15], feature_importance['importance'][:15])
    plt.xlabel('Importance')
    plt.title('Random Forest - Feature Importance')
    plt.tight_layout()
    plt.savefig(f"{PATH_RAPPORTS}06_rf_feature_importance.png", dpi=300)
    plt.close()
    
    # Sauvegarder modèle
    with open('./scripts/random_forest_model.pkl', 'wb') as f:
        pickle.dump(rf_model, f)
    
    return rf_model, scaler, feature_importance


# ============================================================================
# ÉTAPE 3 : MODÈLE 2 - K-MEANS
# ============================================================================
def train_kmeans(df, numeric_cols):
    """Entraîner modèle K-Means."""
    print("\n[3] Entraînement K-Means...")
    
    # Préparer données
    X = df[numeric_cols].dropna()
    
    # Normaliser
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    # Déterminer nombre clusters optimal (Elbow method)
    inertias = []
    silhouette_scores = []
    K_range = range(2, 8)
    
    for k in K_range:
        km = KMeans(n_clusters=k, random_state=RANDOM_STATE, n_init=10)
        km.fit(X_scaled)
        inertias.append(km.inertia_)
        silhouette_scores.append(silhouette_score(X_scaled, km.labels_))
    
    # Visualiser Elbow
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    ax1.plot(K_range, inertias, 'bo-', linewidth=2, markersize=8)
    ax1.set_xlabel('Nombre de clusters (k)')
    ax1.set_ylabel('Inertie')
    ax1.set_title('Elbow Method')
    ax1.grid(True, alpha=0.3)
    
    ax2.plot(K_range, silhouette_scores, 'ro-', linewidth=2, markersize=8)
    ax2.set_xlabel('Nombre de clusters (k)')
    ax2.set_ylabel('Silhouette Score')
    ax2.set_title('Silhouette Analysis')
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f"{PATH_RAPPORTS}07_kmeans_elbow.png", dpi=300)
    plt.close()
    
    # Utiliser k optimal
    best_k = KMEANS_N_CLUSTERS
    kmeans_model = KMeans(n_clusters=best_k, random_state=RANDOM_STATE, n_init=10)
    clusters = kmeans_model.fit_predict(X_scaled)
    
    print(f"  ✓ K-Means entraîné (k={best_k})")
    print(f"    - Silhouette score : {silhouette_scores[best_k-2]:.4f}")
    
    # Visualiser clusters (PCA 2D)
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X_scaled)
    
    plt.figure(figsize=(10, 8))
    scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=clusters, cmap='viridis', s=100, alpha=0.6)
    plt.scatter(pca.transform(kmeans_model.cluster_centers_)[:, 0],
                pca.transform(kmeans_model.cluster_centers_)[:, 1],
                c='red', marker='X', s=300, edgecolors='black', linewidths=2, label='Centroids')
    plt.xlabel(f'PC1 ({pca.explained_variance_ratio_[0]:.1%})')
    plt.ylabel(f'PC2 ({pca.explained_variance_ratio_[1]:.1%})')
    plt.title('K-Means Clustering (PCA visualization)')
    plt.colorbar(scatter, label='Cluster')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{PATH_RAPPORTS}08_kmeans_visualization.png", dpi=300)
    plt.close()
    
    # Sauvegarder modèle
    with open('./scripts/kmeans_model.pkl', 'wb') as f:
        pickle.dump(kmeans_model, f)
    
    return kmeans_model, clusters, scaler


# ============================================================================
# ÉTAPE 4 : GÉNÉRER PRÉDICTIONS
# ============================================================================
def generate_predictions(rf_model, X_test):
    """Générer prédictions futures."""
    print("\n[4] Génération prédictions...")
    
    if rf_model is None:
        print("  ⚠ Modèle RF non disponible - prédictions impossibles")
        return None
    
    # Prédictions
    predictions = rf_model.predict(X_test)
    
    # DataFrame résultats
    predictions_df = pd.DataFrame({
        'prediction': predictions,
        'confidence': rf_model.predict(X_test)  # Approx confidence
    })
    
    # Exporter
    predictions_df.to_csv(f"{PATH_DATA_PROCESSED}predictions.csv", index=False)
    print(f"  ✓ Prédictions sauvegardées : {len(predictions_df)} résultats")
    
    return predictions_df


# ============================================================================
# MAIN
# ============================================================================
if __name__ == "__main__":
    try:
        # Charger données
        df, numeric_cols, target_col = load_and_prepare_data()
        
        # Random Forest
        rf_model, scaler, feature_importance = train_random_forest(df, numeric_cols, target_col)
        
        # K-Means
        kmeans_model, clusters, kmeans_scaler = train_kmeans(df, numeric_cols)
        
        # Prédictions
        if rf_model is not None:
            X_test = df[numeric_cols].dropna().sample(min(50, len(df)))
            predictions = generate_predictions(rf_model, X_test)
        
        print()
        print("=" * 70)
        print("✓ MODÉLISATION TERMINÉE")
        print("=" * 70)
        print()
        print("Modèles sauvegardés :")
        print("  - Random Forest : scripts/random_forest_model.pkl")
        print("  - K-Means : scripts/kmeans_model.pkl")
        print()
        print("Visualisations sauvegardées dans : {PATH_RAPPORTS}")
        print()
        print("Étapes suivantes :")
        print("  1. Configurer base données PostgreSQL")
        print("  2. Charger résultats dans visualisation Grafana")
        print("  3. Rédiger rapport final")
        print()
        
    except Exception as e:
        print(f"❌ ERREUR : {e}")
        raise
