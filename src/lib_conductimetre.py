import serial
import serial.tools.list_ports
import os
import glob
import csv
import time
from datetime import datetime
import numpy as np
from scipy import interpolate
import matplotlib.pyplot as plt
from sklearn.metrics import r2_score


###############################################
#
# ACCES ARDUINO
#
###############################################

def port_connexion(br = 9600 , portIN = '') :
    """
    Établit la connexion au port série.

    Parameters
    ----------
    br : int
        Flux de données en baud.
    portIN : string
        Identifiant du port série sur lequel le script doit lire des données.

    Returns
    -------
    port : string
        Identifiant du port série sur lequel le script doit lire des données.
    s : serial.tools.list_ports_common.ListPortInfo / string
        Objet Serial sur lequel on peut appliquer des fonctions d'ouverture, de lecture et de fermeture du port série affilié. En cas d'échec de connexion, 's' sera une chaîne de caractères "erreur".

    """

    #arduino_list=['0x7fa89e971690']
#remplacer par la liste des numéros de série des cartes arduinos des conductimètres 
    if portIN == '' :
        ports = list(serial.tools.list_ports.comports())
    else :
        ports = [portIN]  
    i = 0 
    conn = False
    while conn == False :
        try :
            port = ports[i] 
            if portIN == '' and (port.manufacturer == 'Arduino (www.arduino.cc)' or port.serial_number in arduino_list ):
                port = port.device
                port = (port).replace('cu','tty')
                s = serial.Serial(port=port, baudrate=br, timeout=5) 
                conn = True  
                print('Connexion établie avec le port', port)
            else :
                s = serial.Serial(port=port, baudrate=br, timeout=5)
                conn = True
                print('Connexion établie avec le port', port)
        except :
            i += 1
            if i >= len(ports) :
                print("/!\ Port de connexion non détecté. Merci de rétablir la connexion non établie : connexion au processeur dans les réglages avant utilisation.")
                s = 'error' 
                portIN = '' 
                conn = True
            pass     
    return port , s
    
###################################
    
    
def fn_settings(portIN , s , br , nb_inter , time_inter) :
    """
    Configuration des paramètres modifiables par l'utilisateur.

    Parameters
    ----------
    portIN : string
        Identifiant du port série sur lequel le script doit lire des données.
    s : serial.tools.list_ports_common.ListPortInfo
        Objet Serial sur lequel on peut appliquer des fonctions d'ouverture, de lecture et de fermeture du port série affilié.
    br : int
        Flux de données en baud.
    nb_inter : int
        Nombre de valeurs utilisées pour constituer une mesure (une mesure correspond à la moyenne de toutes les valeurs prélevées).
    time_inter : float
        Temps d'intervalle entre chaque prélèvement de valeur au sein d'une mesure.

    Returns
    -------
    portIN : string
        Identifiant du port série sur lequel le script doit lire des données.
    s : serial.tools.list_ports_common.ListPortInfo
        Objet Serial sur lequel on peut appliquer des fonctions d'ouverture, de lecture et de fermeture du port série affilié.
    br : int 
        Flux de données en baud.
    nb_inter : int
        Nombre de valeurs utilisées pour constituer une mesure (une mesure correspond à la moyenne de toutes les valeurs prélevées).
    time_inter : float
        Temps d'intervalle entre chaque prélèvement de valeur au sein d'une mesure.

    """
    
    print("Configurer le port de connexion : P \nChanger le flux (baudrate) : B \nChanger le temps et la fréquence de mesure : T")
    setting = input('>>> ')
    if setting == 'P' or setting == 'p':
        print('Saisissez le chemin du port (pour tester toutes les connexions périphériques de l\'ordinateur, laissez le champ vide)')
        port_name = input('>>> ')
        try :
            portIN , s = port_connexion(br, port_name)
        except Exception as inst :
            print("/!\ Echec de l'opération.")
            print('Erreur :',inst)
            pass
    elif setting == 'B' or setting == 'b' :
        try :
            br = int(input('Saisissez le nouveau baudrate : '))
            portIN , s = port_connexion(br, portIN)
            print('Paramètre enregistré.')
        except :
            print('/!\ Saisie invalide.')
            pass
    elif setting == 'T' or setting == 't' :
        try :
            time_measurement = float(input('Saisissez la durée d\'une mesure (sec) : '))
            nb_inter = int(input('Saisissez le nombres de valeurs composant une mesure : '))
            time_inter = time_measurement / nb_inter
            print("Une mesure comprend désormais ",nb_inter," valeurs, espacées entre elles de ",time_inter," secondes.\n")
        except :
            print('/!\ Saisie invalide.')
            pass
    else :
        print('/!\ Saisie invalide.')
    return portIN , s, br , nb_inter , time_inter


