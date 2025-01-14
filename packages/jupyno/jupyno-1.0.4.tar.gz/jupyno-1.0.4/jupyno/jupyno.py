#############################################################################################################
# Modules utilisés
#############################################################################################################
from platform import system
from os import remove
from os.path import isfile
from subprocess import run
from re import search
from IPython.core.magic import register_cell_magic
from IPython.core.display import display_javascript

#############################################################################################################
# Arduino-cli
#############################################################################################################
# Fonctionnement avec les différents OS
sys = system().lower()
if sys == 'windows':
    arduino_cli = 'arduino-cli.exe'
else:
    arduino_cli = './arduino-cli'
    
# Verification que arduino-cli est bien présent dans le dossier du notebook, sinon tentative de téléchargement
if not isfile(arduino_cli):
    if sys == 'windows': # windows
        url = 'https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Windows_64bit.zip'
        file = 'arduino-cli.zip'       
    elif sys == 'linux': # linux
        url = 'https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_Linux_64bit.tar.gz'
        file = 'arduino-cli.tar.gz'
    elif sys == 'darwin': # macOS
        url = 'https://downloads.arduino.cc/arduino-cli/arduino-cli_latest_macOS_64bit.tar.gz'
        file = 'arduino-cli.tar.gz'
    # téléchargement
    try:
        import urllib
        urllib.request.urlretrieve(url, file)
    except: # si le téléchargement échoue, lève une exception
        raise ImportError("Ce module nécessite arduino-cli pour fonctionner. Veuillez l'ajouter dans le même dossier que le notebook.")
    # extraction de l'archive compressée
    if 'zip' in file: # windows
        import zipfile
        with zipfile.ZipFile(file, 'r') as myzip:
            myzip.extractall()
    else: # linux et macOS
        import tarfile
        with tarfile.open(file, 'r:gz') as mytar:
            mytar.extractall()
    # suppression de l'archive compressée
    remove(file)

# Nouveau test de présence de arduino-cli
if not isfile(arduino_cli): # si pas présent, lève une exception
    raise ImportError("Ce module nécessite arduino-cli pour fonctionner. Veuillez l'ajouter dans le même dossier que le notebook.")        

# Fichier de configuration
run([arduino_cli, 'config', 'init'], capture_output=True, text=True).stdout

############################################################################################################# 
# Fonctions pour trouver Arduino, créer un croquis, le téléverser, et rechercher et installer une librairie
#############################################################################################################
# Fonction pour trouver automatiquement la carte Arduino
def trouver_arduino() -> (str, str):
    """Trouve la carte Arduino et renvoie le port COM et le FQBN (Fully Qualified Board Name) de la carte."""
    print("Veuillez patienter...", end='')
    # détection automatique de la carte avec port, FQBN et core
    run([arduino_cli, 'core','update-index'], capture_output=True, text=True).stdout
    cartes = run([arduino_cli, 'board', 'list'], capture_output=True, text=True).stdout
    arduino = search('.+arduino.+\n', cartes)
    if arduino is None: # si pas de carte trouvée
        print("la carte n'a été pas trouvée. :( Vérifiez qu'elle est bien branchée.")
        return None, None
    arduino = arduino.group().strip().split()
    port, FQBN, core = arduino[0], arduino[-2], arduino[-1]
    
    # core de la carte installé ?
    core_list = run([arduino_cli, 'core', 'list'], capture_output=True, text=True).stdout
    if search(core, core_list) is None:
        # installation du core
        core_install = run([arduino_cli, 'core', 'install', core], capture_output=True, text=True)
        if core_install.stderr: # si erreur lors de l'installation
            print("Erreur lors de l'installation du core de la carte :")
            print()
            print(core_install.stderr.strip())
            return None, None
        # vérification
        core_list = run([arduino_cli, 'core', 'list'], capture_output=True, text=True).stdout
        if search(core, core_list) is None: 
            print("il y a un problème avec la core de la carte ! :(") 
            return None, None
    print("la carte a été trouvée ! :)")
    return port, FQBN

# Fonction pour créer un nouveau croquis
def creer_croquis(nom: str) -> str:
    """Crée un nouveau croquis et renvoie le chemin vers ce croquis."""
    croquis = run([arduino_cli, 'sketch', 'new', nom], capture_output=True, text=True)
    if croquis.stderr and search('invalid sketch name', croquis.stderr):
        print(f"'{nom}' est un nom de croquis invalide.")
        return None
    elif croquis.stderr and search('file already exists', croquis.stderr):
        print(f"Croquis '{nom}' déjà existant.")
    elif croquis.stderr:
        print(f"Erreur lors de la création du croquis '{nom}' : '")
        print()
        print(croquis.stderr.strip())
    else:
        print(f"Croquis '{nom}' créé.")
    return f'./{nom}/{nom}.ino'

# Fonction pour compiler et transférer (=téléverser) un croquis dans la carte Arduino
def televerser(croquis: str, port: str, FQBN: str) -> None:
    """Compilation et transfère du croquis 'croquis' dans la carte Arduino connecté au port COM 'port' et de FQBN 'FQBN'."""
    # compilation
    compilation = run([arduino_cli, 'compile', '--fqbn', FQBN, croquis], capture_output=True, text=True)
    if compilation.stderr:
        print("Une erreur s'est produite lors de la compilation : ")
        print()
        print(compilation.stderr.strip())
        return
    # transfère dans l'Arduino
    upload = run([arduino_cli, 'upload', '-p', port, '--fqbn', FQBN, croquis], capture_output=True, text=True)
    if upload.stderr:
        print("Une erreur s'est produite lors du transfère du programme dans l'Arduino : ")
        print()
        print(upload.stderr.strip())
    else:
        print("Téléversement réussi ! :)")
        
