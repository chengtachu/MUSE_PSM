# -*- coding: utf-8 -*-

import os

import cls_misc
import io_import_util


_sFolderPath = "Data/Assumption/"


def get_RegionTechAssump(objRegion, lsProcessDefObjs, iAllYearSteps_YS):
    ''' load region technical assumptions (process) '''
    
    sFilePath = _sFolderPath + "Region_Tech/" + objRegion.sRegion + ".xlsx"
    sSheetName = "GenTech"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
    dfData = dfData.drop(dfData.index[0])
    
    # load technical parameter
    for index, row in dfData.iterrows():
        dicParameters = {}
        for indexPR, sParameter in enumerate(row.index[1:]) :
            dicParameters[sParameter] = row[indexPR + 1]    # first column is ProcessName
        objRegion.lsProcessAssump.append(cls_misc.RegionProcess(row["ProcessName"], dicParameters))
            
    # update definition from instance process definition
    for objProcess in objRegion.lsProcessAssump :
        for indexInstanceTech, objInstanceTech in enumerate(lsProcessDefObjs):
            if objInstanceTech.sProcessName == objProcess.sProcessName :
                objProcess.sProcessType = objInstanceTech.sProcessType
                objProcess.bCCS = objInstanceTech.bCCS
                objProcess.sProcessFullName = objInstanceTech.sProcessFullName
                objProcess.sFuel = objInstanceTech.sFuel
                objProcess.sOperationMode = objInstanceTech.sOperationMode
                break
            
    # load process gross efficiencty parameter - power condense mode
    sSheetName = "GenTechGrossEff_Power_CM"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
    for index, row in dfData.iterrows():
        iRegionProcessIndex = io_import_util.get_RegionGenProcessIndex(objRegion, row["ProcessName"])
        objRegion.lsProcessAssump[iRegionProcessIndex].fEffPowerCM_YS = io_import_util.DataAdjustWithTimePeriod(row, iAllYearSteps_YS)

    # load process gross efficiencty parameter - power back-pressure mode
    sSheetName = "GenTechGrossEff_Power_BP"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
    for index, row in dfData.iterrows():
        iRegionProcessIndex = io_import_util.get_RegionGenProcessIndex(objRegion, row["ProcessName"])
        objRegion.lsProcessAssump[iRegionProcessIndex].fEffPowerBP_YS = io_import_util.DataAdjustWithTimePeriod(row, iAllYearSteps_YS)
        
    # load process gross efficiencty parameter - heat back-pressure mode
    sSheetName = "GenTechGrossEff_Heat_BP"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
    for index, row in dfData.iterrows():
        iRegionProcessIndex = io_import_util.get_RegionGenProcessIndex(objRegion, row["ProcessName"])
        objRegion.lsProcessAssump[iRegionProcessIndex].fEffHeatBP_YS = io_import_util.DataAdjustWithTimePeriod(row, iAllYearSteps_YS)
        
    return



