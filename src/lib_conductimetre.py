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
                conn = False
            pass    
    return port,s


def type_conductimetre():
    type_sonde=0
    conn= False
    list_K1=['7513931383135170A031','75131313932351F08160','85138313034351818222','75131313932351403012','7513131393235121B0A1']
    #['ADNI','SOMA','LOTHI','GUITERA','AMPAPI']
    list_K10=['7513931383135110A2D1','9513832383835190A231','751393138313510190A0','85138313633351403151']
    #['ANRE','MAJUCA','BALEW','GAGAMA']
    while conn == False:
        try :
            port=list(serial.tools.list_ports.comports())[0]
            if port.serial_number in list_K1:
                type_sonde=1
            elif port.serial_number in list_K10:
                type_sonde=10
            else :
                print('Votre conductimètre n\'est pas reconnu, merci de vérifier les branchements')
                conn = False
        except Exception :
            conn= False
            pass
        return type_sonde
        
        
    
    

#########################################################
#
# FONCTIONS DE CALIBRATION 
#
#########################################################

def mesure_etalonnage(nbr_mesure_par_etalon,conductimeter,C25):
    # confirmation que l'étalonnage est bon en faisant pendant x min à haute fréquence des mesures puis en les mettant sur un graphique
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
    list_conductivite=[]
    numerotation = []
    date= datetime.now()
    date=date.replace(second=0,microsecond=0)
    
    
    print('Les mesures sont en cours, attendez s\'il vous plait.')
    conductimeter.flushInput()
    for k in range(nbr_mesure_par_etalon):
        lect = conductimeter.readline().decode().strip('\r\n').split(',')
        try :
            if float(lect[1]) != 0 :
                temperature=float(lect[0])
                tension=float(lect[1])
                conductivite, alpha= correction_temperature_etalonnage(C25,temperature)
                list_tension_etalon.append(tension)
                list_temperature.append(temperature)
                list_conductivite.append(conductivite)
                numerotation.append(k*0.01)
                print(' Conductivité=',conductivite,'uS/cm', 'Température =',temperature,'°C')
        except Exception:
            print('erreur')
            pass
          
        
        
    Temperature_etalon= np.mean(list_temperature)
    Tension_etalon=np.mean(list_tension_etalon)
    
    Ecart_type_conductivite=np.std(list_conductivite)
    Ecart_type_temperature=np.std(list_temperature)
    conductivite=np.mean(list_conductivite)
    conductivite=round(conductivite/Ecart_type_conductivite)*Ecart_type_conductivite
    temperature = round(temperature/Ecart_type_temperature)*Ecart_type_temperature
        
    
  
    plt.figure()
    plt.plot(numerotation, list_tension_etalon, 'o')
    plt.xlabel('Temps (s)')
    plt.ylabel('Tension (V)')
    plt.show()
    
    
    
    
    return conductivite,Tension_etalon,Temperature_etalon,alpha


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
    donnees=[]
    list_tension = []
    list_temp=[]
    list_conductivite=[]
    date= datetime.now()
    date=date.replace(second=0,microsecond=0)
    list_conductivite_25=[]
    numerotation=0
    list_tension_25=[]
    list_tension_25_bis=[]

    
    for k in range(nbr_etalon):
        print('\n[ Étalon', k+1,']')
        
        C25 = float(input('Quelle est la valeur de conductivité de votre étalon à 25°C ? (en uS/cm): '))
        input('\nAppuyez sur Entrée pour lancer la mesure.')
        conductivite,Tension_etalon,temperature,alpha = mesure_etalonnage(nbr_mesure_par_etalon,conductimeter,C25)
        tension_25=Tension_etalon/(1+alpha*(temperature-25))
        tension_25_bis=(Tension_etalon*C25)/conductivite
        # print('La conductivité de votre étalon a été corrigée en tenant compte de la température. \nLa conductivité de votre solution étalon vaut :',conductivite,'\nAvec une température moyenne de',temperature,'°C')
        list_conductivite.append(conductivite)
        list_conductivite_25.append(C25)
        list_temp.append(temperature)
        
        list_tension.append(Tension_etalon)
        list_tension_25.append(tension_25)
        list_tension_25_bis.append(tension_25_bis)
        numerotation = k+1
        
   
       
        
        # a = input('\nEst ce que la mesure est stable ? (y/n) : ')
        # moy_etalon = stabilite_mesure(a, list_tension_etalonnage, nbr_mesure_par_etalon)
        # list_tension.append(float(moy_etalon))
        print('Cette mesure est enregistrée, passez à la suite.\n')
        donnees.append([numerotation,temperature,Tension_etalon,conductivite])
        

    K= np.sum(np.array(list_conductivite)*np.array(list_tension))/np.sum(np.square(np.array(list_tension)))
    K_25= np.sum(np.array(list_conductivite_25)*np.array(list_tension_25))/np.sum(np.square(np.array(list_tension_25)))
    K_25_bis= np.sum(np.array(list_conductivite_25)*np.array(list_tension_25_bis))/np.sum(np.square(np.array(list_tension_25_bis)))
    

    print('\nLa constante de cellule calculée à partir des conductivités à température ambiante  vaut',K,'uS.V.cm-1')
    print('\nLa constante de cellule calculée à partir des conductivités à température ambiante  vaut',K_25,'uS.V.cm-1')
    #Calcul coefficient de corrélation linéaire 
    R_carre= np.square(np.corrcoef(list_tension,list_conductivite)[0,1])
    R_carre_25= np.square(np.corrcoef(list_tension_25,list_conductivite_25)[0,1])
    R_carre_25_bis= np.square(np.corrcoef(list_tension_25_bis,list_conductivite_25)[0,1])
    
    print ('R**2 =',R_carre)
    print ('R**2 25°C =',R_carre_25)
    print ('R**2 25 °C bis',R_carre_25_bis)
    
    type_conductimeter= type_conductimetre()
    if type_conductimeter==1:
        np.savetxt('../data/data_etalonnage/dernier_etalonnage_K1.csv',[[K,R_carre,R_carre_25,R_carre_25_bis]] ,delimiter = ';',fmt = '%.2f',header="Constante de Cellule K du dernier étalonnage; Coefficient de correlation linéaire; Coeff 25 °C méthode 1; Coeff 25°C méthode 2")
        np.savetxt('../data/data_etalonnage/donnees_etalonnage_K1 %s.csv' % (date), donnees, delimiter = ';',fmt = '%.2f', header="Étalon n°;Température de l'échantillon (°C);Tension mesurée par  conductimètre (V);Tension à 25°C (V); Conductivité de la solution (us/cm);Conductivité de la solution à 25°C (uS/cm)")
        print('Vos mesures sont désormais stockées dans le fichier donnees_etalonnage_K1 %s.csv'%date)    
    
    elif type_conductimeter==10:
        np.savetxt('../data/data_etalonnage/dernier_etalonnage_K10.csv',[[K,R_carre]] ,delimiter = ';',fmt = '%.2f',header="Constante de Cellule K du dernier étalonnage; Coefficient de correlation linéaire")
        np.savetxt('../data/data_etalonnage/donnees_etalonnage_K10 %s.csv' % (date), donnees, delimiter = ';',fmt = '%.2f', header="Étalon n°;Température de l'échantillon (°C);Tension mesurée par  conductimètre (V);Tension à 25°C (V); Conductivité de la solution (us/cm);Conductivité de la solution à 25°C (uS/cm)")
        print('Vos mesures sont désormais stockées dans le fichier donnees_etalonnage_K10 %s.csv'%date)    
    
    

    list_tension.append(0)
    list_conductivite.append(0)
    
    list_tension_25.append(0)
    list_conductivite_25.append(0)
    
    list_tension=np.array(list_tension)
    list_tension_25=np.array(list_tension_25)
    
    #Graphique pour la droite d'étalonnage à température ambiante 
    
    reg=np.polyfit(list_tension,list_conductivite,2,full=False)
    x=np.linspace(0,np.max(list_tension+0.2),500)
    a,b=reg[0],reg[1]
    y=a*(x**2)+b*x
    
    
    plt.figure()
    plt.plot(list_tension,list_conductivite, 'o', color = 'pink')
    plt.plot(list_tension,K*list_tension,'--',color='pink')
    plt.plot(x,y,'--',color='pink')
    plt.xlabel('Tension (V)')
    plt.ylabel('Conductivité (us/cm)')
    plt.axis([0, np.max(list_tension)+0.2, 0, np.max(list_conductivite) +1000])
    # plt.legend()
    plt.title('Courbe d\'étalonnage sonde %s' %type_conductimeter)
    plt.savefig('../data/figures/Courbe d\'étalonnage sonde %s du %s.png' %(type_conductimeter,date))
    
    plt.figure()
    plt.plot(list_tension_25,list_conductivite_25, 'o', color = 'purple')
    plt.plot(list_tension_25,K_25*list_tension_25,'--',color='purple')
    plt.xlabel('Tension (V)')
    plt.ylabel('Conductivité (us/cm)')
    plt.axis([0, np.max(list_tension)+0.2, 0, np.max(list_conductivite) +1000])
    # plt.legend()
    plt.title('Courbe d\'étalonnage sonde %s à 25 °C' %type_conductimeter)
    plt.savefig('../data/figures/Courbe d\'étalonnage sonde %s du %s.png' %(type_conductimeter,date))
    
    
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
    
    
    
    np.savetxt('../data/data_etalonnage/étalonnage du %s.csv' %date,[[K,K_25,K_25_bis,R_carre,R_carre_25,R_carre_25_bis]], header = 'Constante de cellule du %s;Constante de cellule K à 25 °C;Constante de cellule K à 25 °C méthode 2;R carre 25 °C;R carre 25 °C méthode 2' %date)
    return K#Constante de cellule obtenue a partir de la relation C(T)= K*V(T) avec C la conductivité et V la tension 

    




