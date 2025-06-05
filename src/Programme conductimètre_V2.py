import sys
sys.path.append(".")
from lib_conductimetre import *



if __name__ == '__main__':

    plt.ion() 

    try:
        port, s = port_connexion()
        print(" conductimètre connecté  au port %s" % (port))
    except:
        print("Attention aucun arduino disponible")
    
    interface ="""
    ===========================================================================
    MENU PRINCIPAL
    ===========================================================================
    Que souhaitez-vous faire ?
    1 - Calibrer
    2 - Mesurer
    3 - Représenter graphiquement
    4 - Quitter
    ===========================================================================
    ? """
    
    
    
##################################################################
#
# A ADAPTER AU CONDUCTIMETRE 
#
##################################################################

    """
    Fonction d'accueil du conductimètre, lance le programme complet.'

    Returns
    -------
    None.

    """
    
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
    Votre réponse >>> ? """
    
    interface_calibration ="""
    ===========================================================================
    CALIBRATION
    ===========================================================================
    Que voulez-vous faire ? :
    1 - Nouvel étalonnage
    2 - Utiliser un étalonnage par défaut 
    3 - Quitter
    ===========================================================================
    Votre réponse >>> ? """
    
    interface_type_etalonnage="""
    ===========================================================================
    Quel étalonnage par défaut 
    ===========================================================================
    1 - Utiliser l'étalonnage le plus récent
    2 - Choisir un étalonnage particulier en fonction de son nombre d'é'
    ===========================================================================
    Votre réponse >>> ? """
        
    while(True) : 
        reponse = input(interface_acceuil)
        
        if reponse == '1' : # Calibration
            choix_calib=int(input(interface_calibration))
            if choix_calib==1 : 
                nbr_etalon = int(input("Combien d'étalons voulez-vous mesurer ? (au moins 1) : "))
                droite_etalonnage= Etalonnage(nbr_etalon, nbr_mesure_par_etalon)
                print('- Vous avez fini le calibrage.\n')
            elif choix_calib==2:
                type_etalonnage=int(input(interface_type_etalonnage))
                if type_etalonnage==1:
                    print("Utilisation du dernier étalonnage en date ") #A remplacer par le chargement du dernier coefficient a
                elif type_etalonnage==2:
                    nombre_etalons=int(input('Vous souhaitez charger un étalonnage avec combien de solutions étalons'))
                    print('Par défaut nous chargerons l\'étalonnage le plus récent') # A modifier par l'etalonnage le plus récent 
            elif choix_calib == '3' : # Arret du programme
                print('- Merci, et bonne journée !')
                break
            
            else :
                print('Merci de répondre uniquement 1, 2 ou 3')
                
                 
                    
            
        elif reponse == '2' : # Mesures
            nbr_echantillon = int(input('Combien d\'échantillons voulez-vous mesurer ? : '))
            Mesures(nbr_echantillon, droite, nbr_mesure_par_echantillon)
            print('- Vous avez fini vos mesures.\n')
            
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
    

