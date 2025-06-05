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

def port_connexion(br = 115200 , portIN = '') :
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

    arduino_list=['7513931383135170A031','85138313034351818222','85138313633351403151','751393138313510190A0','9513832383835190A231','7513131393235121B0A1','75131313932351F08160','7513931383135110A2D1','75131313932351403012']
    #Dans l'ordre[ADNI,LOTHI,GAGAMA,BALEW,MAJUCA,AMPAPI,SOMA,ANRE,GUITERA]
    if portIN == '' :
        ports = list(serial.tools.list_ports.comports())
    else :
        ports = [portIN]  
    i = 0 
    conn = False
    while conn == False :
        try :
            port = ports[i] 
            #if portIN == '' and (port.manufacturer == 'Arduino (www.arduino.cc)' or port.serial_number in arduino_list ): (Version intiale du code )
            if portIN == '' and (port.serial_number in arduino_list ):
                port = port.device
                port = (port).replace('cu','tty')
                s = serial.Serial(port=port, baudrate=br, timeout=5) 
                conn = True  
               # print('Connexion établie avec le port', port)
            else :
                conn = False
                print('Carte Arduino non reconnue /nVeuillez vous connecter à l\'un des conductimètres reconnu par le programme', port)
        except :
            i += 1
            if i >= len(ports) :
                print("/!\ Port de connexion non détecté. Merci de rétablir la connexion non établie : connexion au processeur dans les réglages avant utilisation.")
                s = 'error' 
                portIN = '' 
                conn = True
            pass    
    return port,s

    
    
    
def fn_settings(portIN='',br =9600, nb_inter =100, time_inter=5) :
    """
    Configuration des paramètres modifiables par l'utilisateur.

    Parameters
    ----------
    portIN : string
        Identifiant du port série sur lequel le script doit lire des données.
    br : int
        Flux de données en baud.
    nb_inter : int
        Nombre de valeurs utilisées pour constituer une mesure (une mesure correspond à la moyenne de toutes les valeurs prélevées).
    time_inter : float
        Temps d'intervalle entre chaque prélèvement de valeur au sein d'une mesure.

    Returns
    -------
    s : serial.tools.list_ports_common.ListPortInfo
        Objet Serial sur lequel on peut appliquer des fonctions d'ouverture, de lecture et de fermeture du port série affilié.
    br : int 
        Flux de données en baud.
    nb_inter : int
        Nombre de valeurs utilisées pour constituer une mesure (une mesure correspond à la moyenne de toutes les valeurs prélevées).
    time_inter : float
        Temps d'intervalle entre chaque prélèvement de valeur au sein d'une mesure.

    """
    
    print(" Le flux (baudrate) actuel vaut 9600, le temps entre chaque mesure vaut 1s et la fréquence vaut 5 Hz.\nVoulez-vous ? : \n\nChanger le flux (baudrate) : B \nChanger le temps et la fréquence de mesure : T \nNe rien faire : N " )
    setting = input('>>> ')
    
    if setting == 'B' or setting == 'b' :
        try :
            br = int(input('Saisissez le nouveau baudrate : '))
            portIN= port_connexion(br, portIN)[0]
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
    elif setting == 'N' or setting == 'n' :
        pass
    else :
        print('/!\ Saisie invalide.')
    return port_connexion(br,portIN)[1]
   
 
    

#########################################################
#
# FONCTIONS DE CALIBRATION 
#
#########################################################

