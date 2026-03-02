-- ========================================================================
-- SCHEMA BASE DE DONNÉES MSPR1 - ÉLECTIONS AURA
-- PostgreSQL
-- ========================================================================

-- ========================================================================
-- TABLE 1 : DÉPARTEMENTS
-- ========================================================================
CREATE TABLE IF NOT EXISTS departements (
    id_dept SERIAL PRIMARY KEY,
    code_dept VARCHAR(2) UNIQUE NOT NULL,
    nom_dept VARCHAR(100) NOT NULL,
    region VARCHAR(50) NOT NULL,
    population_2022 INTEGER,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO departements (code_dept, nom_dept, region) VALUES
('01', 'Ain', 'Auvergne Rhône-Alpes'),
('03', 'Allier', 'Auvergne Rhône-Alpes'),
('07', 'Ardèche', 'Auvergne Rhône-Alpes'),
('15', 'Cantal', 'Auvergne Rhône-Alpes'),
('26', 'Drôme', 'Auvergne Rhône-Alpes'),
('38', 'Isère', 'Auvergne Rhône-Alpes'),
('42', 'Loire', 'Auvergne Rhône-Alpes'),
('43', 'Haute-Loire', 'Auvergne Rhône-Alpes'),
('63', 'Puy-de-Dôme', 'Auvergne Rhône-Alpes'),
('69', 'Rhône', 'Auvergne Rhône-Alpes'),
('73', 'Savoie', 'Auvergne Rhône-Alpes'),
('74', 'Haute-Savoie', 'Auvergne Rhône-Alpes');

-- ========================================================================
-- TABLE 2 : RÉSULTATS ÉLECTORAUX
-- ========================================================================
CREATE TABLE IF NOT EXISTS elections (
    id_election SERIAL PRIMARY KEY,
    id_dept INTEGER NOT NULL REFERENCES departements(id_dept) ON DELETE CASCADE,
    annee INTEGER NOT NULL,
    vote_majoritaire VARCHAR(100),
    score_pct DECIMAL(5, 2),
    nb_votes INTEGER,
    participation_pct DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_election UNIQUE(id_dept, annee)
);

CREATE INDEX idx_elections_dept ON elections(id_dept);
CREATE INDEX idx_elections_annee ON elections(annee);

-- ========================================================================
-- TABLE 3 : INDICATEURS ÉCONOMIQUES & SOCIAUX
-- ========================================================================
CREATE TABLE IF NOT EXISTS indicateurs (
    id_indicateur SERIAL PRIMARY KEY,
    id_dept INTEGER NOT NULL REFERENCES departements(id_dept) ON DELETE CASCADE,
    annee INTEGER NOT NULL,
    
    -- Économie
    revenu_median DECIMAL(10, 2),
    taux_chomage DECIMAL(5, 2),
    nb_entreprises INTEGER,
    
    -- Démographie
    age_moyen DECIMAL(4, 2),
    population_total INTEGER,
    
    -- Education
    niveau_diplome_bac_plus_pct DECIMAL(5, 2),
    
    -- Logement
    pct_logements_sociaux DECIMAL(5, 2),
    taux_residences_secondaires DECIMAL(5, 2),
    
    -- Activité économique
    pct_terres_agricoles DECIMAL(5, 2),
    
    -- Sécurité
    nb_cambriolages INTEGER,
    
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT unique_indicateur UNIQUE(id_dept, annee)
);

CREATE INDEX idx_indicateurs_dept ON indicateurs(id_dept);
CREATE INDEX idx_indicateurs_annee ON indicateurs(annee);

-- ========================================================================
-- TABLE 4 : CLUSTERS K-MEANS
-- ========================================================================
CREATE TABLE IF NOT EXISTS clusters (
    id_cluster SERIAL PRIMARY KEY,
    id_dept INTEGER NOT NULL REFERENCES departements(id_dept) ON DELETE CASCADE,
    cluster_id INTEGER NOT NULL,
    cluster_label VARCHAR(100),
    profil_description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_cluster UNIQUE(id_dept)
);

CREATE INDEX idx_clusters_dept ON clusters(id_dept);
CREATE INDEX idx_clusters_id ON clusters(cluster_id);

-- ========================================================================
-- TABLE 5 : PRÉDICTIONS RANDOM FOREST
-- ========================================================================
CREATE TABLE IF NOT EXISTS predictions (
    id_prediction SERIAL PRIMARY KEY,
    id_dept INTEGER NOT NULL REFERENCES departements(id_dept) ON DELETE CASCADE,
    annee_prediction INTEGER NOT NULL,
    vote_predict VARCHAR(100),
    confidence_score DECIMAL(5, 4),
    intervalle_confiance_min DECIMAL(5, 2),
    intervalle_confiance_max DECIMAL(5, 2),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT unique_prediction UNIQUE(id_dept, annee_prediction)
);

CREATE INDEX idx_predictions_dept ON predictions(id_dept);
CREATE INDEX idx_predictions_annee ON predictions(annee_prediction);

-- ========================================================================
-- VUES UTILES POUR GRAFANA
-- ========================================================================

-- Vue : Comparaison historique vs prédictions
CREATE OR REPLACE VIEW v_elections_vs_predictions AS
SELECT 
    d.code_dept,
    d.nom_dept,
    e.annee,
    e.vote_majoritaire,
    e.score_pct as score_historique,
    p.vote_predict,
    p.confidence_score,
    'Historique' as type_donnee
FROM elections e
JOIN departements d ON e.id_dept = d.id_dept
LEFT JOIN predictions p ON e.id_dept = p.id_dept AND e.annee = p.annee_prediction
ORDER BY d.code_dept, e.annee;

-- Vue : Indicateurs par département et année
CREATE OR REPLACE VIEW v_indicateurs_complets AS
SELECT 
    d.code_dept,
    d.nom_dept,
    i.annee,
    i.revenu_median,
    i.taux_chomage,
    i.age_moyen,
    i.niveau_diplome_bac_plus_pct,
    i.pct_logements_sociaux,
    i.taux_residences_secondaires,
    i.pct_terres_agricoles,
    i.nb_cambriolages,
    c.cluster_label,
    e.vote_majoritaire
FROM indicateurs i
JOIN departements d ON i.id_dept = d.id_dept
LEFT JOIN clusters c ON i.id_dept = c.id_dept
LEFT JOIN elections e ON i.id_dept = e.id_dept AND i.annee = e.annee
ORDER BY d.code_dept, i.annee DESC;

-- Vue : Résumé statistiques par département
CREATE OR REPLACE VIEW v_resume_departements AS
SELECT 
    d.code_dept,
    d.nom_dept,
    ROUND(AVG(i.revenu_median), 0) as revenu_median_moyen,
    ROUND(AVG(i.taux_chomage), 2) as taux_chomage_moyen,
    ROUND(AVG(i.age_moyen), 1) as age_moyen,
    ROUND(AVG(i.niveau_diplome_bac_plus_pct), 1) as diplome_moyen,
    COUNT(DISTINCT e.annee) as nb_annees_elections,
    MAX(e.annee) as derniere_election
FROM departements d
LEFT JOIN indicateurs i ON d.id_dept = i.id_dept
LEFT JOIN elections e ON d.id_dept = e.id_dept
GROUP BY d.id_dept, d.code_dept, d.nom_dept
ORDER BY d.code_dept;

-- ========================================================================
-- PERMISSIONS (si utilisateur différent de créateur)
-- ========================================================================
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO grafana_user;
-- GRANT SELECT ON ALL TABLES IN SCHEMA public TO app_user;

-- ========================================================================
-- COMMENTAIRES
-- ========================================================================
COMMENT ON TABLE departements IS 'Liste des 12 départements AURA';
COMMENT ON TABLE elections IS 'Résultats électoraux historiques 2017-2022';
COMMENT ON TABLE indicateurs IS 'Indicateurs économiques, sociaux et démographiques';
COMMENT ON TABLE clusters IS 'Résultats clustering K-Means';
COMMENT ON TABLE predictions IS 'Prédictions Random Forest pour 2023-2026';

-- ========================================================================
-- FIN SCHÉMA
-- ========================================================================
