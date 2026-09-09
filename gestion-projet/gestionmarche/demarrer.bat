@echo off

cd /d "%~dp0"

echo Activation de l'environnement...

call venv\Scripts\activate.bat

echo Demarrage de Gestion du Marche...

python lancer_application.py

pause