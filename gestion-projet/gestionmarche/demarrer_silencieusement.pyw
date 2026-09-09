import subprocess
import os
import webbrowser
import time


chemin_projet = os.path.dirname(os.path.abspath(__file__))

# Démarre le serveur
process = subprocess.Popen(
    [
        os.path.join(chemin_projet, "venv", "Scripts", "python.exe"),
        os.path.join(chemin_projet, "lancer_application.py")
    ],
    cwd=chemin_projet
)

# Attend que Django démarre
time.sleep(3)

# Ouvre le navigateur
webbrowser.open("http://127.0.0.1:8000")