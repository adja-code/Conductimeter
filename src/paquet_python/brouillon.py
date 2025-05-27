#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue May 27 11:34:58 2025

@author: dfed
"""

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