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
 
#########################################################
#
# FONCTIONS DE CALIBRATION 
#
#########################################################

def Etalonnage(nbr_etalon, nbr_mesure_par_etalon):
    '''
    Fonction qui, pour le nombre d'étalon indiqué en argument, mesure la tension, trouve la corrélation entre Tension et conductivité, puis trace le graphique et renvoie la droite d'étalonnage

    Parameters
    ----------
    nbr_etalon : int
        Nombre d'étalon pour l'étalonnage.
    nbr_mesure_par_etalon : int
        Nombre de mesure à faire pour chaque étalon.

    Returns
    -------
    droite : numpy.poly1d
        Droite d'étalonnage sous la forme ax + b.

    '''
    conductimeter = setup()
    list_tension = []
    list_conductivite=[]
    
    #Correction de la conductivité par la température 
    Temperature = [0,5,10,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31]
    Conductivite_12880 = [7150,8220,9330,10480,10720,10950,11190,11430,11670,11910,12150,12390,12640,12880,13130,13370,13620,13870,14120,14370]
    Conductivite_1413 = [776,896,1020,1147,1173,1199,1225,1251,1278,1305,1332,1359,1386,1413,1440,1467,1494,1521,1548,1575]
    Conductivite_5000 = [2760,3180,3615,4063,4155,4245,4337,4429,4523,4617,4711,4805,4902,5000,5096,5190,5286,5383,5479,5575]

    reg_12880 = np.polyfit(Temperature,Conductivite_12880,1)
    droite_12880 = np.poly1d(reg_12880)

    reg_1413= np.polyfit(Temperature,Conductivite_1413,1)
    droite_1413 = np.poly1d(reg_1413)

    reg_5000= np.polyfit(Temperature,Conductivite_5000,1)
    droite_5000 = np.poly1d(reg_5000)
    
    for k in range(nbr_etalon):
        print('\n[ Étalon', k+1,']')
        
        conductivite = float(input('Quelle est la valeur de conductivité de votre étalon à 25°C ? (en uS/cm): '))
        if conductivite == 12880 :
            print('Remarque : Votre mesure sera corrigée avec la température mesurée dans l\'échantillon pour plus de précision.')
            input('Appuyez sur Entrée après avoir plongé le thermomètre dans la solution.')
            lect = conductimeter.readline().decode().strip('\r\n').split(',')
            T = float(lect[0])
            conductivite = droite_12880(T)
        elif conductivite == 5000 :
            print('Remarque : Votre mesure sera corrigée avec la température mesurée dans l\'échantillon pour plus de précision.')
            input('Appuyez sur Entrée après avoir plongé le thermomètre dans la solution.')
            lect = conductimeter.readline().decode().strip('\r\n').split(',')
            T = float(lect[0])
            conductivite = droite_5000(T)
        elif conductivite == 1413 :
            print('Remarque : Votre mesure sera corrigée avec la température mesurée dans l\'échantillon pour plus de précision.')
            input('Appuyez sur Entrée après avoir plongé le thermomètre dans la solution.')
            lect = conductimeter.readline().decode().strip('\r\n').split(',')
            T = float(lect[0])
            conductivite = droite_1413(T)
        else : 
            print('Remarque : Votre mesure ne pourra pas être corrigée selon la température.')
            
        input('\nAppuyez sur Entrée pour lancer la mesure.')
        list_conductivite.append(conductivite)
        list_tension_etalonnage = mesure_etalonnage(nbr_mesure_par_etalon)
        ecart_type = np.std(list_tension_etalonnage)
        print('L\'écart-type des mesures de l\'étalon est :', ecart_type,'V, un graphique s\'est aussi affiché.')
        a = input('\nEst ce que la mesure est stable ? (y/n) : ')
        moy_etalon = stabilite_mesure(a, list_tension_etalonnage, nbr_mesure_par_etalon)
        print('La conductivité de votre étalon est de', conductivite, ' uS/cm avec une tension enregistrée de ', moy_etalon, 'V pour une température de', T, '°C.')
        list_tension.append(float(moy_etalon))
        print('Cette mesure est enregistrée, passez à la suite.\n')

    plt.figure()
    plt.plot(list_tension,list_conductivite, 'o', color = 'r')
    plt.xlabel('Tension (V)')
    plt.ylabel('Conductivité (us/cm)')
    plt.axis([0, np.max(list_tension), 0, np.max(list_conductivite) +5])
    plt.title('Courbe d\'étalonnage')
    reg = np.polyfit(list_tension, list_conductivite, 1)
    droite = np.poly1d(reg)
    plt.plot(list_tension, droite[1] * np.array(list_tension) + droite[0])
    plt.show()
    
    return droite
    
def Etalonnage_existant():
    cali_dispo = sorted(glob.glob('./Nextcloud/Conductimetre/data/*12880*.csv'), key=os.path.getmtime)
    print("Calibrations disponibles:")
    for i in range(len(cali_dispo)):
        print("%i - %s" % (i, cali_dispo[i]))
    res = input("Choisissez votre calibration en entrant son numéro d'ordre: ")

    print(cali_dispo[int(res)][-28:-4])

    cali_chosen = glob.glob('./CALIB/*%s.csv' % (cali_dispo[int(res)][-28:-4]))
    
# Fonction à compléter Etalonnage_existant à compléter et à adapter à la conductivité 






     return droite 


def default_calibration() : 

    Conductivite = [12880,5000,1413]
    Tension =[] #Effectuer une série de 200 mesures et prendre la moyenne des tensions pour chaque solution étalon 

 #Correction de la conductivité par la température 
     Temperature = [0,5,10,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31]
     Conductivite_12880 = [7150,8220,9330,10480,10720,10950,11190,11430,11670,11910,12150,12390,12640,12880,13130,13370,13620,13870,14120,14370]
     Conductivite_1413 = [776,896,1020,1147,1173,1199,1225,1251,1278,1305,1332,1359,1386,1413,1440,1467,1494,1521,1548,1575]
     Conductivite_5000 = [2760,3180,3615,4063,4155,4245,4337,4429,4523,4617,4711,4805,4902,5000,5096,5190,5286,5383,5479,5575]
     
     reg12880 = np.polyfit(Temperature,Conductivite_12880,1)
     droite_12880 = np.poly1d(reg12880)
     
     
     reg1413 = np.polyfit(Temperature,Conductivite_1413,1)
     droite_1413 = np.poly1d(reg1413)
     
     
     reg5000 = np.polyfit(Temperature,Conductivite_5000,1)
     droite_5000 = np.poly1d(reg5000)
     
     Conductivite[1]= droite_12880(20)#remplacer 20 par la température moyenne de la salle dans laquelle s'effectue les manips 
     Conductivite[2]= droite_5000(20)
     Conductivite[3]= droite_1413(20)
     
     reg = np.polyfit(Tension,Conductivite_12880,1)
     droite= np.poly1d(reg)
     
     plt.figure()
     plt.plot(Tension,Conductivite)
     plt.xlabel('Tension en V')
     plt.ylabel('Conductivité en us/cm')
     plt.title('Courbe d\'étalonnage par défaut')
    
     return droite





    

    






