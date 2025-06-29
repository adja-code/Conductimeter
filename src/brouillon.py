#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 27 12:47:52 2025

@author: dfed
"""
import numpy as np 
import matplotlib.pyplot as plt 




def correction_temperature():
    # conductimeter= port_connexion()[1]
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

    C25=[12880,5000,1413]
    C0=[7150,2760,776]
    C30=[14120,5479,1575]
    Coefficient_directeur=[droite_12880[1],droite_5000[1],droite_1413[1]]
    

    a_12880,b_12880=reg_12880[0],reg_12880[1]
    a_5000,b_5000=reg_5000[0],reg_5000[1]
    a_1413,b_1413=reg_1413[0],reg_1413[1]
    
    print ('a_12880 =',a_12880,'b_12880',b_12880)
    print ('a_5000 =',a_5000 ,'b_5000 ',b_5000)
    print ('a_1413 =',a_1413 ,'b_1413 ',b_1413)
    
    reg=np.polyfit(Coefficient_directeur,C25,1)
    x = np.linspace (0, np.max(Coefficient_directeur)+0.25*np.max(Coefficient_directeur),10000)
    y= reg[0]*x+reg[1]
   
    plt.figure()
    plt.plot(Coefficient_directeur,C25,'o',color='purple')
    plt.plot(x,y,'--',color='purple')
    plt.axis([0, np.max(Coefficient_directeur)+0.25*np.max(Coefficient_directeur), 0, np.max(C25) +0.25*np.max(C25)])
    plt.xlabel('Conductivité de l\'échantillon à 25 °C')
    plt.ylabel('Coefficient directeur a')
    plt.savefig('a_conductivite.pdf')
    plt.show()
    
    #droite=np.poly1d(reg)
    # alpha=reg[0]
    
    # list_temp =[] #liste pour relever la température moyenne de la solution
    # conductimeter.flushInput()
    # for i in range(100): 
    #     data = conductimeter.readline().decode().strip('\r\n').split(',')
    #     list_temp.append(data[0])
    # Temperature_echantillon= np.mean(list_temp)
    
    # conductivite_corrige=alpha*conductivite_25*Temperature_echantillon
    
    # print('alpha=', reg[0])
    # print('beta=', reg[1])
    # plt.figure()
    # plt.plot(Conductivite,Coefficient_directeur,'o',color='purple')
    # plt.plot(Conductivite,droite(Conductivite),'--',color='purple')
    # plt.xlabel('Conductivité à 25° en us/cm')
    # plt.ylabel('Coefficient directeur correction de température')
    
    x=np.linspace(0,np.max(Temperature)+0.25*np.max(Temperature),10000)
    y_12880=droite_12880(x)
    y_5000=droite_5000(x)
    y_1413=droite_1413(x)
   
    plt.figure()
    plt.plot(Temperature,np.array(Conductivite_12880),'o',color= 'r')
    plt.plot(x,y_12880,'--', label='étalon 12880 us/cm à 25°C',color='r')
    plt.plot(Temperature,np.array(Conductivite_5000),'o',color='g')
    plt.plot(x,y_5000,'--', label='étalon 5000 us/cm à 25°C',color='g')
    plt.plot(Temperature,np.array(Conductivite_1413),'o',color='b')
    plt.plot(x,y_1413,'--',label='étalon 1413 us/cm à 25°C',color='b')
    plt.axis([0, np.max(Temperature)+0.25*np.max(Temperature), 0, np.max(Conductivite_12880) +0.25*np.max(Conductivite_12880)])
    plt.legend()
    plt.ylabel('Conductivité (us/cm)')
    plt.xlabel('Température (°C)')

    plt.savefig('../data/figures/Conductivite_temperature.pdf')
    plt.show()
    
    # plt.figure()
    # plt.plot(Temperature,np.array(Conductivite_12880)/C25[0],'o',color= 'r')
    # # plt.plot(Temperature,droite_12880(Temperature),'--', label='étalon 12880 us/cm à 25°C',color='r')
    # plt.plot(Temperature,np.array(Conductivite_5000)/C25[1],'o',color='g')
    # # plt.plot(Temperature,droite_5000(Temperature),'--', label='étalon 5000 us/cm à 25°C',color='g')
    # plt.plot(Temperature,np.array(Conductivite_1413)/C25[2],'o',color='b')
    # # plt.plot(Temperature,droite_1413(Temperature),'--',label='étalon 1413 us/cm à 25°C',color='b')
    # plt.legend()
    # plt.xlabel('Température en °C')
    # plt.ylabel('C/C25')
    # plt.show()
    
    
    # reg=np.polyfit(Conductivite,Coefficient_directeur,1)
    # droite=np.poly1d(reg)
    
    Moy_coeff= np.mean(Coefficient_directeur)
    Moy_C25=np.mean(C25)
    alpha25 = Moy_coeff/Moy_C25
    
    print('alpha25 =',alpha25)
    
    Moy_C0=np.mean(C0)
    alpha0 = Moy_coeff/Moy_C0
    
    print('alpha0 =',alpha0)
    
    
    Moy_C30=np.mean(C30)
    alpha30 = Moy_coeff/Moy_C30
    
    print('alpha30 =',alpha30)
    
    # alpha=reg[0]
    # beta=reg[1]
    # print('alpha=', reg[0])
    # print('beta=', reg[1])
    
    # plt.figure()
    # plt.plot(C25,Coefficient_directeur ,'o',color='red')
    # plt.plot(C25,Coefficient_directeur,'--',color='red',label='coefficient directeur 25°C')
    # plt.legend()
    # plt.xlabel('Conductivité à température fixée')
    # plt.ylabel('Coefficient_directeur a')
    
 
    # plt.plot(C0,Coefficient_directeur ,'o',color='purple')
    # plt.plot(C0,Coefficient_directeur ,'--',color='purple',label='coefficient directeur 0°C')
    # plt.legend()
    # plt.xlabel('Conductivité à température fixée')
    # plt.ylabel('Coefficient_directeur a')

    # plt.plot(C30,Coefficient_directeur ,'o',color='yellow')
    # plt.plot(C30,Coefficient_directeur ,'--',color='yellow',label='coefficient directeur 30°C')
    # plt.legend()
    # plt.xlabel('Conductivité à température fixée')
    # plt.ylabel('Coefficient_directeur a')

    # plt.figure()
    # T=[0,25,30]
    # plt.plot(T,[alpha0,alpha25,alpha30] ,'o',color='purple')
    # plt.plot(T,[alpha0,alpha25,alpha30] ,'--',color='purple',label='alpha')
    # plt.legend()
    # plt.xlabel('Température')
    # plt.ylabel('Coefficient_directeur alpha')
    

    # plt.plot(Conductivite,Coefficient_directeur,'o',color='purple')
    # plt.plot(Conductivite,droite(Conductivite),'--',color='purple')
    # plt.xlabel('Conductivité à 25° en us/cm')
    # plt.ylabel('Coefficient directeur correction de température')
    
    # Conductivite=[]
    # Coefficient_alpha=[]
    # Coefficient_alpha_bis=[]
    # Coefficient_beta=[]
    # for i in range(len(Temperature)):
    #     Conductivite.append(Conductivite_12880[i])
    #     Conductivite.append(Conductivite_5000[i])
    #     Conductivite.append(Conductivite_1413[i])
    #     Coefficient_alpha.append(np.polyfit(Conductivite,Coefficient_directeur,1)[0])
    #     Coefficient_alpha_bis.append(np.mean(Coefficient_directeur)/np.mean(Conductivite))
    #     Coefficient_beta.append(np.polyfit(Conductivite,Coefficient_directeur,1)[1])
    #     Conductivite=[]
    
    # reg_alpha=np.polyfit(Temperature,Coefficient_alpha,2)
    # polynome_alpha=np.poly1d(reg_alpha)
    # print('Équation régression :',reg_alpha[0],'*x**2',reg_alpha[1],'*x',reg_alpha[2])
    
    # reg_alpha_bis=np.polyfit(Temperature,Coefficient_alpha_bis,2)
    
    # plt.figure()
    # plt.plot(Temperature,Coefficient_alpha ,'o',color='pink')
    # plt.plot(Temperature,Coefficient_alpha_bis ,'o',color='purple')
    # plt.xlabel('Température')
    # plt.ylabel('Coefficient_alpha')
    # plt.plot(Temperature,reg_alpha[0]*np.array(Temperature)**2+reg_alpha[1]*np.array(Temperature)+reg_alpha[2],'--',color='pink')
 
    
    # ## C / C0 
    # plt.figure()
    # plt.plot(Temperature,np.array(Conductivite_12880)/Conductivite_12880[0],'o',color= 'b', label='C/C0')
    # # plt.plot(Temperature,droite_12880(Temperature),'--', label='étalon 12880 us/cm à 0°C',color='r')
    # plt.plot(Temperature,np.array(Conductivite_5000)/Conductivite_5000[0],'o',color='b')
    # # plt.plot(Temperature,droite_5000(Temperature),'--', label='étalon 5000 us/cm à 0°C',color='g')
    # plt.plot(Temperature,np.array(Conductivite_1413)/Conductivite_1413[0],'o',color='b')
    # # plt.plot(Temperature,droite_1413(Temperature),'--',label='étalon 1413 us/cm à 0°C',color='b')
    # plt.legend()
    # plt.xlabel('Température en °C')
    # plt.ylabel('Conductivité normalisée')
   
    
    # # C / C20
    # plt.plot(Temperature,np.array(Conductivite_12880)/Conductivite_12880[10],'o',color= 'r', label='C/C20')
    # # plt.plot(Temperature,droite_12880(Temperature),'--', label='étalon 12880 us/cm à 20°C',color='r')
    # plt.plot(Temperature,np.array(Conductivite_5000)/Conductivite_5000[10],'o',color='r')
    # # plt.plot(Temperature,droite_5000(Temperature),'--', label='étalon 5000 us/cm à 20°C',color='g')
    # plt.plot(Temperature,np.array(Conductivite_1413)/Conductivite_1413[10],'o',color='r')
    # # plt.plot(Temperature,droite_1413(Temperature),'--',label='étalon 1413 us/cm à 20°C',color='b')
    # plt.legend()

    # # C / C25
    # plt.plot(Temperature,np.array(Conductivite_12880)/Conductivite_12880[14],'o',color= 'g', label='C/C25')
    # # plt.plot(Temperature,droite_12880(Temperature),'--', label='étalon 12880 us/cm à 20°C',color='r')
    # plt.plot(Temperature,np.array(Conductivite_5000)/Conductivite_5000[14],'o',color='g')
    # # plt.plot(Temperature,droite_5000(Temperature),'--', label='étalon 5000 us/cm à 20°C',color='g')
    # plt.plot(Temperature,np.array(Conductivite_1413)/Conductivite_1413[14],'o',color='g')
    # # plt.plot(Temperature,droite_1413(Temperature),'--',label='étalon 1413 us/cm à 20°C',color='b')
    # plt.legend()
    
    # # C / C25
    # plt.plot(Conductivite,np.array(Coefficient_directeur)/Conductivite_12880[14],'o',color= 'g', label='C/C25')
    # # plt.plot(Temperature,droite_12880(Temperature),'--', label='étalon 12880 us/cm à 20°C',color='r')
    # plt.plot(Temperature,np.array(Conductivite_5000)/Conductivite_5000[14],'o',color='g')
    # # plt.plot(Temperature,droite_5000(Temperature),'--', label='étalon 5000 us/cm à 20°C',color='g')
    # plt.plot(Temperature,np.array(Conductivite_1413)/Conductivite_1413[14],'o',color='g')
    # # plt.plot(Temperature,droite_1413(Temperature),'--',label='étalon 1413 us/cm à 20°C',color='b')
    # plt.legend()

   
    
    # plt.show()
    
    