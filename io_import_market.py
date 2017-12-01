# -*- coding: utf-8 -*-

import copy

import io_import_util
import cls_misc

_sFolderPath = "Data/Assumption/"

def get_MarketPolicy(objMarket, iAllYearSteps_YS):
    ''' import market policy settings '''

    sFilePath = _sFolderPath + "Market/" + objMarket.sMarket + ".xlsx"

    #### Policy constraints
    sSheetName = "Policy"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
    for index, row in dfData.iterrows():
        
        if row["DataCode"] == "30sRegulationRequire" :
            objMarket.fRegulationRequire_YS = io_import_util.DataAdjustWithTimePeriod(row,iAllYearSteps_YS)

        elif row["DataCode"] == "10mReserve" :
            objMarket.f10mReserve_YS = io_import_util.DataAdjustWithTimePeriod(row,iAllYearSteps_YS)

        elif row["DataCode"] == "30mReserve" :
            objMarket.f30mReserve_YS = io_import_util.DataAdjustWithTimePeriod(row,iAllYearSteps_YS)

        elif row["DataCode"] == "CO2EmissionLimit" :
            objMarket.fCO2EmissionLimit_YS = io_import_util.DataAdjustWithTimePeriod(row,iAllYearSteps_YS)

    return



def get_MarketTransmission(objMarket):
    ''' get assumptions on cross-border physical transmission '''

    sFilePath = _sFolderPath + "Market_Transmission/" + objMarket.sMarket + ".xlsx"

    sSheetName = "PowerTransmission"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)

    for index, row in dfData.iterrows():
        
        lsZoneID = [objZone.sZone for objZone in objMarket.lsZone ]
        if row["From"] in lsZoneID and row["To"] in lsZoneID:
            dicParameters = {}
            for indexPR, sParameter in enumerate(row.index[:]) :
                dicParameters[sParameter] = row[indexPR]
                
            objMarket.lsTransmission.append(cls_misc.Transmission(dicParameters))

    return



def get_ZoneTechAssump(objZone, iAllYearSteps_YS):
    ''' import market policy settings '''

    sFilePath = _sFolderPath + "Zone/" + objZone.sZone + ".xlsx"

    #### Policy constraints
    sSheetName = "TechAssumption"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
    for index, row in dfData.iterrows():
        
        if row["DataCode"] == "PowerDistLossRate" :
            objZone.fPowerDistLossRate_YS = io_import_util.DataAdjustWithTimePeriod(row,iAllYearSteps_YS)
            
        elif row["DataCode"] == "HeatDistLossRate" :
            objZone.fHeatDistLossRate_YS = io_import_util.DataAdjustWithTimePeriod(row,iAllYearSteps_YS)

    return


def get_ZoneProcessAvail(instance, objZone):
    ''' import market policy settings '''

    sFilePath = _sFolderPath + "Zone/" + objZone.sZone + ".xlsx"

    #### Policy constraints
    sSheetName = "AvailableProcess"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
    for index, row in dfData.iterrows():

        for objCountryProcess in instance.lsRegion[objZone.iRegionIndex].lsCountry[objZone.iCountryIndex].lsProcessAssump:
            if objCountryProcess.sProcessName == row["ProcessName"]:
                objZone.lsProcessAssump.append(copy.copy(objCountryProcess))
                break

    return



def get_ZoneExistProcess(instance, objZone):
    ''' import exist process in the zone '''

    sFilePath = _sFolderPath + "Zone_ExistProcess/" + objZone.sZone + ".xlsx"

    #### Policy constraints
    sSheetName = "ProcessList"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
    dfData = dfData.drop(dfData.index[0])
    
    for index, row in dfData.iterrows():
        dicParameters = {}
        for indexPR, sParameter in enumerate(row.index[3:]) :
            dicParameters[sParameter] = row[indexPR + 3]    # first three column are company, ProcessName and ProcessID
        objZoneProcess = cls_misc.ZoneProcess( row["Company"], row["ProcessName"], row["ProcessID"], dicParameters)
        
        for objProcessDef in instance.lsProcessDefObjs:
            if row["ProcessName"] == objProcessDef.sProcessName:
                objZoneProcess.sFuel = objProcessDef.sFuel
                objZoneProcess.sOperationMode = objProcessDef.sOperationMode
                break

        objZone.lsProcess.append(objZoneProcess)

    return



