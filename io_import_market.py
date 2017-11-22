# -*- coding: utf-8 -*-


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
        
        if row["DataCode"] == "PowerLossRatio" :
            objZone.fPowerLossRatio_YS = io_import_util.DataAdjustWithTimePeriod(row,iAllYearSteps_YS)

    return





