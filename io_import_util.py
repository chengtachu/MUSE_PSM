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
    iDataYS_YS = list()
    for iYear in dfDatarow.index:
        if type(iYear) is int:
            if iYear > 1950 and iYear <= 2100:
                iDataYS_YS.append(iYear)

    for indexDefault, iDefaultYS in enumerate(iAllYearSteps_YS):
        for indexData, iDataYS in enumerate(iDataYS_YS):
            
            if iDataYS == iDefaultYS:
                iNewData_YS[indexDefault] = dfDatarow[iDataYS]
                break
            
            if iDataYS > iDefaultYS:
                # do interpolation if the given data does not match the instance timep preiod setting
                iPreYS = iDataYS_YS[indexData-1]
                iNextYS = iDataYS
                sPreTPData = dfDatarow[iPreYS]
                sNextTPData = dfDatarow[iNextYS]
                iNewData_YS[indexDefault] = sPreTPData + (sNextTPData-sPreTPData)*(iDefaultYS-iPreYS)/(iNextYS-iPreYS)
                break

    return iNewData_YS



def GetDataAdjustWithTimePeriodAndSlice(dfData , iAllYearSteps_YS, lsTimeSlice):
    ''' formate data in defined time period and time slice '''

    # imported data time period setting
    aColumns = list(dfData.columns.values)
    fDataYS_YS = list()
    for iYear in aColumns:
        if type(iYear) is int:
            fDataYS_YS.append(iYear)

    dfData = dfData.set_index("SN")
    aNewData = np.zeros((len(lsTimeSlice), len(iAllYearSteps_YS)))

    for indexYS, iDefaultYS in enumerate(iAllYearSteps_YS):
        for indexData, iDataYS in enumerate(fDataYS_YS):
            if iDataYS == iDefaultYS:
                aNewData[:, indexYS] = dfData.loc[:, iDataYS]
                break
            if iDataYS > iDefaultYS:
                # do interpolation if the given data does not match the instance timep preiod setting
                iPreYS = fDataYS_YS[indexData-1]
                iNextYS = iDataYS
                sPreTPData = dfData.loc[:, iPreYS]
                sNextTPData = dfData.loc[:, iNextYS]
                aNewData[:, indexYS] = sPreTPData[:] + (sNextTPData[:]-sPreTPData[:])*(iDefaultYS-iPreYS)/(iNextYS-iPreYS)
                break

    return aNewData



def get_RegionGenProcessIndex(objRegion, sProcessName):
    ''' return the index of process in region process list '''
    
    for index, objProcess in enumerate(objRegion.lsProcessAssump):
        if objProcess.sProcessName == sProcessName :
            iRegionProcessIndex = index
            break
        
    return iRegionProcessIndex



def Get_ZoneVREOutput(dfData, lsTimeSlice, sColumn):
    ''' return the default VRE output by time-slice '''
    
    dfData = dfData.set_index("SN")
    aNewData = np.zeros(len(lsTimeSlice))

    aColumns = list(dfData.columns.values)
    for sColumnName in aColumns:
        if str(sColumnName) == sColumn:
            aNewData[:] = dfData.loc[:, sColumnName]
            break

    return aNewData



