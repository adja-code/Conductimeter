#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 27 12:47:52 2025

@author: dfed
"""
import numpy as np 
import matplotlib.pyplot as plt 


def correction_temperature(conductivite_25):
    conductimeter= port_connexion()[1]
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

    Conductivite=[12880,5000,1413]
    Coefficient_directeur=[droite_12880[1],droite_5000[1],droite_1413[1]]

    reg=np.polyfit(Conductivite,Coefficient_directeur,1)
    alpha=reg[0]
    
    list_temp =[] #liste pour relever la température moyenne de la solution
    conductimeter.flushInput()
    for i in range(100): 
        data = conductimeter.readline().decode().strip('\r\n').split(',')
        list_temp.append(data[0])
    Temperature_echantillon= np.mean(list_temp)
    
    conductivite_corrige=alpha*conductivite_25*Temperature_echantillon
    


plt.figure()
plt.plot(Conductivite,Coefficient_directeur,'o')
plt.xlabel('Conductivité en us/cm')
plt.ylabel('Coefficient_directeur correction de température')
plt.show()