def get_RegionCostAssump(objRegion, iAllYearSteps_YS):
    ''' load region cost assumptions (process) '''
    
    sFilePath = _sFolderPath + "Region_Cost/" + objRegion.sRegion + ".xlsx"

    # load process cost projections - CAPEX
    sSheetName = "CAPEX"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
    for index, row in dfData.iterrows():
        iRegionProcessIndex = io_import_util.get_RegionGenProcessIndex(objRegion, row["ProcessName"])
        objRegion.lsProcessAssump[iRegionProcessIndex].fCAPEX_YS = io_import_util.DataAdjustWithTimePeriod(row, iAllYearSteps_YS)

    # load process cost projections - OPEX
    sSheetName = "OPEX"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
    for index, row in dfData.iterrows():
        iRegionProcessIndex = io_import_util.get_RegionGenProcessIndex(objRegion, row["ProcessName"])
        objRegion.lsProcessAssump[iRegionProcessIndex].fOPEX_YS = io_import_util.DataAdjustWithTimePeriod(row, iAllYearSteps_YS)

    # load process cost projections - running cost
    sSheetName = "RunningCost"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
    for index, row in dfData.iterrows():
        iRegionProcessIndex = io_import_util.get_RegionGenProcessIndex(objRegion, row["ProcessName"])
        objRegion.lsProcessAssump[iRegionProcessIndex].fRunningCost_YS = io_import_util.DataAdjustWithTimePeriod(row, iAllYearSteps_YS)

    # load process cost projections - Discount rate
    sSheetName = "Discount"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
    for index, row in dfData.iterrows():
        iRegionProcessIndex = io_import_util.get_RegionGenProcessIndex(objRegion, row["ProcessName"])
        objRegion.lsProcessAssump[iRegionProcessIndex].fDiscountRate_YS = io_import_util.DataAdjustWithTimePeriod(row, iAllYearSteps_YS)

    # load process cost projections - Start Up Cost
    sSheetName = "StartUpCost"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
    for index, row in dfData.iterrows():
        iRegionProcessIndex = io_import_util.get_RegionGenProcessIndex(objRegion, row["ProcessName"])
        objRegion.lsProcessAssump[iRegionProcessIndex].fStartUpCost_YS = io_import_util.DataAdjustWithTimePeriod(row, iAllYearSteps_YS)

    # load process cost projections - No Load Cost
    sSheetName = "NoLoadCost"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
    for index, row in dfData.iterrows():
        iRegionProcessIndex = io_import_util.get_RegionGenProcessIndex(objRegion, row["ProcessName"])
        objRegion.lsProcessAssump[iRegionProcessIndex].fNoLoadCost_YS = io_import_util.DataAdjustWithTimePeriod(row, iAllYearSteps_YS)

    return



def get_CountryTechAssump(objRegion, objCountry, iAllYearSteps_YS):
    ''' load country technical assumptions (process) '''
            
    sFilePath = _sFolderPath + "Country_Tech/" + objCountry.sCountry + ".xlsx"
        
    # check file exist    
    if os.path.exists(sFilePath):

        # check and override technical parameter
        sSheetName = "GenTech"
        dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
        dfData = dfData.drop(dfData.index[0])
        
        for index, row in dfData.iterrows():
            iProcessIndex = io_import_util.get_RegionGenProcessIndex(objRegion, row["ProcessName"])
            
            dicParameters = {}
            for indexPR, sParameter in enumerate(row.index[1:]) :
                dicParameters[sParameter] = row[indexPR + 1]    # first column is ProcessName
            
            for sParameter, value in dicParameters.items():
                setattr(objCountry.lsProcessAssump[iProcessIndex], sParameter, value)


        # load process gross efficiencty parameter - power condense mode
        sSheetName = "GenTechGrossEff_Power_CM"
        dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
        for index, row in dfData.iterrows():
            iRegionProcessIndex = io_import_util.get_RegionGenProcessIndex(objRegion, row["ProcessName"])
            objCountry.lsProcessAssump[iRegionProcessIndex].fEffPowerCM_YS = io_import_util.DataAdjustWithTimePeriod(row, iAllYearSteps_YS)

        # load process gross efficiencty parameter - power back-pressure mode
        sSheetName = "GenTechGrossEff_Power_BP"
        dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
        for index, row in dfData.iterrows():
            iRegionProcessIndex = io_import_util.get_RegionGenProcessIndex(objRegion, row["ProcessName"])
            objCountry.lsProcessAssump[iRegionProcessIndex].fEffPowerBP_YS = io_import_util.DataAdjustWithTimePeriod(row, iAllYearSteps_YS)
            
        # load process gross efficiencty parameter - heat back-pressure mode
        sSheetName = "GenTechGrossEff_Heat_BP"
        dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
        for index, row in dfData.iterrows():
            iRegionProcessIndex = io_import_util.get_RegionGenProcessIndex(objRegion, row["ProcessName"])
            objCountry.lsProcessAssump[iRegionProcessIndex].fEffHeatBP_YS = io_import_util.DataAdjustWithTimePeriod(row, iAllYearSteps_YS)
        
    return



