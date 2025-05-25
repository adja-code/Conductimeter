Etalonnage
==========

Un nouveau calibrage est conseillé à chaque nouvelle utilisation du conductimètre. 
Cependant, le programme enregistre à chaque fois le dernier étalonnage en date et le réutilise si 
vous n’en refaites pas.
 Les instructions pour l’étalonnage sont les suivantes :
 
Protocole
--------- 

1. Entrez le nombre d’étalon que vous voulez mesurer, il est conseillé d’en faire au moins 3. 

2. Indiquez la conductivité de votre premier étalon.
 Remarque : Si cette mesure correspond à 12,8 mS/cm, 1413 μS/cm ou 5000 μS/cm, les 
conductivités seront corrigées selon la température de la solution. Il vous faudra alors 
plonger le thermomètre dans la solution.

3. Versez votre étalon dans un bécher de 50mL.

4. Plongez le conductimètre et le thermomètre dans la solution en les immergeant bien 
comme sur le schéma suivant : 

5. Appuyez sur Entrée pour lancer la mesure.
 Cette étape peut prendre du temps.
 
6. L’écart type ainsi qu’un graphique vous sont affichés, il vous faut indiquer à l’ordinateur si la 
mesure est assez stable. 
Si la mesure n’est pas stable, elle sera effectuée une nouvelle fois.

7. Une fois que vous avez indiqué la série de mesure comme stable, vous pouvez passer à la 
solution étalon suivante en répétant les étapes 2 à 6.

8. Une fois tous vos étalons faits, la courbe d’étalonnage devrait s’afficher sur votre ordinateur. 


Ce calibrage est ainsi enregistré dans votre ordinateur sous le nom **dernier_étalonnage.csv’**
en écrasant le dernier fichier du même nom. Si vous voulez le conserver même si vous 
refaite un étalonnage, il vous suffit de le renommer.
 Une fois toutes ces étapes effectuées, vous avez fini le calibrage. Vous pouvez passer aux mesures. 
 
Principe général du code python 
-------------------------------

Le conductimètre que nous avons construit mesure une tension en bits convertie simplement en volt. Or il existe une relation linéaire entre cette tension et la conductivité d'une solution. L'étalonnage nous permet de réaliser une régression linéaire  à partir d'échatillons dont la conductivité est connue, nous permettant par la suite de déterminer la conductivité de n'importe quel échantillon. 

La conductivité varie de façon linéaire en fonction de la température. En revanche cette relation dépend de la conductivité initiale de notre échantillon. Le code python que nous avons développé intègre des corrections de température uniquement pour des solutions étalons de 12 880 us/cm, 1413us/cm et 5000 us/cm. Cela est problématique pour deux raisons. D'une part les solutions étalons mis à disposition des utilisateurs n'ont pas nécessairement ces valeurs de conductivité; D'autre part effectuer une correction de température uniquement pendant l'étalonnage suppose que la température  de la solution reste constante pendant toute la durée de la manipulation. 

.. figure:: images/correction_temp_12880.png

   :width: 600
  
.. figure:: images/correction_temp_1413.png

   :width: 600
  
.. figure:: images/correction_temp_5000.png

   :width: 600
  
 
Description de la fonction d'étalonnage
---------------------------------------

.. autofunction:: ADNI_ProgrammePython.Etalonnage


..
.. code-block:: python
   
   import numpy as np 
   import matplotlib.pyplot as plt 
   import time 
   
   def Etalonnage(nbr_etalon, nbr_mesure_par_etalon):
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
    



 