def mesure_etalonnage(nbr_mesure_par_etalon):   # confirmation que l'étalonnage est bon en faisant pendant x min à haute fréquence des mesures puis en les mettant sur un graphique
    '''
    Fonction permettant de faire plein de mesure à haute fréquence puis les mettant dans un graphique pour vérifier qu'elles sont stables'

    Parameters
    ----------
    nbr_mesure_par_etalon : int
        nombre de mesures par étalon, décidé dans les valeurs par défaut.

    Returns
    -------
    list_tension_etalon : list
        Liste des tensions mesurées pendant l'étalonnage.

    '''
    conductimeter = port_connexion()[1]
    list_tension_etalon = []
    list_temperature=[]
    numerotation = []
    date_today= datetime.now()
    date=date_today.strftime("%d-%m-%y")
    #date=t.replace(microsecond=0)
    print('Les mesures sont en cours, attendez s\'il vous plait.')
    conductimeter.flushInput()
    for k in range(nbr_mesure_par_etalon):
        lect = conductimeter.readline().decode().strip('\r\n').split(',')
        list_tension_etalon.append(float(lect[1]))
        list_temperature.append(float(lect[0]))
        numerotation.append(k*0.01)
        #time.sleep(0.0readline().decode().strip('\r\n').split(',')
    Temperature_etalon= np.mean(list_temperature)
    Tension_etalon=np.mean(list_tension)
        
    np.savetxt('./tension_etalonnage du %s.csv' %date,list_tension_etalon, delimiter = ';',fmt = '%.2f', header='Tensions mesurées par la sonde conductimétrique',)
    print('Vos mesures sont désormais stockées dans le fichier tension_etalonnage.csv')
  
    plt.figure()
    plt.plot(numerotation, list_tension_etalon, 'o')
    plt.xlabel('Temps (s)')
    plt.ylabel('Tension (V)')
    plt.show()
    
    
    
    
    return Tension_etalon,Temperature_etalon


def Etalonnage(nbr_etalon=2, nbr_mesure_par_etalon=200):
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
    # conductimeter = port_connexion()[1]
    list_tension = []
    list_conductivite_25=[]
    list_conductivite=[]
    date_today= datetime.now()
    date=date_today.strftime("%d-%m-%y")

    
    for k in range(nbr_etalon):
        print('\n[ Étalon', k+1,']')
        
        conductivite = float(input('Quelle est la valeur de conductivité de votre étalon à 25°C ? (en uS/cm): '))
        input('\nAppuyez sur Entrée pour lancer la mesure.')
        Tension_etalon,temperature = mesure_etalonnage(nbr_mesure_par_etalon)
        conductivite= correction_temperature(conductivite,temperature)
        print('La conductivité de votre étalon a été corrigée en tenant compte de la température. \nLa conductivité de votre solution étalon vaut :',conductivite,'\nAvec une température moyenne de',temperature,'°C')
        list_conductivite.append(conductivite)
        
        list_tension.append(Tension_etalon)
        # ecart_type = np.std(list_tension_etalonnage)
        # print('L\'écart-type des mesures de l\'étalon est :', ecart_type,'V, un graphique s\'est aussi affiché.')
        
       
        
        # a = input('\nEst ce que la mesure est stable ? (y/n) : ')
        # moy_etalon = stabilite_mesure(a, list_tension_etalonnage, nbr_mesure_par_etalon)
        # list_tension.append(float(moy_etalon))
        print('Cette mesure est enregistrée, passez à la suite.\n')
        
    
    #Graphique pour la droite d'étalonnage à température ambiante 
    plt.figure()
    plt.plot(list_tension,list_conductivite, 'o', color = 'r')
    plt.xlabel('Tension (V)')
    plt.ylabel('Conductivité (us/cm)')
    plt.axis([0, np.max(list_tension), 0, np.max(list_conductivite) +5])
    plt.title('Courbe d\'étalonnage')
    reg_etalonnage= np.polyfit(list_tension, list_conductivite, 1)
    droite_etalonnage= np.poly1d(reg_etalonnage)
    plt.plot(list_tension, droite_etalonnage(list_tension),'--',color='r')
    plt.show()
    
    # plt.figure()
    # plt.plot(list_tension,list_conductivite_25, 'o', color = 'purple')
    # plt.xlabel('Tension (V)')
    # plt.ylabel('Conductivité  à 25 °C (us/cm)')
    # plt.axis([0, np.max(list_tension), 0, np.max(list_conductivite) +5])
    # plt.title('Courbe d\'étalonnage')
    # reg_T_25 = np.polyfit(list_tension, list_conductivite, 1)
    # droite_T_25= np.poly1d(reg_T_ambiante)
    # plt.plot(list_tension, droite_T_25(np.array(list_tension)),'--',color='purple')
    # plt.show()
    
    
    
    np.savetxt('étalonnage du %s.csv' %date, droite, delimiter = ';', header = 'Droite étalonnage du %s' %date)
    return droite_etalonnage #C en fonction de V. On fait l'hypothèse que la pente ne dépend pas de la température. On suppose que V par contre est proportionnel à la température. Reste à vérifier cette hypothèse. 

    


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
     
    Conductivite[0]= droite_12880(20)#remplacer 20 par la température moyenne de la salle dans laquelle s'effectue les manips 
    Conductivite[1]= droite_5000(20)
    Conductivite[2]= droite_1413(20)
     
    reg = np.polyfit(Tension,Conductivite_12880,1)
    droite= np.poly1d(reg)
     
    plt.figure()
    plt.plot(Tension,Conductivite)
    plt.xlabel('Tension en V')
    plt.ylabel('Conductivité en us/cm')
    plt.title('Courbe d\'étalonnage par défaut')
    
    return droite

