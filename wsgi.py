# -*- coding: utf-8 -*-
"""
Point d'entrée WSGI pour le déploiement (AlwaysData, etc.).
Expose l'application Flask sous le nom `application`.
"""
import os
import sys

# S'assurer que la racine du projet est dans le path
_racine = os.path.dirname(os.path.abspath(__file__))
if _racine not in sys.path:
    sys.path.insert(0, _racine)

from app import server

# AlwaysData (et la plupart des hébergeurs WSGI) attendent "application"
application = server
