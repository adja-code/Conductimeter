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
# from uncertainties import ufloat 


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
    """
    Fonction qui détermine si le conductimètre possède une sonde de type K1 ou K10 en fonction du numéro de série de la carte arduino. 

    Returns
    -------
    type_sonde : TYPE
    Entier qui vaut 1 Si la sonde du conductimètre est de type K1 et 10 si la sonde est de type K10.
    """
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

def mesure_etalonnage(nbr_mesure_par_etalon,conductimeter,C25,type_conductimeter):
    # confirmation que l'étalonnage est bon en faisant pendant x min à haute fréquence des mesures puis en les mettant sur un graphique
    '''
    Fonction permettant de faire une série de mesures à haute fréquence, et de la représenter sur un graphique 

    Parameters
    ----------
    nbr_mesure_par_etalon : int
        nombre de mesures par étalon, décidé dans les valeurs par défaut.

    Returns
    conductivite : int
        Conductivité moyenne à température ambiante 
    Ecart_type_conductivite : int
        Ecart-type associé à la valeur de conductivite moyenne
    
    Tension_etalon  : int
    Tension moyenne mesurée à température ambiante 
    
    Ecart_type_tension : int
        Ecart_type associé à la valeure de tension mesurée en dortie de la sonde conductimétrique.
    Temperature_etalon: int
        Température moyenne de la solution
    Ecart_type_temperature : int 
        Écart type associé à la valeur moyenne de conductivité.
    alpha : int 
        Coefficient de correction de tepérature à 25 °C calculé à partir des données présentes sur les solutions tampons Hanna Instruments
    -------
   

    '''
    donnees=[]
    list_tension_etalon = []
    list_temperature=[]
    list_conductivite=[]
    date= datetime.now()
    date=date.replace(second=0,microsecond=0)
    temps=[]
    
    
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
                temps.append(k*0.01)
                print(' Conductivité=',conductivite,'uS/cm', 'Température =',temperature,'°C')
                numero=k+1
                donnees.append([numero,conductivite,C25,temperature,tension])
               
        except Exception:
            pass
          
        
        
    Temperature_etalon= np.mean(list_temperature)
    Tension_etalon=np.mean(list_tension_etalon)
    conductivite=np.mean(list_conductivite)
    
    Ecart_type_conductivite=np.std(list_conductivite)
    Ecart_type_temperature=np.std(list_temperature)
    Ecart_type_tension=np.std(list_tension_etalon)
   
      
    
  
    plt.figure()
    plt.plot(temps, list_conductivite, 'o')
    plt.xlabel('Temps (s)')
    plt.ylabel('Conductivité (uS/cm)')
    plt.title('Evolution de la conductivité en fonction du temps')
    plt.show()
    
    if type_conductimeter==1:
        plt.savefig('../data/figures/Courbe_etalonnage_%s_sonde_K1.png' %(date))
    
    if type_conductimeter==10:
        plt.savefig('../data/figures/Courbe_etalonnage_%s_sonde_K10.png' %(date))
    
    
    
    np.savetxt('../data/data_etalonnage/donnees_brutes_etalonnage_%s.csv' % (date), donnees, delimiter = ';',fmt = '%.2f', header="Étalon n°; Conductivité de la solution (us/cm);Conductivité de la solution à 25°C (uS/cm);Température de l'échantillon (°C);Tension mesurée par le conductimètre (V)")
    return conductivite,Ecart_type_conductivite,Tension_etalon,Ecart_type_tension,Temperature_etalon,Ecart_type_temperature,alpha


