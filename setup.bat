@echo off
REM Script installation environnement MSPR1
REM Windows PowerShell ou CMD

echo ===============================================
echo MSPR1 - Installation Environnement Python
echo ===============================================

REM 1. Créer environnement virtuel
echo.
echo [1/4] Creation environnement virtuel Python...
python -m venv venv
if %ERRORLEVEL% NEQ 0 (
    echo ERREUR : Python non trouve. Verifie installation Python 3.8+
    pause
    exit /b 1
)

REM 2. Activer environnement
echo [2/4] Activation environnement virtuel...
call venv\Scripts\activate.bat

REM 3. Mettre à jour pip
echo [3/4] Mise a jour pip...
python -m pip install --upgrade pip

REM 4. Installer dépendances
echo [4/4] Installation dependances (requirements.txt)...
pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo ERREUR : Echec installation dependances
    pause
    exit /b 1
)

echo.
echo ===============================================
echo SUCCESS! Environnement configure
echo ===============================================
echo.
echo Prochaines etapes :
echo 1. Activer environnement : venv\Scripts\activate
echo 2. Verifier Python : python --version
echo 3. Verifier pandas : python -c "import pandas; print(pandas.__version__)"
echo.
pause
