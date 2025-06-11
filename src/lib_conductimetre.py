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
            if portIN == '' and (port.manufacturer == 'Arduino (www.arduino.cc)' or port.serial_number in arduino_list ): 
                port = port.device
                port = (port).replace('cu','tty')
                s = serial.Serial(port=port, baudrate=br, timeout=5) 
                conn = True  
                print('Connexion établie avec le port', port)
            else :
                conn = True
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

#########################################################
#
# FONCTIONS DE CALIBRATION 
#
#########################################################

def mesure_etalonnage(nbr_mesure_par_etalon,conductimeter):   # confirmation que l'étalonnage est bon en faisant pendant x min à haute fréquence des mesures puis en les mettant sur un graphique
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
    list_tension_etalon = []
    list_temperature=[]
    numerotation = []
    date= datetime.now()
    date=date.replace(second=0,microsecond=0)
    
    print('Les mesures sont en cours, attendez s\'il vous plait.')
    conductimeter.flushInput()
    for k in range(nbr_mesure_par_etalon):
        lect = conductimeter.readline().decode().strip('\r\n').split(',')
        list_tension_etalon.append(float(lect[1]))
        list_temperature.append(float(lect[0]))
        numerotation.append(k*0.01)
        time.sleep(0.01)
    Temperature_etalon= np.mean(list_temperature)
    Tension_etalon=np.mean(list_tension_etalon)
        
    
  
    plt.figure()
    plt.plot(numerotation, list_tension_etalon, 'o')
    plt.xlabel('Temps (s)')
    plt.ylabel('Tension (V)')
    plt.show()
    
    
    
    
    return Tension_etalon,Temperature_etalon


def Etalonnage(nbr_etalon, nbr_mesure_par_etalon,conductimeter):
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

    list_tension = []
    list_temp=[]
    list_conductivite=[]
    date= datetime.now()
    date=date.replace(second=0,microsecond=0)
    list_conductivite_25=[]
    numerotation=[]

    
    for k in range(nbr_etalon):
        print('\n[ Étalon', k+1,']')
        
        conductivite = float(input('Quelle est la valeur de conductivité de votre étalon à 25°C ? (en uS/cm): '))
        input('\nAppuyez sur Entrée pour lancer la mesure.')
        list_conductivite_25.append(conductivite)
        Tension_etalon,temperature = mesure_etalonnage(nbr_mesure_par_etalon,conductimeter)
        conductivite, alpha= correction_temperature_etalonnage(conductivite,temperature)
        # print('La conductivité de votre étalon a été corrigée en tenant compte de la température. \nLa conductivité de votre solution étalon vaut :',conductivite,'\nAvec une température moyenne de',temperature,'°C')
        list_conductivite.append(conductivite)
        list_temp.append(temperature)
        
        list_tension.append(Tension_etalon)
        ecart_type = np.std(list_tension)
        numerotation.append(k+1)
        print('L\'écart-type des mesures de l\'étalon est :', ecart_type,'V, un graphique s\'est aussi affiché.')
        
   
       
        
        # a = input('\nEst ce que la mesure est stable ? (y/n) : ')
        # moy_etalon = stabilite_mesure(a, list_tension_etalonnage, nbr_mesure_par_etalon)
        # list_tension.append(float(moy_etalon))
        print('Cette mesure est enregistrée, passez à la suite.\n')
        
    K = np.mean(list_conductivite)/np.mean(list_tension)#Constante de cellule supposée indépendante de la température. 
    print('La constante de cellule vaut',K,'uS.V.cm-1')
    np.savetxt('../data/dernier_etalonnage.csv',np.array([K]),header='Constante de Cellule K du dernier étalonnage')
    np.savetxt('../data/tension_etalonnage du %s.csv' %date,np.array([numerotation,list_temp,list_tension,list_conductivite,list_conductivite_25]), delimiter = ';',fmt = '%.2f', header='Étalon n°;Température de l\'échantillon (°C);Tension mesurée par le conductimètre (V);Conductivité de la solution (us/cm);Conductivité de la solution à 25°C (uS/cm)')
    print('Vos mesures sont désormais stockées dans le fichier tension_etalonnage.csv')    
    
    list_tension.append(0)
    list_conductivite.append(0)
    #Graphique pour la droite d'étalonnage à température ambiante 
    plt.figure()
    plt.plot(list_tension,list_conductivite, 'o', color = 'r')
    plt.plot(list_tension,K*np.array(list_tension),'--',color='r')
    plt.xlabel('Tension (V)')
    plt.ylabel('Conductivité (us/cm)')
    plt.axis([0, np.max(list_tension), 0, np.max(list_conductivite) +5])
    plt.title('Courbe d\'étalonnage')
    plt.savefig('../data/Courbe d\'étalonnage du %s.png' %date)
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
    
    
    
    np.savetxt('../étalonnage du %s.csv' %date, np.array([K]), header = 'Constante de cellule du %s' %date)
    return K #Constante de cellule obtenue a partir de la relation C(T)= K*V(T) avec C la conductivité et V la tension 

    




