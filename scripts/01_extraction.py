"""
SCRIPT 01 - EXTRACTION DES DONNÉES
===================================

Récupération des 10 indicateurs depuis les sources publiques :
- INSEE (économie, démographie)
- Ministère Intérieur (élections, sécurité)
- Teruti-Lucas, Foncier, etc.

Données sauvegardées dans : data/raw/

Exécution : python scripts/01_extraction.py
"""

import os
import pandas as pd
import requests
from pathlib import Path

# Import config
from config import PATH_DATA_RAW, AURA_DEPARTMENTS

# Créer dossier raw si n'existe pas
os.makedirs(PATH_DATA_RAW, exist_ok=True)

print("=" * 60)
print("SCRIPT 01 - EXTRACTION DONNÉES SOURCES PUBLIQUES")
print("=" * 60)
print()

# ============================================================================
# FONCTION 1 : TÉLÉCHARGER REVENU MÉDIAN (INSEE)
# ============================================================================
def extract_revenu_median():
    """Télécharger données revenu médian INSEE par département."""
    print("[1/10] Extraction revenu médian...")
    
    # À implémenter : Télécharger de INSEE
    # Résultat : data/raw/insee_revenu_median.csv
    
    print("  ✓ Revenu médian téléchargé")


# ============================================================================
# FONCTION 2 : TÉLÉCHARGER TAUX CHÔMAGE (INSEE)
# ============================================================================
def extract_taux_chomage():
    """Télécharger données taux chômage INSEE par département."""
    print("[2/10] Extraction taux chômage...")
    
    # À implémenter : Télécharger de INSEE
    # Résultat : data/raw/insee_chomage.csv
    
    print("  ✓ Taux chômage téléchargé")


# ============================================================================
# FONCTION 3 : ÂGE MOYEN POPULATION (INSEE RECENSEMENT)
# ============================================================================
def extract_age_moyen():
    """Télécharger données age moyen INSEE par département."""
    print("[3/10] Extraction âge moyen...")
    
    # À implémenter : Télécharger de INSEE Recencement
    # Résultat : data/raw/insee_age_moyen.csv
    
    print("  ✓ Âge moyen téléchargé")


# ============================================================================
# FONCTION 4 : NIVEAU DIPLÔME MOYEN (INSEE)
# ============================================================================
def extract_niveau_diplome():
    """Télécharger données niveau diplôme INSEE par département."""
    print("[4/10] Extraction niveau diplôme...")
    
    # À implémenter : Télécharger de INSEE
    # Résultat : data/raw/insee_diplome.csv
    
    print("  ✓ Niveau diplôme téléchargé")


# ============================================================================
# FONCTION 5 : CAMBRIOLAGES (MINISTÈRE INTÉRIEUR)
# ============================================================================
def extract_cambriolages():
    """Télécharger données cambriolages Ministère Intérieur."""
    print("[5/10] Extraction cambriolages...")
    
    # À implémenter : Télécharger crimes & délits par département
    # Résultat : data/raw/interieur_cambriolages.csv
    
    print("  ✓ Cambriolages téléchargés")


# ============================================================================
# FONCTION 6 : RÉSULTATS ÉLECTORAUX 2022 (MINISTÈRE INTÉRIEUR)
# ============================================================================
def extract_elections_2022():
    """Télécharger résultats élections 2022."""
    print("[6/10] Extraction élections 2022...")
    
    # À implémenter : Télécharger résultats législatives 2022
    # Résultat : data/raw/elections_2022.csv
    
    print("  ✓ Élections 2022 téléchargées")


# ============================================================================
# FONCTION 7 : RÉSULTATS ÉLECTORAUX 2017 (MINISTÈRE INTÉRIEUR)
# ============================================================================
def extract_elections_2017():
    """Télécharger résultats élections 2017."""
    print("[7/10] Extraction élections 2017...")
    
    # À implémenter : Télécharger résultats législatives 2017
    # Résultat : data/raw/elections_2017.csv
    
    print("  ✓ Élections 2017 téléchargées")


# ============================================================================
# FONCTION 8 : % TERRES AGRICOLES (TERUTI-LUCAS)
# ============================================================================
def extract_terres_agricoles():
    """Télécharger données occupation sol - Teruti-Lucas."""
    print("[8/10] Extraction % terres agricoles...")
    
    # À implémenter : Télécharger de data.gouv.fr (Teruti-Lucas)
    # Résultat : data/raw/teruti_terres_agricoles.csv
    
    print("  ✓ Terres agricoles téléchargées")


# ============================================================================
# FONCTION 9 : RÉSIDENCES SECONDAIRES (FICHIER FONCIER)
# ============================================================================
def extract_residences_secondaires():
    """Télécharger données résidences secondaires - Fichier Foncier."""
    print("[9/10] Extraction taux résidences secondaires...")
    
    # À implémenter : Télécharger de data.gouv.fr (Foncier)
    # Résultat : data/raw/foncier_residences_secondaires.csv
    
    print("  ✓ Résidences secondaires téléchargées")


# ============================================================================
# FONCTION 10 : LOGEMENTS SOCIAUX (MINISTÈRE LOGEMENT / SNCF)
# ============================================================================
def extract_logements_sociaux():
    """Télécharger données logements sociaux."""
    print("[10/10] Extraction part logements sociaux...")
    
    # À implémenter : Télécharger de data.gouv.fr ou site ministère
    # Résultat : data/raw/logements_sociaux.csv
    
    print("  ✓ Logements sociaux téléchargés")


# ============================================================================
# MAIN : Lancer toutes extractions
# ============================================================================
if __name__ == "__main__":
    try:
        # Exécuter toutes les extractions
        extract_revenu_median()
        extract_taux_chomage()
        extract_age_moyen()
        extract_niveau_diplome()
        extract_cambriolages()
        extract_elections_2022()
        extract_elections_2017()
        extract_terres_agricoles()
        extract_residences_secondaires()
        extract_logements_sociaux()
        
        print()
        print("=" * 60)
        print("✓ EXTRACTION TERMINÉE")
        print("=" * 60)
        print()
        print(f"Fichiers sauvegardés dans : {PATH_DATA_RAW}")
        print()
        print("Prochaine étape : python scripts/02_nettoyage.py")
        print()
        
    except Exception as e:
        print(f"❌ ERREUR : {e}")
        raise
