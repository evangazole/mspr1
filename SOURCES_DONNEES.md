# Sources de Données - AURA (Auvergne Rhône-Alpes)

**Région ciblée** : 12 départements (01, 03, 07, 15, 26, 38, 42, 43, 63, 69, 73, 74)  
**Période** : 2017-2022 (5 années)  
**Format collecte** : CSV ou Excel (via téléchargement manuel ou API)

---

## 1️⃣ REVENU MÉDIAN
**Indicateur clé pour prédiction votes**

### Source principale : INSEE
- **URL base** : https://www.insee.fr/fr/statistiques
- **Données** : Revenus & Salaires → Données régionales
- **Fichier à chercher** : 
  - "REV_RIC_REG" (Revenus fiscaux par région)
  - "REV_DEP" (Revenus par département)
- **Millésimes** : 2017, 2018, 2019, 2020, 2021, 2022
- **Format** : CSV/XLS
- **Clé de fusion** : Code département

### Alternative (Agirc-Arrco) :
- https://www.agirc-arrco.fr/documents-statistiques

---

## 2️⃣ TAUX DE CHÔMAGE
**Indicateur structurant pour prédictions**

### Source principale : INSEE
- **URL base** : https://www.insee.fr/fr/statistiques/5431902
- **Données** : Taux de chômage par région/département
- **Fichier** : "CHOMRF" (Chômage régions/France)
- **Millésimes** : Trimestriel 2017-2022
- **Format** : CSV/Tableau direct
- **Clé de fusion** : Code département

### Alternative (Pôle Emploi) :
- https://www.data.gouv.fr/fr/datasets/
- Rechercher "Pôle emploi - demandeurs d'emploi"

---

## 3️⃣ ÂGE MOYEN POPULATION
**Données démographiques essentielles**

### Source principale : INSEE (Recensement)
- **URL** : https://www.insee.fr/fr/statistics/by-theme/2
- **Données** : Pyramide des âges par département
- **Fichier** : "RP_CHPS" ou "TAB_POP"
- **Millésimes** : 2017, 2019, 2021, 2022
- **Format** : CSV depuis INSEE
- **Clé de fusion** : Code département (CODGEO)

### Calculer :
```
age_moyen = sum(age_classe * population_classe) / population_totale
```

---

## 4️⃣ NIVEAU DE DIPLÔME MOYEN
**Profil population → comportement électoral**

### Source principale : INSEE (Scolarité & Diplômes)
- **URL** : https://www.insee.fr/fr/statistics/2558070
- **Données** : Diplôme le plus élevé par département
- **Fichier** : "RP_SCOL" ou "FORM_DIPL"
- **Millésimes** : 2017, 2019, 2021, 2022
- **Format** : CSV
- **Variables clés** :
  - % Bac+2 minimum
  - % Bac
  - % Niveau collège ou sans diplôme
- **Clé de fusion** : Code département

### Calculer :
```
% population_diplome_bac_plus = (Bac+2+ / Pop_15ans_scolarisee) * 100
```

---

## 5️⃣ CAMBRIOLAGES
**Sécurité zone → perception électorale**

### Source principale : Ministère de l'Intérieur
- **URL** : https://www.data.gouv.fr/fr/organizations/ministere-de-linterieur/
- **Données** : Crimes et délits par département
- **Fichier exact** : Rechercher "crimes délits par région" 2017-2022
- **Format** : CSV (généralement)
- **Variante** : Base Nationale de Criminalité (BNC)
  - https://www.interieur.gouv.fr/Interieur/Nos-politiques/Securite-publique
- **Variables** : 
  - Cambriolages de résidences principales
  - Cambriolages résidences secondaires
- **Clé de fusion** : Code département

### Alternative (Data.gouv) :
- https://www.data.gouv.fr/
- Rechercher "statistiques police" + année

---

## 6️⃣ RÉSULTATS ÉLECTORAUX 2022
**Variable cible pour prédiction**

### Source officielle : Ministère de l'Intérieur
- **URL** : https://www.interieur.gouv.fr/
- **Élections concernées** : Élections législatives 2022 (juin)
- **Format** : CSV disponible sur le site
- **Variables clés** :
  - Parti/Candidat gagnant par circonscription
  - Nombre de voix
  - % votes exprimés
- **Niveau géographique** : Circonscription législative
  - **À convertir** en département si nécessaire (regrouper résultats)

### Alternative : Data.gouv
- https://www.data.gouv.fr/fr/datasets/resultats-des-elections-legislatives-2022-par-circonscription/
- Fichier prêt à télécharger

### Regrouper par département :
```
vote_majoritaire_dept = mode(votes_par_circonscription_dept)
```

---

## 7️⃣ RÉSULTATS ÉLECTORAUX 2017
**Comparaison temporelle 2017 vs 2022**

### Source officielle : Ministère de l'Intérieur
- **URL** : https://www.interieur.gouv.fr/
- **Élections concernées** : Élections législatives 2017 (juin)
- **Format** : CSV
- **Même méthodologie que 2022**

### Alternative : Data.gouv
- https://www.data.gouv.fr/
- Rechercher "élections législatives 2017"

---

