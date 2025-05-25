Mesures 
=======

 
   

Mode d'emploi pour réaliser  les mesures de conductivité 
--------------------------------------------------------

Pour mesurer la conductivité de vos différents échantillon vous devez : 
vous devez : 

1. Saisir le nombre d'échantillons à mesurer.

2. Introduire dans un bécher de 50 mL une quantité suffisante de solution à mesurer afin  
d’assurer l'immersion totale des deux électrodes du conductimètre, comme sur le schéma 
suivant : 

.. figure :: images/ comment_plonger_electrode.png

   :width: 800

3. Plonger le conductimètre dans la solution.

4. Appuyer sur Entrée pour lancer la mesure.

5. Attendre que la conductivité moyenne s'affiche sur votre écran. Cette étape peut être assez 
longue et dépend du nombre de valeurs prise pour calculer la conductivité (modifiable 
depuis l’accueil).

6. Nettoyer l'électrode à l'eau distillée et la sécher.

7. Passer à l'échantillon suivant.

 Vos mesures ont été effectuées avec succès. Vous pouvez réaliser une nouvelle série de 
mesures ou procéder au rangement du matériel. N'oubliez pas de rincer les électrodes et le 
thermomètre à l'eau distillée et de tout sécher avant de ranger le matériel.

Principe du code Python 
-----------------------
La majeure partie du travail a été effectuée pendant l'étalonnage. Cette partie consiste à mesurer un certain nombre de valeurs de conductivité en tension, à les convertir grâce à la relation linéaire trouvée pendant l'étalonnage et à renvoyer la moyenne et l'écart type de cette valeur. 

Code Python documenté
---------------------

.. code-block:: python

   import numpy as np
   import time 
   import matplotlib.pyplot as plt 
   import serial 
   
   def Mesures(nbr_echantillon, droite, nbr_mesure_par_echantillon):
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
    conductimeter = setup()
    list_temp = []
    list_conductivite = []
    numerotation = []
    donnees = []
    
    for k in range(nbr_echantillon):
        print('\n[ Échantillon',k+1,']')
        input('Veuillez préparer votre échantillon, puis appuyer sur Entrée pour lancer la mesure.')
        print('Vos mesures sont en cours, patientez s\'il vous plait.')
        conductimeter.flushInput()
        for i in range(nbr_mesure_par_echantillon): 
            data = conductimeter.readline().decode().strip('\r\n').split(',')
            list_temp.append(float(data[0]))
            list_conductivite.append(droite[0]*(float(data[1])) + droite[1])
            numerotation.append(k*0.01)
            time.sleep(0.01)
        print('-> Resultat : La température moyenne est : ', np.mean(list_temp), '°C, et la conductivité moyenne est de : ', np.mean(list_conductivite),'uS/cm.')
        donnees.append([k, np.mean(list_temp), np.mean(list_conductivite)])
    np.savetxt('./data_conductivité.csv', donnees, delimiter = ';',fmt = '%.2f', header='Mesure n°;Température(°C);Conductivité(uS/cm)',)
    print('Vos mesures sont désormais stockées dans le fichier data_conductivité.csv.\nAttention, si vous ne modifiez pas le nom du fichier, elles seront écrasées à la prochaine série de mesures.\n')
    return 
   
  