def Etalonnage_K1(nbr_etalon, nbr_mesure_par_etalon,conductimeter,type_conductimeter):
    '''
    Fonction qui permet d'étalonner les sondes de type K10 grâce à une régression polyfit si le nombre d'étalons vaut 2  ou gâce à la méthode des moindres carrés et qui enregistre les données automatiquement dans un fichier en format csv et les courbes d'étalonnage au format choisit par l'utilisateur.

    Parameters
    ----------
    nbr_etalon : int
        Nombre de solutions étalons
    nbr_mesure_par_etalon : int
        Nombre de mesures par étalon (200 par défaut à modifier si besoin)
    conductimeter : serial.tools.list_ports_common.ListPortInfo / string
        Objet Serial sur lequel on peut appliquer des fonctions d'ouverture, de lecture et de fermeture du port série affilié. En cas d'échec de connexion, 's' sera une chaîne de caractères "erreur".

    type_conductimeter : int 
        Entier qui vaut 1 si la sonde est de type K1 et 10 si la sonde est de type K10

    Returns
    -------
    a : int
        Coefficient directeur de la régression linéaire C=f(U)
    b : int
        Coefficient directeur de la régression linéaire C=f(U)

    '''
    donnees=[]
    list_tension = []
    list_temp=[]
    list_conductivite=[]
    date= datetime.now()
    date=date.replace(second=0,microsecond=0)
    list_conductivite_25=[]
    list_tension_25=[]
    
    format_figures="""
    ===========================================================================
    Choisissez le format d'enregistrement de vos figures 
    ===========================================================================
    1 - pdf
    2 - svg
    3 - png
    4 - jpeg
    ===========================================================================
    Votre réponse >>> """

    
  

    
    for k in range(nbr_etalon):
        print('\n[ Étalon', k+1,']')
        
        C25 = float(input('Quelle est la valeur de conductivité de votre étalon à 25°C ? (en uS/cm): '))
        input('\nAppuyez sur Entrée pour lancer la mesure.')
        conductivite,Ecart_type_conductivite,Tension_etalon,Ecart_type_tension,temperature,Ecart_type_temperature,alpha = mesure_etalonnage(nbr_mesure_par_etalon,conductimeter,C25,type_conductimeter)
        tension_25=Tension_etalon/(1+alpha*(temperature-25))
      
       
        # print('La conductivité de votre étalon a été corrigée en tenant compte de la température. \nLa conductivité de votre solution étalon vaut :',conductivite,'\nAvec une température moyenne de',temperature,'°C')
        list_conductivite.append(conductivite)
        list_conductivite_25.append(C25)
        list_temp.append(temperature)
        
        list_tension.append(Tension_etalon)
        list_tension_25.append(tension_25)
        
        # conductivite=ufloat(conductivite,Ecart_type_conductivite)
        # conductivite=str(conductivite).replace("+/-","(±)")
        
        # temperature =ufloat(temperature,Ecart_type_temperature)
        # temperature=str(temperature).replace("+/-","(±)")
        
        # tension=ufloat(Tension_etalon,Ecart_type_tension)
        # tension=str(tension).replace("+/-","(±)")
        
        
        
        
        # numerotation = k+1
        
        
        
   
       
        
        # a = input('\nEst ce que la mesure est stable ? (y/n) : ')
        # moy_etalon = stabilite_mesure(a, list_tension_etalonnage, nbr_mesure_par_etalon)
        # list_tension.append(float(moy_etalon))
        print('Cette mesure est enregistrée, passez à la suite.\n')
        donnees.append([conductivite,C25,temperature,Tension_etalon,tension_25])
        
        
        if nbr_etalon==2:
            reg = np.polyfit(list_tension,list_conductivite,1)
            a,b=reg[0],reg[1]
        else : 
            a= np.sum(np.array(list_conductivite_25)*np.array(list_tension_25))/np.sum(np.square(np.array(list_tension_25)))#Méthode des moindres carrés 
            b=0
    

    print('Le coefficient directeur de la dernière courbe d\'étalonnage vaut :' ,a,'uS.V.cm-1')
    
    #Calcul coefficient de corrélation linéaire 
    R_carre= np.square(np.corrcoef(list_tension_25,list_conductivite_25)[0,1])
    print ('R**2 =',R_carre)
    

    np.savetxt('../data/data_etalonnage/dernier_etalonnage_K1.csv',[[a,R_carre]] ,delimiter = ';',fmt = '%.2f',header="Coefficient directeur dernière courbe étalonnage; Coefficient de correlation linéaire")
    np.savetxt('../data/data_etalonnage/donnees_etalonnage_K1 %s.csv' % (date), donnees, delimiter = ';',fmt = '%.2f', header="Conductivité de la solution (us/cm);Conductivité de la solution à 25°C (uS/cm);Température de l'échantillon (°C);Tension mesurée par le conductimètre (V);Tension à 25°C (V)")
    print('Vos mesures sont désormais stockées dans le fichier donnees_etalonnage_K1 %s.csv'%date)    
    
   
    

    list_tension.append(0)
    list_conductivite.append(0)
    
    list_tension_25.append(0)
    list_conductivite_25.append(0)
    
    list_tension=np.array(list_tension)
    list_tension_25=np.array(list_tension_25)
    
    #Graphique pour la droite d'étalonnage à température ambiante 
    

    x=np.linspace(0,np.max(list_tension)+1,500)
    y=a*x
    
    plt.figure()
    plt.plot(list_tension_25,list_conductivite_25, 'o', color = 'pink')
    plt.plot(x,y,'--',color='pink')
    plt.xlabel('Tension  de l\'échantillon à 25°C (V) ')
    plt.ylabel('Conductivité de l\'échantillon à 25°C (us/cm)')
    plt.axis([0, np.max(list_tension)+0.25*np.max(list_tension), 0, np.max(list_conductivite) +0.25*np.max(list_conductivite)])
    # plt.legend()
    plt.title('Courbe d\'étalonnage du %s (sonde K1)' %(date))
    
    choix_format_fig=input(format_figures)
    if choix_format_fig==1:
        format_figure='pdf'
    elif choix_format_fig==2:
        format_figure='svg'
    elif choix_format_fig==3:
        format_figure='png'
    elif choix_format_fig==4:
        format_figure='jpeg'
    
    plt.savefig('../data/figures/Courbe_etalonnage_%s_sonde_K1.%s' %(date,format_figure))

    
    plt.show()
    
    np.savetxt('../data/data_etalonnage/etalonnage_du_%s_sonde_K1.csv' %(date),[[a,R_carre]], header = 'Constante de cellule du %s;Constante de cellule K à 25 °C;Constante de cellule K à 25 °C méthode 2;R carre 25 °C;R carre 25 °C méthode 2' %date)
    return a,b


