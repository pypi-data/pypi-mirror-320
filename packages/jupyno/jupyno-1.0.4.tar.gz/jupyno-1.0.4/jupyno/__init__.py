"""
Module permettant d'écrire et de téléverser des croquis Arduino directement depuis un notebook Jupyter.
Nécessite le programme arduino-cli (https://github.com/arduino/arduino-cli) présent dans le même dossier.

Auteur : Guillaume Froehlicher

version 1.0.0 (27/02/2024) : version initiale
version 1.0.1 (25/03/2024) : - affichage des librairies déjà installées
                           - recherche et installation d'une librairie
                           - désinstallation d'une librairie
version 1.0.2 (30/03/2024) : - correction core install
                             - fonction pour exécuter une commande quelconque de arduino-cli
                             - téléchargement automatique de arduino-cli
                             - ajout d'une exception ImportError si arduino-cli manquant
version 1.0.3 (10/01/2025) : - tentative de téléchargement automatique
                             - correction des instructions avec run
                             - ajout paramètre optionnel output pour les fonctions liste_librairies et commande
version 1.0.4 (13/01/2025) : - modification du fichier __init__.py 
"""
from .jupyno import *