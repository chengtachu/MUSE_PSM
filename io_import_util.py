# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np


def getDataFrame(strFilePath , strSheetName):
    ''' import instance config '''

    fFile = pd.ExcelFile(strFilePath)
    if strSheetName != "":
        dfData = fFile.parse(strSheetName)
    else:
        dfData = fFile.parse()

    return dfData



def DataAdjustWithTimePeriod(dfDatarow , iAllYearSteps_YS):
    """adjusted imported data according to time pefiod setting"""

    iNewData_YS = np.zeros(len(iAllYearSteps_YS))

    # imported data year step setting (check the column headers)
    aDataTimePefiod = list()
    for iYear in dfDatarow.index:
        if type(iYear) is int:
            if iYear > 1950 and iYear <= 2100:
                aDataTimePefiod.append(iYear)

    for indexDefault, iDefaultTimePeriod in enumerate(iAllYearSteps_YS):
        for indexData, iDataTimePeriod in enumerate(aDataTimePefiod):
            
            if iDataTimePeriod == iDefaultTimePeriod:
                iNewData_YS[indexDefault] = dfDatarow[iDataTimePeriod]
                break
            
            if iDataTimePeriod > iDefaultTimePeriod:
                # do interpolation if the given data does not match the instance timep preiod setting
                iPreTimePeriod = aDataTimePefiod[indexData-1]
                iNextTimePeriod = iDataTimePeriod
                sPreTPData = dfDatarow[iPreTimePeriod]
                sNextTPData = dfDatarow[iNextTimePeriod]
                iNewData_YS[indexDefault] = sPreTPData + (sNextTPData-sPreTPData)*(iDefaultTimePeriod-iPreTimePeriod)/(iNextTimePeriod-iPreTimePeriod)
                break

    return iNewData_YS



def get_RegionGenProcessIndex(objRegion, sProcessName):
    ''' return the index of process in region process list '''
    
    for index, objProcess in enumerate(objRegion.lsProcessAssump):
        if objProcess.sProcessName == sProcessName :
            iRegionProcessIndex = index
            break
        
    return iRegionProcessIndex