################################################################################
#
# FONCTIONS DE MESURE DE CONDUCTIVITÉ
#
################################################################################
def Mesures(K,nbr_mesure_par_echantillon,conductimeter):
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

    donnees = []
    list_conductivite=[]
    list_temp=[]
    list_C25=[]
    

    
    
   
  
    input('Veuillez préparer votre échantillon, puis appuyer sur Entrée pour lancer la mesure.')
    print('Vos mesures sont en cours, patientez s\'il vous plait.')
    conductimeter.flushInput()
    for i in range(nbr_mesure_par_echantillon): 
        data = conductimeter.readline().decode().strip('\r\n').split(',')
        try :
            if float(data[1]) != 0 :
                temperature=float(data[0])
                tension=float(data[1])
                alpha=correction_temperature_mesure(temperature,tension,K)[1]
                conductivite=K*tension
                list_conductivite.append(conductivite)
                list_temp.append(temperature)
                list_C25.append(conductivite/(alpha*(temperature-25)+1))
                print('Conductivité =',conductivite,'us/cm', 'Température =',temperature,'°C')
       
        except Exception:
            pass
                
               
        
        
        Ecart_type_conductivite=np.std(list_conductivite)
        Ecart_type_temperature=np.std(list_temp)
        
        conductivite=np.mean(list_conductivite)
        # conductivite=round(conductivite/Ecart_type_conductivite)*Ecart_type_conductivite
        
        temperature=np.mean(list_temp)
        # temperature=round(temperature/Ecart_type_temperature)*Ecart_type_temperature 
        
        
        
        print('-> Resultat : La température moyenne est : ',temperature,'(±)',Ecart_type_temperature, '°C \nLa conductivité moyenne est de : ', np.mean(list_conductivite),'(±)',Ecart_type_conductivite,'uS/cm.\nLa conductivité de votre échantillon à 25 ° C vaut : ',np.mean(list_C25))
        donnees.append([np.mean(list_temp), np.mean(list_conductivite)])
        
    date= datetime.now()
    date=date.replace(second=0,microsecond=0)
    
    np.savetxt('../data/data_mesures/data_conductivité du %s.csv' %date, donnees, delimiter = ';',fmt = '%.2f', header='Température(°C);Conductivité(uS/cm);Conductivité de l\'échantillon à 25°C (uS/cm);Conductivité méthode 2(uS/cm);Conductivité de l\'échantillon à 25°C méthode 2 (uS/cm)')
    print('Vos mesures sont désormais stockées dans le fichier data_conductivite du %s.csv.' %date)
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
    print('Conductivité:',conductivite_corrige,'uS/cm',' Temperature:',Temperature_echantillon,'°C')
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





    

    






