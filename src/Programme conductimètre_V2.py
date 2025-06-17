import sys
sys.path.append(".")
from lib_conductimetre import *



if __name__ == '__main__':

    plt.ion() 
    nbr_mesure_par_echantillon = 100 
    nbr_mesure_par_etalon = 200
    port, conductimeter = port_connexion()
   

    


    
    
    #Initialisation des valeurs par défaut
    nbr_mesure_par_echantillon = 100 
    nbr_mesure_par_etalon = 200
    interface_acceuil="""
    ===========================================================================
    ACCEUIL
    ===========================================================================
    Que voulez-vous faire ? :
    1 - Etalonner le conductimètre 
    2 - Mesurer la conductivité d'une solution
    3 - Modifier les valeurs par défaut 
    4 - Quitter
    ===========================================================================
    Votre réponse >>> """
    
    interface_calibration ="""
    ===========================================================================
    CALIBRATION
    ===========================================================================
    Que voulez-vous faire ? :
    1 - Nouvel étalonnage
    2 - Utiliser un étalonnage par défaut 
    3 - Quitter
    ===========================================================================
    Votre réponse >>> """
    
    interface_type_etalonnage="""
    ===========================================================================
    Quel étalonnage par défaut 
    ===========================================================================
    1 - Utiliser l'étalonnage le plus récent
    2 - Choisir un étalonnage particulier en fonction de sa date
    ===========================================================================
    Votre réponse >>> """
    
    interface_mesure="""
    ===========================================================================
    Souhaitez-vous mesurer la conductivité d'une autre solution
    ===========================================================================
     Y - Yes
     N - No  
    ===========================================================================
    Votre réponse >>> 
    """
    
        
    while(True) : 
        reponse = input(interface_acceuil)
        
        if reponse == '1' : # Calibration
            choix_calib=int(input(interface_calibration))
            if choix_calib==1 : 
                nbr_etalon = int(input("Combien d'étalons voulez-vous mesurer ? (au moins 1) : "))
                Etalonnage(nbr_etalon, nbr_mesure_par_etalon,conductimeter)
                print('- Vous avez fini le calibrage.\n')
            elif choix_calib==2:
                type_etalonnage=int(input(interface_type_etalonnage))
                if type_etalonnage==1:
                    type_conductimetre()
                    if type_conductimetre()==1:
                        K = np.loadtxt('../data/data_etalonnage/dernier_etalonnage_K1.csv', delimiter = ';',skiprows=1)[0]
                    elif type_conductimetre()==2:
                        K = np.loadtxt('../data/data_etalonnage/dernier_etalonnage_K10.csv', delimiter = ';',skiprows=1)[0]
                        
                elif type_etalonnage==2:
                    date=int(input(''))
                    # A modifier
            elif choix_calib == '3' : # Arret du programme
                print('- Merci, et bonne journée !')
                break
            
            else :
                print('Merci de répondre uniquement 1, 2 ou 3')
                
                 
                    
            
        elif reponse == '2' : # Mesures
            try : 
                type_conductimeter=type_conductimetre()
                if type_conductimeter==1:
                    K= np.loadtxt('../data/data_etalonnage/dernier_etalonnage_K1.csv',usecols=0, delimiter = ';',skiprows=1)
                
                    print('Le dernier étalonnage a été enregistré, il sera réutilisé par défaut si vous n\'en refaite pas. Il est cependant conseillé d\'en refaire avant chaque utilisation du conductimètre.\nLa valeur de la constante K vaut :',K)
                elif type_conductimeter==10:
                    K= np.loadtxt('../data/data_etalonnage/dernier_etalonnage_K10.csv',usecols=0, delimiter = ';',skiprows=1)
                
                    print('Le dernier étalonnage a été enregistré, il sera réutilisé par défaut si vous n\'en refaite pas. Il est cependant conseillé d\'en refaire avant chaque utilisation du conductimètre.\nLa valeur de la constante K vaut :',K)
            except Exception :
                print('Aucun calibrage n\'est enregistré, il vous faut en faire un.')
                nbr_etalon = int(input("Combien d'étalons voulez-vous mesurer ? (au moins 3) : "))
                K= Etalonnage(nbr_etalon, nbr_mesure_par_etalon,conductimeter)
                print('- Vous avez fini le calibrage.')
            
            mesure=True
            k=0
            while mesure :
                k+=1
                print('\n[ Échantillon %d]'%k)
                Mesures(K, nbr_mesure_par_echantillon,conductimeter)
                print('- Vous avez fini vos mesures.\n')
                choix=input(interface_mesure)
                if choix == 'y' or choix=='Y':
                    mesure = True
                elif choix=='n' or choix == 'N' : 
                    mesure= False
                else:
                    print('Merci de répondre uniquement y ou n ')
                    mesure=False
        elif reponse == '3' : # Modification des valeurs par défaut
            choix_modif = input('\nQuelle valeur voulez-vous modifier ?\n1 : Nombre de valeurs par échantillon\n2 : Nombre de valeurs par étalon\nVotre réponse : ')
            if choix_modif == '1' :
                print('Actuellement, votre nombre de valeurs par échantillon est de : ', nbr_mesure_par_echantillon)
                nbr_mesure_par_echantillon = int(input('Combien de mesures voulez-vous effectuer ? : '))
            elif choix_modif == '2' : 
                print('Actuellement, votre nombre de valeurs par étalon est de : ', nbr_mesure_par_etalon)
                nbr_mesure_par_etalon = int(input('Combien de mesures voulez-vous effectuer pour chaque étalon ? : '))
            else :
                print('Veuillez répondre uniquement 1 ou 2')
            
        elif reponse == '4' : # Arret du programme
            print('- Merci, et bonne journée !')
            break
        
        else :
            print('Merci de répondre uniquement 1, 2, 3 ou 4\n')
    

