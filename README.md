# MSPR1 - Prédiction Tendances Électorales AURA

## Contexte
Proof of Concept pour **Electio-Analytics** : modèle prédictif des tendances électorales en région Auvergne-Rhône-Alpes sur 1-3 ans en exploitant données publiques et indicateurs socio-économiques.

## Structure du Projet

```
project/
├── data/
│   ├── raw/              # Données brutes (CSV téléchargés)
│   └── processed/        # Données nettoyées (après Pandas)
├── scripts/
│   ├── 01_extraction.py  # Récupération données
│   ├── 02_nettoyage.py   # Nettoyage Pandas
│   ├── 03_exploration.py # Analyse exploratoire
│   └── 04_modeles.py     # Random Forest + K-Means
├── sql/
│   ├── schema.sql        # Structure base données
│   └── inserts.sql       # Chargement données nettoyées
├── grafana/
│   └── dashboards/       # Configurations dashboards
├── rapports/             # Rapport final + annexes
├── requirements.txt      # Dépendances Python
└── README.md            # Ce fichier
```

## Installation

### 1. Créer environnement virtuel Python
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate # Linux/Mac
```

### 2. Installer dépendances
```bash
pip install -r requirements.txt
```

### 3. Configurer PostgreSQL
```bash
# Créer base de données
createdb mspr1_aura

# Configurer connexion (voir fichier config.py si créé)
```

### 4. Installer Grafana (optionnel pour visualisation)
Télécharger : https://grafana.com/grafana/download

## Datasets Collectés (10 indicateurs)

| Indicateur | Unité | Source | Période |
|-----------|-------|--------|---------|
| Revenu médian | €/an | INSEE | 2017-2022 |
| Taux de chômage | % | INSEE | 2017-2022 |
| Âge moyen | ans | INSEE | 2017-2022 |
| Niveau diplôme moyen | % bac+ | INSEE | 2017-2022 |
| Cambriolages | nombre | Min Intérieur | 2017-2022 |
| Vote 2022 | parti majoritaire | Ministère | 2022 |
| Vote 2017 | parti majoritaire | Ministère | 2017 |
| Terres agricoles | % surface | Teruti | 2017-2022 |
| Résidences secondaires | % logements | Foncier | 2017-2022 |
| Logements sociaux | % logements | SNCF/Immobilière | 2017-2022 |

## Région d'Étude

**AURA - Auvergne Rhône-Alpes (12 départements)**
- 01 Ain | 03 Allier | 07 Ardèche | 15 Cantal
- 26 Drôme | 38 Isère | 42 Loire | 43 Haute-Loire
- 63 Puy-de-Dôme | 69 Rhône | 73 Savoie | 74 Haute-Savoie

## Modèles Utilisés

### 1. Random Forest (Régression)
- **Objectif** : Prédire vote majoritaire 2024-2026
- **Hyperparamètres** : n_estimators=100, max_depth=15, min_samples_split=5
- **Évaluation** : R², RMSE, MAE, Feature Importance

### 2. K-Means (Clustering)
- **Objectif** : Segmenter départements en profils régionaux
- **Clusters** : 3-5 groupes (urbain/rural, riche/pauvre)
- **Évaluation** : Silhouette Score, Inertia

## Exécution des Scripts

```bash
# Étape 1 : Extraction données
python scripts/01_extraction.py

# Étape 2 : Nettoyage avec Pandas
python scripts/02_nettoyage.py

# Étape 3 : Analyse exploratoire
python scripts/03_exploration.py

# Étape 4 : Modélisation (RF + K-Means)
python scripts/04_modeles.py
```

## Livrables

- ✅ Base données PostgreSQL structurée
- ✅ Fichiers CSV nettoyés (processed/)
- ✅ Scripts Python commentés
- ✅ Dashboards Grafana (4 dashboards)
- ✅ Rapport complet (PDF + Markdown)
- ✅ Présentation orale (20 mn)

## Compétences Développées

- ✅ Collecte et analyse besoins données (BI)
- ✅ Architecture Big Data (ETL)
- ✅ Nettoyage données (Pandas)
- ✅ Exploration & visualisation
- ✅ Machine Learning (Random Forest, K-Means)
- ✅ Dashboards temps réel (Grafana)
- ✅ Qualité & sécurité données (RGPD)

## Contacts & Ressources

- Documentation INSEE : https://www.insee.fr
- Data.gouv.fr : https://www.data.gouv.fr
- Scikit-learn Doc : https://scikit-learn.org
- Grafana Doc : https://grafana.com/docs

## Timeline

| Phase | Durée | Status |
|-------|-------|--------|
| Préparation & structure | 2 jours | ✅ En cours |
| Extraction données | 3 jours | ⏳ À venir |
| Nettoyage Pandas | 3 jours | ⏳ À venir |
| Analyse exploratoire | 3 jours | ⏳ À venir |
| Modélisation RF + K-Means | 4 jours | ⏳ À venir |
| Grafana + Dashboards | 2 jours | ⏳ À venir |
| Documentation & rapport | 3 jours | ⏳ À venir |
| **TOTAL** | **20 jours** | |

---
**Dernière mise à jour** : 2 mars 2026