# Fonction pour afficher les librairies déjà installées
def liste_librairies(output: bool=False) -> None or str:
    """Affiche la liste des librairies déjà installées sur l'ordinateur.
    Le paramètre optionnel 'output' permet de renvoyer le résultat au lieu de l'afficher."""
    liste = run([arduino_cli, 'lib', 'list'], capture_output=True, text=True).stdout.strip()
    if output:
        # renvoie la liste
        return liste
    else:
        # affiche la liste
        print(liste)

# Fonction pour rechercher une librairie à partir d'un mot clé
def rechercher_librairie(mot_cle: str) -> None:
    """Recherche une librairie Arduino avec le mot clé 'mot_cle'."""
    # update la liste des librairies
    run([arduino_cli, 'lib', 'update-index'], capture_output=True, text=True).stdout
    # recherche la librairie
    res = run([arduino_cli, 'lib', 'search', mot_cle], capture_output=True, text=True)
    if not res.stderr:
        print(res.stdout.strip())
    else:
        print(f"Une erreur s'est produite lors de le recherche de {mot_cle} : ")
        print()
        print(res.stderr.strip())
        
# Fonction pour installer une librairie
def installer_librairie(librairie: str) -> None:
    """Installe la librairie 'librairie'. Si 'librairie' termine par '.zip' l'installation se fait à partir 
    du fichier zip. Par défaut, le fichier doit être dans le même dossier que le notebook. Sinon, il faut 
    expliciter le chemin d'accès."""
    if librairie[-4:] == '.zip': # si .zip
        # avertissement
        while True:
            rep = input("Attention, l'installation à partir d'un fichier .zip est à vos risques et périls. Souhaitez-vous continuer ? [O/N] ").lower()
            if rep == 'o':
                # mise à jour du fichier de configuration pour autoriser l'installer à partir d'un zip
                run([arduino_cli, 'config', 'set', 'library.enable_unsafe_install', 'true'], capture_output=True, text=True).stdout
                break
            elif rep =='n':
                print(f"La librairie {librairie} n'a pas été installée.")
                return
        # installation
        install = run([arduino_cli, 'lib', 'install', '--zip-path', librairie], capture_output=True, text=True)
        # remise à jour du fichier du configuration 
        run([arduino_cli, 'config', 'set', 'library.enable_unsafe_install', 'false'], capture_output=True, text=True).stdout
    else: # sinon
        # installation
        install = run([arduino_cli, 'lib', 'install', librairie], capture_output=True, text=True)
    # affiche le résultat
    if install.stderr: 
        print(f"Une erreur s'est produite lors de l'installation de la librairie {librairie} :")
        print()
        print(install.stderr.strip())
    else:
        print(f"La librairie {librairie} a été installée avec succès ! :)")

# Fonction pour désinstaller une librairie déjà installée
def supprimer_librairie(librairie: str) -> None:
    """Désinstalle la librairie 'librairie'."""
    # désinstallation
    uninstall = run([arduino_cli, 'lib', 'uninstall', librairie], capture_output=True, text=True)
    if uninstall.stderr:
        print(f"Une erreur s'est produite lors de la désinstallation de la librairie {librairie} :")
        print()
        print(uninstall.stderr.strip())
    else:
        print(f"La librairie {librairie} a été désinstallée avec succès ! :)") 
        
# Fonction pour exécuter une commande quelconque de arduino-cli
def commande(*cmd: str, output: bool=False) -> None or str:
    """Exécute une commande arduino-cli. 'cmd' est une séquence d'arguments.
    Le paramètre optionnel 'output' permet de renvoyer le résultat au lieu de l'afficher.
    Liste des commandes : https://arduino.github.io/arduino-cli/latest/commands/arduino-cli/"""
    res = run([arduino_cli, *cmd], capture_output=True, text=True)
    if res.stderr:
        if output:
            # renvoie l'erreur
            return res.stderr.strip()
        else:
            # affiche l'erreur
            print(f"Une erreur s'est produite lors de l'exécution de la commande :")
            print()
            print(res.stderr.strip())
    elif res.stdout:
        if output:
            # renvoie le résultat
            return res.stdout.strip()
        else:
            # affiche le résultat
            print(res.stdout.strip())
    
#############################################################################################################
# Commande magique pour écrire un croquis dans une cellule avec la coloration syntaxique du C++
#############################################################################################################
# Création de la commande magique
@register_cell_magic
def ecrire_croquis(line, cell):
    """Commande magique pour écrire le croquis dans le fichier."""
    if line[-4:] == '.ino':
        try:
            with open(line, 'w') as f:
                f.write(cell.strip())
            print("Croquis écrit avec succès.")
            return
        except:
            pass
    print("Échec de l'écriture du croquis.")
# Coloration syntaxique C++
display_javascript("IPython.CodeCell.options_default.highlight_modes['text/x-c++src'] = {'reg':[/^%%ecrire_croquis/]};", raw=True)
