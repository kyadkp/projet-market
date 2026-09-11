import os
import sys
import webbrowser
import threading

from waitress import serve


if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))


os.environ.setdefault(
    "DJANGO_SETTINGS_MODULE",
    "gestionmarche.settings"
)


import django
django.setup()


# Appliquer automatiquement les migrations au démarrage
# afin que la base de données soit toujours compatible
# avec la version actuelle de l'application.
from django.core.management import call_command

call_command(
    "migrate",
    interactive=False,
    verbosity=0
)


from gestionmarche.wsgi import application


def ouvrir_navigateur():
    webbrowser.open("http://127.0.0.1:8000")


print("Gestion du Marché démarre...")


threading.Timer(
    3,
    ouvrir_navigateur
).start()


serve(
    application,
    host="127.0.0.1",
    port=8000
)