def Etalonnage_K10(nbr_etalon,nbr_mesure_par_etalon,conductimeter,type_conductimeter):
    '''
    Fonction qui permet d'étalonner les sondes de type K10 grâce à une régression polyfit et qui enregistre les données automatiquement dans un fichier en format csv et les coubres d'étalonnage au format choisit par l'utilisateur.

    Parameters
    ----------
    nbr_etalon : int 
        Nombre de solutions étalons
    nbr_mesure_par_etalon : int
        Nombre de mesures par solution étalons ( 200 par défaut à modifier si besoin dans les paramètres par défaut)
     conductimeter : serial.tools.list_ports_common.ListPortInfo / string
         Objet Serial sur lequel on peut appliquer des fonctions d'ouverture, de lecture et de fermeture du port série affilié. En cas d'échec de connexion, 's' sera une chaîne de caractères "erreur".
    type_conductimeter : int
        Entier qui vaut 1 si le conductimètre possède une sonde K1 et 10 si la sonde est de type K10

    Returns
    -------
    a : int
        Coefficient directeur de la courbe d'étalonnage'
    b : int
        Ordonnée à l'origine de la courbe d'étalonnage  


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
    
    format_figures="""
    ===========================================================================
    Choisissez le format d'enregistrement de vos figures 
    ===========================================================================
    1 - pdf
    2 - svg
    3 - png
    4 - jpeg
    ===========================================================================
    Votre réponse >>> """
  

    
    for k in range(nbr_etalon):
        print('\n[ Étalon', k+1,']')
        
        C25 = float(input('Quelle est la valeur de conductivité de votre étalon à 25°C ? (en uS/cm): '))
        input('\nAppuyez sur Entrée pour lancer la mesure.')
        conductivite,Ecart_type_conductivite,Tension_etalon,Ecart_type_tension,temperature,Ecart_type_temperature,alpha = mesure_etalonnage(nbr_mesure_par_etalon,conductimeter,C25,type_conductimeter)
        
      
       
        # print('La conductivité de votre étalon a été corrigée en tenant compte de la température. \nLa conductivité de votre solution étalon vaut :',conductivite,'\nAvec une température moyenne de',temperature,'°C')
        list_conductivite.append(conductivite)
        list_conductivite_25.append(C25)
        list_temp.append(temperature)
        
        list_tension.append(Tension_etalon)
    
        
        # conductivite=ufloat(conductivite,Ecart_type_conductivite)
        # conductivite=str(conductivite).replace("+/-","(±)")
        
        # temperature =ufloat(temperature,Ecart_type_temperature)
        # temperature=str(temperature).replace("+/-","(±)")
        
        # tension=ufloat(Tension_etalon,Ecart_type_tension)
        # tension=str(tension).replace("+/-","(±)")
        

        
        
        
        
        numerotation = numerotation+1
        
        
        
   
       
        
        # a = input('\nEst ce que la mesure est stable ? (y/n) : ')
        # moy_etalon = stabilite_mesure(a, list_tension_etalonnage, nbr_mesure_par_etalon)
        # list_tension.append(float(moy_etalon))
        print('Cette mesure est enregistrée, passez à la suite.\n')
        donnees.append([numerotation,conductivite,C25,temperature,Tension_etalon])
     
    reg=np.polyfit(list_tension,list_conductivite,1)
    
    a,b=reg[0],reg[1]
    

    print('Le coefficient directeur de la dernière courbe d\'étalonnage vaut :' ,a,'uS.V.cm-1')
    
    #Calcul coefficient de corrélation linéaire 
    # R_carre= np.square(np.corrcoef(list_tension_25,list_conductivite_25)[0,1])
    # print ('R**2 =',R_carre)
    

    np.savetxt('../data/data_etalonnage/dernier_etalonnage_K10.csv',[[a,b]] ,delimiter = ';',fmt = '%.2f',header="Coefficient directeur dernière courbe étalonnage; Ordonnée à l'origine")
    np.savetxt('../data/data_etalonnage/donnees_etalonnage_K10 %s.csv' % (date), donnees, delimiter = ';',fmt = '%.2f', header="Étalon n°; Conductivité de la solution (us/cm);Conductivité de la solution à 25°C (uS/cm);Température de l'échantillon (°C);Tension mesurée par le conductimètre (V)")
    print('Vos mesures sont désormais stockées dans le fichier donnees_etalonnage_K10 %s.csv'%date)    
    
   
    

    
    
    list_tension=np.array(list_tension)
    list_tension_25=np.array(list_tension_25)
    
    #Graphique pour la droite d'étalonnage à température ambiante 
    

    x=np.linspace(0,np.max(list_tension)+1,500)
    y=a*x+b
    
    plt.figure()
    plt.plot(list_tension,list_conductivite, 'o', color = 'purple')
    plt.plot(x,y,'--',color='purple')
    plt.xlabel('Tension  de l\'échantillon (V) ')
    plt.ylabel('Conductivité de l\'échantillon (us/cm)')
    plt.axis([0, np.max(list_tension)+0.25*np.max(list_tension), 0, np.max(list_conductivite) +0.25*np.max(list_conductivite)])
    # plt.legend()
    plt.title('Courbe d\'étalonnage du %s (sonde K10)' %date)
    
    choix_format_fig=input(format_figures)
    if choix_format_fig==1:
        format_figure='pdf'
    elif choix_format_fig==2:
        format_figure='svg'
    elif choix_format_fig==3:
        format_figure='png'
    elif choix_format_fig==4:
        format_figure='jpeg'
    
    plt.savefig('../data/figures/Courbe_etalonnage_%s_sonde_K1.%s' %(date,format_figure))

    
    plt.show()
    
    np.savetxt('../data/data_etalonnage/etalonnage_du_%s_sonde_K10.csv' %(date),[[a,b]], header = 'Coefficient directeur a;Ordonnée à l\'origine b;R**2')
  
    return a,b
    





################################################################################
#
# FONCTIONS DE MESURE DE CONDUCTIVITÉ
#
################################################################################
def Mesures_K1(a,b,nbr_mesure_par_echantillon,conductimeter):
    '''
    Fonction qui convertit la tension mesurée par le conductimètre en conductivité, applique une correction de température afin d'obtenir la conductivité à 25°C, et enregistrerles données dans un fichier pour une sonde K1'

    Parameters
    ----------
    a : int
        Coefficient directeur de la courbe d'étalonage
    b : int
        Ordonnée à l'origine de la courbe d'étalonnage 
    nbr_mesure_par_echantillon :int 
        Nombre de mesures par échantillon 
    conductimeter : serial.tools.list_ports_common.ListPortInfo / string
        Objet Serial sur lequel on peut appliquer des fonctions d'ouverture, de lecture et de fermeture du port série affilié. En cas d'échec de connexion, 's' sera une chaîne de caractères "erreur".
    
    Returns
    -------
    conductivite : int
       Conductivité moyenne de la solution  à Température ambiante
    C25 : int
        Conductivité moyenne de la solution à 25 °C
    temperature : int
        Température moyenne de la solution
    date : datetime
        Date et heure de la mesure 

    '''
    

    # conductimeter = port_connexion()[1]

    donnees_moyennes = []
    list_conductivite=[]
    list_temp=[]
    list_C25=[]
    donnees=[]
    
   

    
    
   
  
    input('Veuillez préparer votre échantillon, puis appuyer sur Entrée pour lancer la mesure.')
    print('Vos mesures sont en cours, patientez s\'il vous plait.')
    conductimeter.flushInput()
    for i in range(nbr_mesure_par_echantillon): 
    
        data = conductimeter.readline().decode().strip('\r\n').split(',')
        try :
            if float(data[1]) != 0 :
                temperature=float(data[0])
                tension=float(data[1])
                alpha=correction_temperature_mesure(temperature,tension,a)[1]
                conductivite=a*tension + b
                C25=conductivite/(alpha*(temperature-25)+1)
                list_conductivite.append(conductivite)
                list_temp.append(temperature)
                list_C25.append(C25)
                print('Conductivité :',conductivite,'us/cm','Conductivité à 25 °C :',C25,'uS/cm', 'Température =',temperature,'°C')
                donnees.append([i,conductivite,C25,temperature,tension])
           
        
       
        except Exception:
            pass
            
               
        
        
        
    Ecart_type_conductivite=np.std(list_conductivite)
    Ecart_type_temperature=np.std(list_temp)
        
    conductivite=np.mean(list_conductivite)
        # conductivite=round(conductivite/Ecart_type_conductivite)*Ecart_type_conductivite
    C25=np.mean(list_C25)  
    temperature=np.mean(list_temp)
        # temperature=round(temperature/Ecart_type_temperature)*Ecart_type_temperature 
        
        
        
    print('-> Resultat : La température moyenne est : ',temperature,'(±)',Ecart_type_temperature, '°C \nLa conductivité moyenne est de : ', np.mean(list_conductivite),'(±)',Ecart_type_conductivite,'uS/cm.\nLa conductivité de votre échantillon à 25 ° C vaut : ',np.mean(list_C25))
    donnees_moyennes.append([np.mean(list_temp), np.mean(list_conductivite)])
        
    date= datetime.now()
    date=date.replace(second=0,microsecond=0)
    
    np.savetxt('../data/data_mesures/data_conductivité_K10 du %s.csv' %date, donnees, delimiter = ';',fmt = '%.2f', header='Température(°C);Conductivité(uS/cm);Conductivité de l\'échantillon à 25°C (uS/cm);Conductivité méthode 2(uS/cm);Conductivité de l\'échantillon à 25°C méthode 2 (uS/cm)')
    
    print('Vos mesures sont désormais stockées dans le fichier data_conductivite_K10 du %s.csv.' %date)
    return conductivite,C25,temperature,date

def Mesures_K10(a,b,nbr_mesure_par_echantillon,conductimeter):
    """
    Fonction qui convertit la tension mesurée par le conductimètre en conductivité, applique une correction de température afin d'obtenir la conductivité à 25°C, et enregistrerles données dans un fichier pour une sonde K1'

    Parameters
    ----------
    a : int
        Coefficient directeur de la courbe d'étalonage
    b : int
        Ordonnée à l'origine de la courbe d'étalonnage 
    nbr_mesure_par_echantillon :int 
        Nombre de mesures par échantillon 
    conductimeter : serial.tools.list_ports_common.ListPortInfo / string
        Objet Serial sur lequel on peut appliquer des fonctions d'ouverture, de lecture et de fermeture du port série affilié. En cas d'échec de connexion, 's' sera une chaîne de caractères "erreur".
    
    Returns
    -------
    conductivite : int
       Conductivité moyenne de la solution  à Température ambiante
    C25 : int
        Conductivité moyenne de la solution à 25 °C
    temperature : int
        Température moyenne de la solution
    date : datetime
        Date et heure de la mesure 


    """
    # conductimeter = port_connexion()[1]

    donnees_moyennes = []
    list_conductivite=[]
    list_temp=[]
    list_C25=[]
    donnees=[]
    
   

    
    
   
  
    input('Veuillez préparer votre échantillon, puis appuyer sur Entrée pour lancer la mesure.')
    print('Vos mesures sont en cours, patientez s\'il vous plait.')
    conductimeter.flushInput()
    for i in range(nbr_mesure_par_echantillon): 
    
        data = conductimeter.readline().decode().strip('\r\n').split(',')
        try :
            if float(data[1]) != 0 :
                temperature=float(data[0])
                tension=float(data[1])
                alpha=correction_temperature_mesure(temperature,tension,a)[1]
                conductivite=a*tension+b
                C25=conductivite/(alpha*(temperature-25)+1)
                list_conductivite.append(conductivite)
                list_temp.append(temperature)
                list_C25.append(C25)
                print('Conductivité :',conductivite,'us/cm','Conductivité à 25 °C :',C25,'uS/cm', 'Température =',temperature,'°C')
                donnees.append([i,conductivite,C25,temperature,tension])
           
        
       
        except Exception:
            pass
            
               
        
        
        
    Ecart_type_conductivite=np.std(list_conductivite)
    Ecart_type_temperature=np.std(list_temp)
    
    conductivite=np.mean(list_conductivite)    
    # conductivite=ufloat(conductivite,Ecart_type_conductivite)
    # conductivite=str(conductivite).replace("+/-","(±)")
   
    temperature=np.mean(temperature)
    # temperature =ufloat(temperature,Ecart_type_temperature)
    # temperature=str(temperature).replace("+/-","(±)")
   

        
        
    print('-> Resultat : La température moyenne est : ',temperature, '°C \nLa conductivité moyenne est de : ', conductivite,'uS/cm.\nLa conductivité de votre échantillon à 25 ° C vaut : ',np.mean(list_C25))
   
        
    date= datetime.now()
    date=date.replace(second=0,microsecond=0)
    
    np.savetxt('../data/data_mesures/data_conductivité du %s.csv' %date, donnees, delimiter = ';',fmt = '%.2f', header='Température(°C);Conductivité(uS/cm);Conductivité de l\'échantillon à 25°C (uS/cm);Conductivité méthode 2(uS/cm);Conductivité de l\'échantillon à 25°C méthode 2 (uS/cm)')
    np.savetxt('../data/data_mesures/data_conductivité du %s.csv' %date, donnees_moyennes, delimiter = ';',fmt = '%.2f', header='Température(°C);Conductivité moyenne (uS/cm);Conductivité moyenne de l\'échantillon à 25°C (uS/cm);Conductivité méthode 2(uS/cm);Conductivité de l\'échantillon à 25°C méthode 2 (uS/cm)')
    print('Vos mesures sont désormais stockées dans le fichier data_conductivite du %s.csv.' %date)
    return conductivite,C25,temperature,date

#################################################################################
#
# CORRECTION DE TEMPERATURE
#
#################################################################################

def correction_temperature_etalonnage(C25,Temperature_echantillon):
    '''
    Fonction qui prend en argument la conductivité d'une solution étalon à 25 et sa température et renvoie la conductivité corrigée'

    Parameters
    ----------
    C25 : int
        Conductivité de la solution étalon à 25 °C
    Temperature_echantillon : int
        Température moyenne de la solution

    Returns
    -------
    conductivite_corrige : int
        Conductivité moyenne de a solution corrigée par la température
    alpha : int
        Coefficient de correction de température calculé à partir des données fournies par la société Hanna Instruments. 

    '''
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
    '''
    Fonction qui prend en argument la conductivité d'une solution étalon à 25 et sa température et renvoie la conductivité corrigée'

    Parameters
    ----------
    C25 : int
        Conductivité de la solution étalon à 25 °C
    Temperature_echantillon : int
        Température moyenne de la solution

    Returns
    -------
    conductivite_corrige : int
        Conductivité moyenne de a solution corrigée par la température
    alpha : int
        Coefficient de correction de température calculé à partir des données fournies par la société Hanna Instruments. 

    '''
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





    

    