################################################################################
#
# FONCTIONS DE MESURE DE CONDUCTIVITÉ
#
################################################################################
def Mesures(nbr_echantillon,K,nbr_mesure_par_echantillon,conductimeter):#
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
    # conductimeter = port_connexion()[1]
    numerotation = []
    donnees = []
    list_conductivite=[]
    list_temp=[]
    list_C25=[]
    nbr_erreurs=0
    
    
    for k in range(nbr_echantillon):
        print('\n[ Échantillon',k+1,']')
        input('Veuillez préparer votre échantillon, puis appuyer sur Entrée pour lancer la mesure.')
        print('Vos mesures sont en cours, patientez s\'il vous plait.')
        conductimeter.flushInput()
        for i in range(nbr_mesure_par_echantillon): 
            data = conductimeter.readline().decode().strip('\r\n').split(',')
            try :
                temperature=float(data[0])
                tension=float(data[1])
            except Exception:
                nbr_erreurs+=1
            if nbr_erreurs>0:
                print ('Le nombre de mesures par échantillon vaut :',nbr_mesure_par_echantillon-nbr_erreurs)
            alpha=correction_temperature_mesure(temperature,tension,K)[1]
            conductivite=K*tension
            list_conductivite.append(conductivite)
            list_temp.append(temperature)
            numerotation.append(k+1)
            list_C25.append(conductivite/(alpha*(temperature-25)+1))
           
            
            
               
        
        
      
        print('-> Resultat : La température moyenne est : ', np.mean(list_temp), '°C \nLa conductivité moyenne est de : ', np.mean(list_conductivite),'uS/cm.\nLa conductivité de votre échantillon à 25 ° C vaut : ',np.mean(list_C25))
        donnees.append([np.mean(list_temp), np.mean(list_conductivite),np.mean(list_C25)])
        
    date= datetime.now()
    date=date.replace(second=0,microsecond=0)
    
    np.savetxt('../data_conductivité du %s.csv' %date, donnees, delimiter = ';',fmt = '%.2f', header='Température(°C);Conductivité(uS/cm);Conductivité de l\'échantillon à 25°C (uS/cm)')
    print('Vos mesures sont désormais stockées dans le fichier data_conductivite.csv.\nAttention, si vous ne modifiez pas le nom du fichier, elles seront écrasées à la prochaine série de mesures.\n')
    return 

#################################################################################
#
# CORRECTION DE TEMPERATURE
#
#################################################################################

def correction_temperature_etalonnage(C25,Temperature_echantillon):
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

    # reg=np.polyfit(C25_etalon,Coefficient_directeur,1)
    #alpha=reg[0]
    #beta=reg[0]
    alpha=np.mean(Coefficient_directeur)/np.mean(C25_etalon)
    
    
    conductivite_corrige=(alpha*(C25))*(Temperature_echantillon-25)+ C25
    print('Une correction de température a été appliquée à la mesure de conductivité de votre échantillon \n\nLa conductivité de votre solution vaut :',conductivite_corrige,'La température de votre solution vaut :',Temperature_echantillon,'°C')
    return conductivite_corrige,alpha

def correction_temperature_mesure(Temperature_echantillon,Tension_echantillon,K):
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

    alpha=np.mean(Coefficient_directeur)/np.mean(C25_etalon)
    
    
    conductivite_corrige=K*Tension_echantillon*(alpha*(Temperature_echantillon - 25)+1)#K correspond à la constante de cellule elle est déterminée à l'étalonnage.
                        
    # print('Une correction de température a été appliquée \n\nLa conductivité de votre solution vaut :',conductivite_corrige,'\nLa température de votre solution vaut :',Temperature_echantillon,'°C')
    return conductivite_corrige,alpha





    

    






