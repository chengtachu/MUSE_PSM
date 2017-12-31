# -*- coding: utf-8 -*-

import os
import glob

import numpy as np

_sDataFilePath = "Data/Output"

def CheckMarketFolderAndDeleteExistFiles(sMarket):

    directory = _sDataFilePath + "/" + sMarket

    if not os.path.exists(directory):
        os.makedirs(directory)
    else:
        allFiles = glob.glob(directory + "/*")
        for filename in allFiles:
            os.remove(filename)


def TableOutputToCSV(sMarket, tableOutput, sFileName):

    directory = _sDataFilePath + "/" + sMarket
    sFilePath = directory + "/" + sFileName + ".csv"
    
    # create file
    if not os.path.exists(sFilePath):
        open(sFilePath, 'w').close() 

    # save content
    np.savetxt( sFilePath, tableOutput, fmt='%s', delimiter=',', newline='\n')



