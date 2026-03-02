#!/bin/bash
# Script installation environnement MSPR1
# Linux / Mac

echo "==============================================="
echo "MSPR1 - Installation Environnement Python"
echo "==============================================="

# 1. Créer environnement virtuel
echo ""
echo "[1/4] Création environnement virtuel Python..."
python3 -m venv venv
if [ $? -ne 0 ]; then
    echo "ERREUR : Python3 non trouvé. Vérifie installation Python 3.8+"
    exit 1
fi

# 2. Activer environnement
echo "[2/4] Activation environnement virtuel..."
source venv/bin/activate

# 3. Mettre à jour pip
echo "[3/4] Mise à jour pip..."
python -m pip install --upgrade pip

# 4. Installer dépendances
echo "[4/4] Installation dépendances (requirements.txt)..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "ERREUR : Échec installation dépendances"
    exit 1
fi

echo ""
echo "==============================================="
echo "SUCCESS! Environnement configuré"
echo "==============================================="
echo ""
echo "Prochaines étapes :"
echo "1. Activer environnement : source venv/bin/activate"
echo "2. Vérifier Python : python --version"
echo "3. Vérifier pandas : python -c 'import pandas; print(pandas.__version__)'"
echo ""
