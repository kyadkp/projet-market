import webbrowser
import threading
from waitress import serve
from gestionmarche.wsgi import application


def ouvrir_navigateur():
    webbrowser.open("http://127.0.0.1:8000")


print("Démarrage de Gestion du Marché...")

# Ouvre le navigateur après 2 secondes
threading.Timer(2, ouvrir_navigateur).start()

serve(application, host="127.0.0.1", port=8000)