## 8️⃣ % TERRES AGRICOLES
**Profil rural/urbain → orientations politiques**

### Source principale : Teruti-Lucas (Ministère de l'Agriculture)
- **URL** : https://www.data.gouv.fr/fr/datasets/occupation-des-terres-teruti-lucas/
- **Données** : Occupation du sol (Teruti-Lucas)
- **Variables clés** :
  - Surface terre agricole
  - Surface terres labourées
  - Prairies permanentes
- **Format** : Fichier GeoDB ou shapefile avec statistiques
- **Période** : Données multi-années (2010, 2015, 2018, 2021...)
- **À calculer** :
  ```
  % terre_agricole = (Surface_agricole / Surface_totale_dept) * 100
  ```

### Alternative (SAU - Superficie Agricole Utile)
- INSEE : Données d'activités agricoles
- https://www.insee.fr/fr/statistics (rechercher SAU)

---

## 9️⃣ TAUX RÉSIDENCES SECONDAIRES
**Profil population, stabilité électorale**

### Source principale : Fichier Foncier (DGFiP)
- **URL** : https://www.data.gouv.fr/fr/datasets/fichier-foncier-donnees-de-valeur-fonciere/
- **Plateformes** : 
  - https://www.data.gouv.fr/
  - https://www.etalab.gouv.fr/
- **Variables** : Résidences secondaires par département
- **Format** : CSV/JSON
- **Données** : Registre foncier national (transactions 2017-2022)
- **À calculer** :
  ```
  % résidences_secondaires = (Nombre_residences_secondaires / Total_logements) * 100
  ```

### Alternative (Orpi, SeLoger API)
- APIs immobilières (requièrent clés API)
- Non recommandé pour POC

---

## 🔟 PART LOGEMENTS SOCIAUX
**Politique urbaine, votes sociaux**

### Source principale : SNCF & Base Immobilière
- **URL 1** : https://www.data.gouv.fr/fr/datasets/logements-sociaux/
- **URL 2** : https://www.data.gouv.fr/
- **Données** : Stock de logements sociaux par région/département
- **Variante** : Directement sur sites gouvernementaux
  - https://www.cohesion-territoires.gouv.fr/
  - https://www.anil.org/
- **Variables** :
  - Nombre logements HLM/sociaux
  - % stock logements sociaux
- **Format** : CSV
- **À calculer** :
  ```
  % logements_sociaux = (Logements_HLM / Total_logements) * 100
  ```

### Alternative (Ministère Logement)
- https://www.cohesion-territoires.gouv.fr/logements-sociaux

---

## 📊 TABLEAU RÉCAPITULATIF SOURCES

| # | Indicateur | Source Principale | Lien | Format |
|---|-----------|-------------------|------|--------|
| 1 | Revenu médian | INSEE | INSEE.fr | CSV |
| 2 | Taux chômage | INSEE | INSEE.fr | CSV |
| 3 | Âge moyen | INSEE (RP) | INSEE.fr | CSV |
| 4 | Diplôme moyen | INSEE | INSEE.fr | CSV |
| 5 | Cambriolages | Min Intérieur | data.gouv.fr | CSV |
| 6 | Vote 2022 | Min Intérieur | interieur.gouv.fr | CSV |
| 7 | Vote 2017 | Min Intérieur | interieur.gouv.fr | CSV |
| 8 | % Terres agri | Teruti-Lucas | data.gouv.fr | GeoJSON |
| 9 | % Résidences 2air | Foncier (DGFiP) | data.gouv.fr | CSV |
| 10 | % Logements sociaux | Min Logement | data.gouv.fr | CSV |

---

## ⚙️ ÉTAPES DE RÉCUPÉRATION

### Semaine 1 - Préparation & Identification
- [ ] Visiter chaque site source (INSEE, data.gouv.fr, Min Intérieur)
- [ ] Identifier fichiers exacts à télécharger
- [ ] Vérifier disponibilité données 2017-2022
- [ ] Créer liste de téléchargements avec liens

### Semaine 2 - Téléchargement
- [ ] Télécharger tous CSV / fichiers
- [ ] Sauvegarder dans `/data/raw/`
- [ ] Documenter source + date téléchargement dans metadata.txt

### Semaine 3 - Validation
- [ ] Vérifier format + colonnes chaque fichier
- [ ] Convertir GeoDB/Shapefiles en CSV si nécessaire
- [ ] Valider clés de fusion (code département)
- [ ] Identifier données manquantes

### Semaine 4 - Nettoyage (Pandas)
- [ ] Importer tous CSV
- [ ] Standardiser colonnes
- [ ] Gérer NaN
- [ ] Fusionner par département
- [ ] Exporter données nettoyées

---

## 🔒 NOTES RGPD/CONFORMITÉ

✅ **Données publiques** : Toutes les sources listées sont publiques et légales  
✅ **Niveau géographique** : Département (pas de données nominatives)  
✅ **Anonymisation** : Aucune donnée personnelle (agrégations 100%)  
✅ **Libre utilisation** : Conformes licences Open Data (ODbL, Etalab)

---

**Dernière mise à jour** : 2 mars 2026  
**Statut** : À compléter avec liens directs des fichiers