def get_CountryCostAssump(objRegion, objCountry, iAllYearSteps_YS):
    ''' load country cost assumptions (process) '''
    
        
    sFilePath = _sFolderPath + "Country_Cost/" + objCountry.sCountry + ".xlsx"
        
    # check file exist    
    if os.path.exists(sFilePath):

        # load process cost projections - CAPEX
        sSheetName = "CAPEX"
        dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
        for index, row in dfData.iterrows():
            iRegionProcessIndex = io_import_util.get_RegionGenProcessIndex(objRegion, row["ProcessName"])
            objCountry.lsProcessAssump[iRegionProcessIndex].fCAPEX_YS = io_import_util.DataAdjustWithTimePeriod(row, iAllYearSteps_YS)
    
        # load process cost projections - OPEX
        sSheetName = "OPEX"
        dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
        for index, row in dfData.iterrows():
            iRegionProcessIndex = io_import_util.get_RegionGenProcessIndex(objRegion, row["ProcessName"])
            objCountry.lsProcessAssump[iRegionProcessIndex].fOPEX_YS = io_import_util.DataAdjustWithTimePeriod(row, iAllYearSteps_YS)
    
        # load process cost projections - running cost
        sSheetName = "RunningCost"
        dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
        for index, row in dfData.iterrows():
            iRegionProcessIndex = io_import_util.get_RegionGenProcessIndex(objRegion, row["ProcessName"])
            objCountry.lsProcessAssump[iRegionProcessIndex].fRunningCost_YS = io_import_util.DataAdjustWithTimePeriod(row, iAllYearSteps_YS)
    
        # load process cost projections - Discount rate
        sSheetName = "Discount"
        dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
        for index, row in dfData.iterrows():
            iRegionProcessIndex = io_import_util.get_RegionGenProcessIndex(objRegion, row["ProcessName"])
            objCountry.lsProcessAssump[iRegionProcessIndex].fDiscountRate_YS = io_import_util.DataAdjustWithTimePeriod(row, iAllYearSteps_YS)
    
        # load process cost projections - Start Up Cost
        sSheetName = "StartUpCost"
        dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
        for index, row in dfData.iterrows():
            iRegionProcessIndex = io_import_util.get_RegionGenProcessIndex(objRegion, row["ProcessName"])
            objCountry.lsProcessAssump[iRegionProcessIndex].fStartUpCost_YS = io_import_util.DataAdjustWithTimePeriod(row, iAllYearSteps_YS)
    
        # load process cost projections - No Load Cost
        sSheetName = "NoLoadCost"
        dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
        for index, row in dfData.iterrows():
            iRegionProcessIndex = io_import_util.get_RegionGenProcessIndex(objRegion, row["ProcessName"])
            objCountry.lsProcessAssump[iRegionProcessIndex].fNoLoadCost_YS = io_import_util.DataAdjustWithTimePeriod(row, iAllYearSteps_YS)
        
        
    # calculate Capital Recovery Factor
    for objProcess in objCountry.lsProcessAssump:

        iPlantLife = objProcess.TechnicalLife
        fDiscountRateP_YS = objProcess.fDiscountRate_YS[:] / 100
        objProcess.fCRF_YS = ( fDiscountRateP_YS[:] * pow((1+fDiscountRateP_YS[:]), iPlantLife) ) / ( pow((1+fDiscountRateP_YS[:]), iPlantLife) - 1)
    
        print("")
    
    return



def get_CountryCarbonPrice(objCountry, iAllYearSteps_YS):
    ''' update carbon price in a country '''

    _sFolderPath = "Data/Input/"
    sFilePath = _sFolderPath + "Country_CarbonPrice/" + objCountry.sCountry + ".xlsx"

    sSheetName = "Policy"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
    for index, row in dfData.iterrows():
        
        if row["DataCode"] == "PowerCarbonCost" :
            objCountry.fCarbonCost_YS = io_import_util.DataAdjustWithTimePeriod(row,iAllYearSteps_YS)

    return



def get_CountryFuelPrice(instance, objCountry):
    ''' update carbon price in a country '''

    # check if commodity object exist in the country
    if hasattr(objCountry, 'lsCommodity'):
        objCountry.lsCommodity = list(instance.lsCommodity)

    _sFolderPath = "Data/Input/"
    sFilePath = _sFolderPath + "Country_FuelPrice/" + objCountry.sCountry + ".xlsx"





    return