def get_ZoneProcessLimit(objZone, iAllYearSteps_YS):
    ''' import process development limit in the zone '''

    sFilePath = _sFolderPath + "Zone_Limit/" + objZone.sZone + ".xlsx"

    # maximun capacity by year steps
    sSheetName = "MaxCapacity"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
    for index, row in dfData.iterrows():
        for objProcessAssump in objZone.lsProcessAssump:
            if objProcessAssump.sProcessName == row["ProcessName"] :
                objProcessAssump.fMaxCapacity_YS = io_import_util.DataAdjustWithTimePeriod(row,iAllYearSteps_YS)
                break
            
    # maximun new install capacity per year steps
    sSheetName = "MaxBuildRate"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
    for index, row in dfData.iterrows():
        for objProcessAssump in objZone.lsProcessAssump:
            if objProcessAssump.sProcessName == row["ProcessName"] :
                objProcessAssump.fMaxBuildRate_YS = io_import_util.DataAdjustWithTimePeriod(row,iAllYearSteps_YS)
                break

    return



def get_ZoneVREOutput(objZone, lsTimeSlice):
    ''' import VRE output in the zone '''

    sFilePath = _sFolderPath + "Zone_VRE/" + objZone.sZone + ".xlsx"

    # Wind
    sSheetName = "RenewableWindCF"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
    objZone.aReWindOutput2025_TS = io_import_util.Get_ZoneVREOutput(dfData, lsTimeSlice, "2025")
    objZone.aReWindOutput2530_TS = io_import_util.Get_ZoneVREOutput(dfData, lsTimeSlice, "2530")
    objZone.aReWindOutput3035_TS = io_import_util.Get_ZoneVREOutput(dfData, lsTimeSlice, "3035")
    objZone.aReWindOutput3540_TS = io_import_util.Get_ZoneVREOutput(dfData, lsTimeSlice, "3540")
    objZone.aReWindOutput40UP_TS = io_import_util.Get_ZoneVREOutput(dfData, lsTimeSlice, "40UP")

    # Offshore Wind
    sSheetName = "RenewableOffWindCF"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
    objZone.aReOffWindOutput2025_TS = io_import_util.Get_ZoneVREOutput(dfData, lsTimeSlice, "2025")
    objZone.aReOffWindOutput2530_TS = io_import_util.Get_ZoneVREOutput(dfData, lsTimeSlice, "2530")
    objZone.aReOffWindOutput3035_TS = io_import_util.Get_ZoneVREOutput(dfData, lsTimeSlice, "3035")
    objZone.aReOffWindOutput3540_TS = io_import_util.Get_ZoneVREOutput(dfData, lsTimeSlice, "3540")
    objZone.aReOffWindOutput4045_TS = io_import_util.Get_ZoneVREOutput(dfData, lsTimeSlice, "4045")
    objZone.aReOffWindOutput4550_TS = io_import_util.Get_ZoneVREOutput(dfData, lsTimeSlice, "4550")
    objZone.aReOffWindOutput50UP_TS = io_import_util.Get_ZoneVREOutput(dfData, lsTimeSlice, "50UP")

    # PV
    sSheetName = "RenewablePVCF"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
    objZone.aRePVOutput_TS = io_import_util.Get_ZoneVREOutput(dfData, lsTimeSlice, "Mean")

    
    # Hydro
    sSheetName = "RenewableHydro"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
    objZone.aReHydroOutput_TS = io_import_util.Get_ZoneVREOutput(dfData, lsTimeSlice, "Mean")
        
    return



def update_ZonePowerHeatDemand(objZone, lsTimeSlice, iAllYearSteps_YS):
    ''' import process development limit in the zone '''

    _sFolderPath = "Data/Input/"

    # update power demand
    sFilePath = _sFolderPath + "Zone_DemandPower/" + objZone.sZone + ".xlsx"
    sSheetName = "DemandProfile"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
    objZone.fPowerDemand_TS_YS = io_import_util.GetDataAdjustWithTimePeriodAndSlice(dfData, iAllYearSteps_YS, lsTimeSlice)
    
    # update heat demand
    sFilePath = _sFolderPath + "Zone_DemandHeat/" + objZone.sZone + ".xlsx"
    sSheetName = "DemandProfile"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
    objZone.fHeatDemand_TS_YS = io_import_util.GetDataAdjustWithTimePeriodAndSlice(dfData, iAllYearSteps_YS, lsTimeSlice)

    return



def update_ZonePowerImport(objZone, lsTimeSlice, iAllYearSteps_YS):
    ''' import power import/export from other market(model) in the zone '''

    _sFolderPath = "Data/Input/"
    
    # update power import
    sFilePath = _sFolderPath + "Zone_Trade/" + objZone.sZone + ".xlsx"
    sSheetName = "DemandProfile"
    dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
    objZone.fCrossMarketPowerImport_TS_YS = io_import_util.GetDataAdjustWithTimePeriodAndSlice(dfData, iAllYearSteps_YS, lsTimeSlice)
    
    return