################################################################################
#
# FONCTIONS DE MESURE DE CONDUCTIVITÉ
#
################################################################################
def Mesures(nbr_echantillon, droite_etalonnage,nbr_mesure_par_echantillon=100):
    """
    Fonction pour faire les mesures de conductivité et de température et les stocker dans un fichier.

    Parameters
    ----------
    nbr_echantillon : int
        Nombre d'échantillons à mesurer dans la série.
    droite : numpy.poly1d
        Equation de droite du calibrage permettant de lier la tension mesurer par le conductimètre et la conductivité réelle.
    nbr_mesure_par_echantillon : int
        Nombre de mesure sur lesquelles les conductivité et température moyennes seront calculées.
        
    Returns
    -------
    None.

    """
    conductimeter = port_connexion()[1]
    numerotation = []
    donnees = []
    list_conductivite=[]
    # droite_etalonnage=Etalonnage()
    
    for k in range(nbr_echantillon):
        print('\n[ Échantillon',k+1,']')
        input('Veuillez préparer votre échantillon, puis appuyer sur Entrée pour lancer la mesure.')
        print('Vos mesures sont en cours, patientez s\'il vous plait.')
        conductimeter.flushInput()
        for i in range(nbr_mesure_par_echantillon): 
            data = conductimeter.readline().decode().strip('\r\n').split(',')
            list_conductivite.append(droite_etalonnage(float(data[0])))
            numerotation.append(k*0.01)
            time.sleep(0.01)
      
        
        print('-> Resultat : La température moyenne est : ', np.mean(list_temp), '°C, et la conductivité moyenne est de : ', np.mean(list_conductivite),'uS/cm.')
        donnees.append([k, np.mean(list_temp), np.mean(list_conductivite)])
    np.savetxt('./data_conductivité.csv', donnees, delimiter = ';',fmt = '%.2f', header='Mesure n°;Température(°C);Conductivité(uS/cm)',)
    print('Vos mesures sont désormais stockées dans le fichier data_conductivité.csv.\nAttention, si vous ne modifiez pas le nom du fichier, elles seront écrasées à la prochaine série de mesures.\n')
    return 

#################################################################################
#
# CORRECTION DE TEMPERATURE
#
#################################################################################

def correction_temperature(C25,Temperature_echantillon):
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

    C25_etalon=[12880,5000,1413]
    Coefficient_directeur=[droite_12880[1],droite_5000[1],droite_1413[1]]

    reg=np.polyfit(C25_etalon,Coefficient_directeur,1)
    #alpha=reg[0]
    #beta=reg[0]
    alpha=np.mean(Coefficient_directeur)/np.mean(C25_etalon)
    beta=0
    
    
    conductivite_corrige=(alpha*(C25)+beta)*(Temperature_echantillon-25)+ C25
    print('Une correction de température a été appliquée à la mesure de conductivité de votre échantillon \nLa conductivité de votre solution vaut :',conductivite_corrige)
    return conductivite_corrige,alpha,beta





    

    






