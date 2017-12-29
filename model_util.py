# -*- coding: utf-8 -*-

import copy
import math
import numpy as np

import cls_misc

# ----------------------------------------------------------------------------------------------------------------------
# model_fisrt_Init
# ----------------------------------------------------------------------------------------------------------------------

def model_fisrt_Init(objMarket, instance):
    ''' market initiation in first iteration '''
    
    # first time to run of the model (base year, and no output)
    if instance.iForesightStartYear == instance.iBaseYear and objMarket.MarketOutput.dicGenCapacity_YS_PR == {} :

        # create zone variables
        for objZone in objMarket.lsZone:
            createZoneVars(instance, objZone)

        # process variables initiation
        for objZone in objMarket.lsZone:
            createProcessVar(instance, objZone.lsProcess)

        # transmission initiation
        MarketTransmission_Init(objMarket, instance)

        if objMarket.sModel == "WM":
            # initiate generator agent 
            MarketAgent_Init(objMarket, instance)

    return



def createZoneVars(instance, objZone):
    ''' create zone variables '''

    objZone.fPowerOutput_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
    objZone.fPowerResDemand_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
    objZone.fHeatOutput_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
    objZone.fHeatResDemand_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
    
    objZone.fMarginalGenCost_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
    objZone.fNodalPrice_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )

    objZone.fASRqrRegulation_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
    objZone.fASRqr10MinReserve_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
    objZone.fASRqr30MinReserve_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
    objZone.fASDfcRegulation_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
    objZone.fASDfc10MinReserve_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
    objZone.fASDfc30MinReserve_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
        
    return


def createProcessVar(instance, lsProcess):
    ''' initiate process variables '''

    for objProcess in lsProcess:

        objProcess.fGenCostPerUnit_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )

        objProcess.fHourlyPowerOutput_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
        objProcess.fHourlyHeatOutput_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )

        objProcess.iOperatoinStatus_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )

        objProcess.fASRegulation_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
        objProcess.fAS10MinReserve_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
        objProcess.fAS30MinReserve_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )

        objProcess.fGenerationCost_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
        objProcess.fFuelConsumption_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
        objProcess.fCarbonCost_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
        objProcess.fGenerationCost_YS = np.zeros(len(instance.iAllYearSteps_YS))

        objProcess.fAnnualFixedCostPerMW = 0

        objProcess.fAnnualInvestment_YS = np.zeros(len(instance.iAllYearSteps_YS))

        objProcess.fDAMarketVolumn_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
        objProcess.fDAOfferPrice_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )

    return


def MarketTransmission_Init(objMarket, instance):
    ''' initialize transmission paratemer and variables initiation '''
    
    for objTrans in objMarket.lsTransmission:
        PlantLife = objTrans.LifeTime
        DiscountRate = objTrans.DiscountRate / 100
        fCapacity = objTrans.MaxFlow
        fCAPEX = objTrans.CAPEX     # USD/KW
        fOPEX = objTrans.OPEX       # USD/KW.year
        # capital recovery factor
        objTrans.fCRF = ( DiscountRate*pow((1+DiscountRate),PlantLife) ) / ( pow((1+DiscountRate),PlantLife) - 1)
        # year investment
        objTrans.fYearInvest = (fCAPEX * objTrans.fCRF + fOPEX) / 1000  # USD/kW * % / 1000 = M.USD/MW.year
        # capacity change
        objTrans.fTransNewBuild_YS = np.zeros(len(instance.iAllYearSteps_YS))
        objTrans.fTransAccCapacity_YS = np.empty(len(instance.iAllYearSteps_YS))
        objTrans.fTransAccCapacity_YS.fill(fCapacity)

    # initialize transmission
    for objTrans in objMarket.lsTransmission:
        objTrans.fTransLineInput_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
        objTrans.fTransLineOutput_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
        objTrans.iLineStatus_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )

    return



def MarketAgent_Init(objMarket, instance):
    ''' initialize GenCo agents '''
    
    for objGenerator in objMarket.lsGenerator:
        objGenerator.fAnnualProfit_YS = np.zeros(len(instance.iAllYearSteps_YS))
        objGenerator.fAssetsValue_YS = np.zeros(len(instance.iAllYearSteps_YS))
        objGenerator.fNewInvestment_YS = np.zeros(len(instance.iAllYearSteps_YS))

    return


# ----------------------------------------------------------------------------------------------------------------------
# model_iter_Init (only do once at the start of each whole foresight period iteration)
# ----------------------------------------------------------------------------------------------------------------------
    
def model_iter_Init(objMarket, instance):
    ''' market initiation for each new foresight iteration '''
    
    # calculate the required generation from power plants (include distribution loss and import/export)
    for objZone in objMarket.lsZone:
        ZoneDemand_iter_Init(instance, objZone)

    # move commit or decommit process
    ZoneProcess_Commit(instance, objMarket)
        
    # calculate derived cost, derated capacity
    for objZone in objMarket.lsZone:
        ZoneProcess_Init(objZone.lsProcess)
        
    # assign ancillary service in the market
    ZoneAncillaryServiceReq_Init(objMarket, instance, instance.iFSBaseYearIndex)
    
    return


def ZoneDemand_iter_Init(instance, objZone):
    ''' calculate the required generation from power plants (include distribution loss and import/export) '''

    # account for power distribution loss
    objZone.fPowerDemand_TS_YS[:,instance.iFSBaseYearIndex:] = \
    objZone.fPowerDemand_TS_YS[:,instance.iFSBaseYearIndex:] * (1 + objZone.fPowerDistLossRate_YS[instance.iFSBaseYearIndex:] / 100)

    # account for import/export 
    objZone.fPowerDemand_TS_YS[:,instance.iFSBaseYearIndex:] = \
    objZone.fPowerDemand_TS_YS[:,instance.iFSBaseYearIndex:] - objZone.fCrossMarketPowerImport_TS_YS[:,instance.iFSBaseYearIndex:]

    # account for heat distribution loss
    objZone.fHeatDemand_TS_YS[:,instance.iFSBaseYearIndex:] = \
    objZone.fHeatDemand_TS_YS[:,instance.iFSBaseYearIndex:] * (1 + objZone.fHeatDistLossRate_YS[instance.iFSBaseYearIndex:] / 100)

    # convert head demand unit GJ/h -> MW
    objZone.fHeatDemand_TS_YS[:,instance.iFSBaseYearIndex:] = objZone.fHeatDemand_TS_YS[:,instance.iFSBaseYearIndex:] * 0.27778

    return


def ZoneProcess_Commit(instance, objMarket):
    ''' move commit or decommit process (only do once at the start of each whole foresight period iteration) '''
    
    for objZone in objMarket.lsZone:
        # move decommited plant into decommitioned list 
        for objProcess in list(objZone.lsProcess):
            if objProcess.DeCommitTime <= instance.iForesightStartYear:
                objZone.lsProcessDecomm.append(copy.copy(objProcess))
                objZone.lsProcess.remove(objProcess)
    
        # move in new commisioned plants
        for objProcess in list(objZone.lsProcessPlanned):
            if objProcess.CommitTime <= instance.iForesightStartYear:
                objZone.lsProcess.append(copy.copy(objProcess))
                objZone.lsProcessPlanned.remove(objProcess)
           
        # existing process to be built in the near future still in the lsProcess
    
    return
    
    
def ZoneProcess_Init(lsProcess):
    ''' calculate derived cost, derated capacity '''
            
    # don't move plant decommited in the future into future list, if the data read from database, they should be planned for the near future

    # calculate derived parameters for existing plants 
    for objProcess in lsProcess:

        ### fixed cost
        fCapacity = objProcess.Capacity                                     # MW
        fCapitalCost = objProcess.CAPEX * objProcess.Capacity * 1000        # USD/KW * MW * 1000 = USD
        fYearOMCost = objProcess.OPEX * objProcess.Capacity * 1000          # USD/KW * MW * 1000 = USD
        fDiscountRate = objProcess.DiscountRate / 100
        iPlantLife = objProcess.TechnicalLife

        # fCapitalRecoveyFactor = (D*(1+D)^L) / ( ((1+D)^L)-1 )
        fCapitalRecoveyFactor =  ( fDiscountRate * ((1+fDiscountRate)**iPlantLife)) / ( ((1+fDiscountRate)**iPlantLife) - 1 )

        objProcess.fAnnualCapex = fCapitalCost * fCapitalRecoveyFactor / 1000000            # MillionUSD / year
        objProcess.fAnnualFixedCost = objProcess.fAnnualCapex + (fYearOMCost / 1000000)     # MillionUSD / year

        ### derated capacity
        fAvailability = objProcess.Availability
        fOwnUseRate = objProcess.OwnUseRate
        objProcess.fDeratedCapacity = fCapacity * (fAvailability / 100) * (1 - fOwnUseRate / 100)     # MW

    # calculate CHP power generation ratio
    for objProcess in lsProcess:
        if "CHP" in objProcess.sProcessName:
            # we assume all CHP process is back-pressure for now
            objProcess.fCHPPowerToHeatRate = objProcess.EffPowerBP / objProcess.EffHeatBP
                
    return



def ZoneAncillaryServiceReq_Init(objMarket, instance, indexYS):
    ''' assign ancillary service requirement in each zone of the market '''
    
    fMarketTotalDemand_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
    for objZone in objMarket.lsZone:
        fMarketTotalDemand_TS_YS = fMarketTotalDemand_TS_YS + objZone.fPowerDemand_TS_YS

    # ------------------------------------------------------
    # -------- regulatoin requirement ----------------------
    # assign the capacity based on peak demand in each zone
    for objZone in objMarket.lsZone:
    
        lsDayTimeSlice = list(instance.lsDayTimeSlice)
        for objDay in lsDayTimeSlice:
            
            # find the highest demand in the day
            fDailyHighestDemand = 0
            for objDayTS in objDay.lsDiurnalTS:
                fZoneDemand = objZone.fPowerDemand_TS_YS[objDayTS.iTimeSliceIndex, indexYS]
                if fZoneDemand > fDailyHighestDemand:
                    fDailyHighestDemand = fZoneDemand

            # calculate the required regulation in the day
            fRegulationRequire = 0  # MW
            if fDailyHighestDemand > 0:
                fRegulationRequire = fDailyHighestDemand * objMarket.fRegulationRequire_YS[indexYS] / 100
            
            for objDayTS in objDay.lsDiurnalTS:
                objZone.fASRqrRegulation_TS_YS[objDayTS.iTimeSliceIndex,indexYS] = fRegulationRequire
                    
    # --------------------------------------------------------    
    # -------- 10 and 30 Minutes Reserve requirement --------
    # assign the capacity based on the biggest plant peak in each zone in foresight base year

    f10mReserve_TS = np.zeros(len(instance.lsTimeSlice))
    f30mReserve_TS = np.zeros(len(instance.lsTimeSlice))
    
    # calculate daily required reserve capacity in the market
    lsDayTimeSlice = list(instance.lsDayTimeSlice)
    for objDay in lsDayTimeSlice:
        
        # find the highest demand in the day
        fDailyHighestDemand = 0
        for objDayTS in objDay.lsDiurnalTS:
            fMarketDemand = fMarketTotalDemand_TS_YS[objDayTS.iTimeSliceIndex, indexYS]
            if fMarketDemand > fDailyHighestDemand:
                fDailyHighestDemand = fMarketDemand 
                
        # calculate daily required reserve capacity in the market
        for objDayTS in objDay.lsDiurnalTS:
            f10mReserve_TS[objDayTS.iTimeSliceIndex] = fDailyHighestDemand * objMarket.f10mReserve_YS[indexYS] / 100
            f30mReserve_TS[objDayTS.iTimeSliceIndex] = fDailyHighestDemand * objMarket.f30mReserve_YS[indexYS] / 100

    # get the biggest operating unit capacity of the zones
    fBiggestUnitCapacity_ZN = np.zeros(len(objMarket.lsZone))
    for indexZone, objZone in enumerate(objMarket.lsZone):
        fBiggetUnitCapacity = -1    # negative number by default (if the zone has no plant or all renewables)
        for objProcess in objZone.lsProcess:
            if objProcess.sOperationMode == "Dispatch":
                fUnitCapacity = int(objProcess.Capacity / objProcess.NoUnit)
                if fUnitCapacity > fBiggetUnitCapacity:
                    fBiggetUnitCapacity = fUnitCapacity
        fBiggestUnitCapacity_ZN[indexZone] = fBiggetUnitCapacity

    lsDayTimeSlice = list(instance.lsDayTimeSlice)
    for objDay in lsDayTimeSlice:

        # get peak demand of the zone in the day
        fPeakDemand_ZN = np.zeros(len(objMarket.lsZone))
        for indexZone, objZone in enumerate(objMarket.lsZone):
            fPeakDemand = 0  # MW
            for objDayTS in objDay.lsDiurnalTS:
                if objZone.fPowerDemand_TS_YS[objDayTS.iTimeSliceIndex, indexYS] > fPeakDemand:
                    fPeakDemand = objZone.fPowerDemand_TS_YS[objDayTS.iTimeSliceIndex, indexYS]
            fPeakDemand_ZN[indexZone] = fPeakDemand
                    
        # ----------- assignment 10 minutes reserve capacity -----------
        fAssignedCapacity_ZN = np.zeros(len(objMarket.lsZone))
        fAssignedCapacity_ZN.fill(1)  # assign a non-zero value
        
        # minimal reserve requirement is half of the biggest unit in the zone
        for indexZone, objZone in enumerate(objMarket.lsZone):
            for objDayTS in objDay.lsDiurnalTS:
                fAssignedCapacity_ZN[indexZone] += fBiggestUnitCapacity_ZN[indexZone] / 2
                f10mReserve_TS[objDayTS.iTimeSliceIndex] -= fBiggestUnitCapacity_ZN[indexZone] / 2
                objZone.fASRqr10MinReserve_TS_YS[objDayTS.iTimeSliceIndex, indexYS] += fBiggestUnitCapacity_ZN[indexZone] / 2
                    
        # allocate the rest required reserve capacity
        bReserveAssignment = True
        while bReserveAssignment:
            if f10mReserve_TS[objDay.lsDiurnalTS[0].iTimeSliceIndex] > 0.001:
                # find the biggest reserve demand zone in terms of assigned capacity / peak demand
                indexLowestReserveZone = 0
                fLowestReserveRatio = 99999
                for indexZone, objZone in enumerate(objMarket.lsZone):
                    fZoneReserveRatio = fAssignedCapacity_ZN[indexZone] / fPeakDemand_ZN[indexZone]
                    if fZoneReserveRatio < fLowestReserveRatio and fBiggestUnitCapacity_ZN[indexZone] > 0:
                        fLowestReserveRatio = fZoneReserveRatio
                        indexLowestReserveZone = indexZone
                # assign reserve capacity to the region (half of the biggest capacity)
                fAssignedCapacity_ZN[indexLowestReserveZone] += fBiggestUnitCapacity_ZN[indexLowestReserveZone] / 2
                for objDayTS in objDay.lsDiurnalTS:
                    f10mReserve_TS[objDayTS.iTimeSliceIndex] -= fBiggestUnitCapacity_ZN[indexLowestReserveZone] / 2
                    objMarket.lsZone[indexLowestReserveZone].fASRqr10MinReserve_TS_YS[objDayTS.iTimeSliceIndex, indexYS] += \
                    fBiggestUnitCapacity_ZN[indexLowestReserveZone] / 2
            else:
                bReserveAssignment = False
                # reserve capacity assignment is done
          
        # ----------- assignment 30 minutes reserve capacity -----------
        fAssignedCapacity_ZN.fill(1)  # reset and assign a non-zero value
        
        # minimal reserve requirement is the biggest unit in the zone
        for indexZone, objZone in enumerate(objMarket.lsZone):
            for objDayTS in objDay.lsDiurnalTS:
                fAssignedCapacity_ZN[indexZone] += fBiggestUnitCapacity_ZN[indexZone]
                f30mReserve_TS[objDayTS.iTimeSliceIndex] -= fBiggestUnitCapacity_ZN[indexZone]
                objZone.fASRqr30MinReserve_TS_YS[objDayTS.iTimeSliceIndex, indexYS] += fBiggestUnitCapacity_ZN[indexZone]
                
        # allocate the rest required reserve capacity
        bReserveAssignment = True
        while bReserveAssignment:
            if f30mReserve_TS[objDay.lsDiurnalTS[0].iTimeSliceIndex] > 0.001:
                # find the biggest reserve demand zone in terms of assigned capacity / peak demand
                indexLowestReserveZone = 0
                fLowestReserveRatio = 99999
                for indexZone, objZone in enumerate(objMarket.lsZone):
                    fZoneReserveRatio = fAssignedCapacity_ZN[indexZone] / fPeakDemand_ZN[indexZone]
                    if fZoneReserveRatio < fLowestReserveRatio and fBiggestUnitCapacity_ZN[indexZone] > 0.001:
                        fLowestReserveRatio = fZoneReserveRatio
                        indexLowestReserveZone = indexZone
                # assign reserve capacity to the region (half of the biggest capacity)
                fAssignedCapacity_ZN[indexLowestReserveZone] += fBiggestUnitCapacity_ZN[indexLowestReserveZone] / 2
                for objDayTS in objDay.lsDiurnalTS:
                    f30mReserve_TS[objDayTS.iTimeSliceIndex] -= fBiggestUnitCapacity_ZN[indexLowestReserveZone] / 2
                    objMarket.lsZone[indexLowestReserveZone].fASRqr30MinReserve_TS_YS[objDayTS.iTimeSliceIndex, indexYS] += \
                    fBiggestUnitCapacity_ZN[indexLowestReserveZone] / 2
            else:
                bReserveAssignment = False
                # reserve capacity assignment is done
                
    return


# ----------------------------------------------------------------------------------------------------------------------
# process init
# ----------------------------------------------------------------------------------------------------------------------


def processVarCost_Init_model(objMarket, instance):
    ''' commit and decommit process, and calculate derived variables '''
                    
    # calculate variable generation cost
    for objZone in objMarket.lsZone:
        processVarCost_Init(instance, objMarket, objZone, objZone.lsProcess)
        
    return


def processVarCost_Init(instance, objMarket, objZone, lsProcess):
    ''' commit and decommit process, and calculate derived variables '''
                    
    # calculate variable generation cost

    objCountry = instance.lsRegion[objZone.iRegionIndex].lsCountry[objZone.iCountryIndex]
    
    for objProcess in list(lsProcess):
        
        # process efficiency
        if "CHP" in objProcess.sProcessName:
            fProcessEff = max(objProcess.EffPowerCM, objProcess.EffPowerBP + objProcess.EffHeatBP)
        else:
            fProcessEff = objProcess.EffPowerCM
                
        
        # -------- running cost ------------
        fRunningCost_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
        fRunningCost_TS_YS.fill(objProcess.RunningCost)

        # sum up generation cost
        objProcess.fVariableGenCost_TS_YS = fRunningCost_TS_YS

        # dispatchable plant (thermal generation, including CHP)
        if objProcess.sOperationMode == "Dispatch":

            # get the carrier object
            for objCommodity in objCountry.lsCommodity:
                if objCommodity.sCommodityName == objProcess.sFuel:
                    objFuel = objCommodity
                    break

            # ----------- fuel cost --------------
            # get fuel price (USD/LOE)
            fFuelPrice_TS_YS = objFuel.fFuelPrice_TS_YS

            # conver fuel cost from (USD/LOE) to (USD/kWh)  
            # fFuelPrice = fFuelPrice / 10.46  USD/LOE -> USD/kWh
            # fFuelPrice = fFuelPrice / 277.8  MUSD/PJ -> MUSD/GWh = USD/kWh
            fFuelPrice_TS_YS = fFuelPrice_TS_YS / 10.46

            # get plant tech conversion efficiency (USD/kWh)
            fFuelCost_TS_YS = fFuelPrice_TS_YS / (fProcessEff / 100)


            # ----------- emission cost ---------------
            # emission factor (kg/MJ = MTon/PJ)
            fEmissionFactor = objFuel.fEmissionFactor_CO2
            # fuel consumption per kWh
            fFuelConsumption = 1 / (fProcessEff / 100)    # kWh
            fFuelConsumption = fFuelConsumption * 3.6    # kWh -> MJ (per kWh)
            # capture rate
            fCCSCaptureRate = objProcess.CCSCaptureRate / 100
            # carbon cost (USD/Tonne -> USD/kg)
            fCarbonCost_YS = objCountry.fCarbonCost_YS / 1000

            # emission cost  (kg/MJ) * (MJ/kWh) * (USD/kg) = USD/kWh
            fEmissionCost_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
            fEmissionCost_TS_YS[:,:] = fEmissionFactor * fFuelConsumption * (1-fCCSCaptureRate) * fCarbonCost_YS
            if objFuel.sCategory == "biofuel":
                fEmissionCost_TS_YS += fEmissionFactor * fFuelConsumption * fCCSCaptureRate * fCarbonCost_YS * -1

            # sum up generation cost
            objProcess.fVariableGenCost_TS_YS += fFuelCost_TS_YS + fEmissionCost_TS_YS
            objProcess.fVariableGenCost_TS_YS = np.around(objProcess.fVariableGenCost_TS_YS, 4)
            
    return


# ----------------------------------------------------------------------------------------------------------------------
# update demand
# ----------------------------------------------------------------------------------------------------------------------

def updatePowerResidualDemand_Yearly(instance, objZone, indexYS):
    ''' update power residual demand '''

    objZone.fPowerResDemand_TS_YS[:,indexYS] = objZone.fPowerDemand_TS_YS[:,indexYS] - objZone.fPowerOutput_TS_YS[:,indexYS]
    objZone.fPowerResDemand_TS_YS[ objZone.fPowerResDemand_TS_YS[:,indexYS] < 0 ,indexYS] = 0
    # power import/export from other market already account in ZoneDemand_iter_Init
    return


def updatePowerResDemandWithTrans(objMarket, objZone, indexTS, indexYS):
    ''' calculate residual demand considering cross-zone import/export '''
    
    # all connection import
    fConnImport = 0
    for index, objConnLine in enumerate(objMarket.lsTransmission): 
        if objConnLine.To == objZone.sZone:
            fConnImport += objConnLine.fTransLineOutput_TS_YS[indexTS, indexYS]

    # all connection export
    fConnExport = 0
    for index, objConnLine in enumerate(objMarket.lsTransmission): 
        if objConnLine.From == objZone.sZone:
            fConnExport += objConnLine.fTransLineInput_TS_YS[indexTS, indexYS]

    fResidualDemand = objZone.fPowerDemand_TS_YS[indexTS, indexYS] - objZone.fPowerOutput_TS_YS[indexTS, indexYS] - fConnImport + fConnExport

    if fResidualDemand > 0.01:
        objZone.fPowerResDemand_TS_YS[indexTS, indexYS] = fResidualDemand
    else :
        objZone.fPowerResDemand_TS_YS[indexTS, indexYS] = 0

    return


def updateHeatResidualDemand_Yearly(instance, objZone, indexYS):
    ''' update heat residual demand '''

    objZone.fHeatResDemand_TS_YS[:,indexYS] = objZone.fHeatDemand_TS_YS[:,indexYS] - objZone.fHeatOutput_TS_YS[:,indexYS]
    objZone.fHeatResDemand_TS_YS[ objZone.fHeatResDemand_TS_YS[:,indexYS] < 0 ,indexYS] = 0

    return



# ----------------------------------------------------------------------------------------------------------------------
# node price
# ----------------------------------------------------------------------------------------------------------------------

def nodeprice_Init(instance, objMarket, indexYS, sMode):

    for objZone in objMarket.lsZone:
        
        if sMode == "ExecMode":
            lsProcess = objZone.lsProcess
        elif sMode == "PlanMode":
            lsProcess = objZone.lsProcessOperTemp
        
        aMGC = np.zeros(len(instance.lsTimeSlice))

        for indexTS, objTimeSlice in enumerate(instance.lsTimeSlice):
            for indexP, objProcess in enumerate(lsProcess):
                
                if objProcess.fHourlyPowerOutput_TS_YS[indexTS, indexYS] > 1:
                    if objProcess.sOperationMode == "Dispatch":
                        
                        # must-run block doesn't count
                        fMustRunOutput = objProcess.fDeratedCapacity * (objProcess.MinLoadRate / 100)
                        if objProcess.fHourlyPowerOutput_TS_YS[indexTS, indexYS] > (fMustRunOutput + 1) and objProcess.fVariableGenCost_TS_YS[indexTS, indexYS] > aMGC[indexTS]:
                            aMGC[indexTS] = objProcess.fVariableGenCost_TS_YS[indexTS, indexYS]
                    else:
                        if objProcess.fVariableGenCost_TS_YS[indexTS, indexYS] > aMGC[indexTS]:
                            aMGC[indexTS] = objProcess.fVariableGenCost_TS_YS[indexTS, indexYS]
                            
        objZone.fMarginalGenCost_TS_YS[:,indexYS] = aMGC
        objZone.fNodalPrice_TS_YS[:,indexYS] = copy.deepcopy(objZone.fMarginalGenCost_TS_YS[:,indexYS])

    return


def calNodalPrice(instance, objMarket, indexYS):
    ''' calculate nodal price fNodalPrice_TS_YS '''
    
    for indexTS, objTimeSlice in enumerate(instance.lsTimeSlice):
        
        # create a dictionary to sort the nodal price
        lsVariableGenCost_ZN = []
        for indexZone, objZone in enumerate(objMarket.lsZone):
            lsVariableGenCost_ZN.append([indexZone, objZone.fNodalPrice_TS_YS[indexTS,indexYS]])
        lsVariableGenCost_ZN = sorted(lsVariableGenCost_ZN, key=lambda lsVariableGenCost_ZN: lsVariableGenCost_ZN[1], reverse=True)

        # algorighm starts from high nodal price
        for indexZone in lsVariableGenCost_ZN:
            objZone = objMarket.lsZone[indexZone[0]]

            for iLine, objLine in enumerate(objMarket.lsTransmission): 
                if objLine.From == objZone.sZone:
                    
                    # get direct connected subregion
                    objConnectZone = None
                    for objDesZone in objMarket.lsZone:
                        if objLine.To == objDesZone.sZone:
                            objConnectZone = objDesZone
                            break
    
                    if objLine.fTransLineInput_TS_YS[indexTS,indexYS] > 0.01:
                        # nodal price of destination
                        fCurrentNodalPrice = objZone.fNodalPrice_TS_YS[indexTS,indexYS]
                        fDesNodalPrice = objConnectZone.fNodalPrice_TS_YS[indexTS,indexYS]
                        if (fCurrentNodalPrice / (1 - objLine.FlowLossRate/100)) > fDesNodalPrice:
                            objConnectZone.fNodalPrice_TS_YS[indexTS,indexYS] = fCurrentNodalPrice / (1 - objLine.FlowLossRate/100)

    return


# ----------------------------------------------------------------------------------------------------------------------
# capacity planning
# ----------------------------------------------------------------------------------------------------------------------

def getNewProcessCandidate(instance, objZone, indexYS):
    ''' return a list of plant with each technology in a region '''
    
    listNewPlantCandidate = list()
    for objProcessAssump in objZone.lsProcessAssump:
        
        objNewProcessAssump = copy.deepcopy(objProcessAssump)

        # basic parameters
        sPlantID = objNewProcessAssump.sProcessName + "_" + str(instance.iAllYearSteps_YS[indexYS])
        sProcessName = objNewProcessAssump.sProcessName
        dicParameters = {}
        sCompanyName = objZone.sZone    # need to assign the company name
        objNewProcess = cls_misc.ZoneProcess(sCompanyName , sProcessName, sPlantID, dicParameters)
        # set parameters
        objNewProcess.bCCS = objNewProcessAssump.bCCS
        objNewProcess.sProcessFullName = objNewProcessAssump.sProcessFullName
        objNewProcess.sFuel = objNewProcessAssump.sFuel
        objNewProcess.sOperationMode = objNewProcessAssump.sOperationMode
        # set technical parameters (inherit from region assumption)
        # default capacity to boot running speed
        if objNewProcessAssump.StdUnitCapacity > np.average(objZone.fPowerDemand_TS_YS[:,indexYS]) / 30:
            objNewProcess.Capacity = objNewProcessAssump.StdUnitCapacity
        else:
            # take the round up unit numbers
            objNewProcess.NoUnit = math.ceil((np.average(objZone.fPowerDemand_TS_YS[:,indexYS])/30)/objNewProcessAssump.StdUnitCapacity)
            objNewProcess.Capacity = int(objNewProcessAssump.StdUnitCapacity * objNewProcess.NoUnit)
        objNewProcess.TechnicalLife = objNewProcessAssump.TechnicalLife
        objNewProcess.NoUnit = int(objNewProcess.Capacity // objNewProcessAssump.StdUnitCapacity) + 1
        objNewProcess.CommitTime = instance.iAllYearSteps_YS[indexYS]
        objNewProcess.DeCommitTime = instance.iAllYearSteps_YS[indexYS] + objNewProcessAssump.TechnicalLife
        objNewProcess.Company = sCompanyName
        objNewProcess.OwnUseRate = objNewProcessAssump.OwnUseRate
        objNewProcess.Availability = objNewProcessAssump.Availability
        objNewProcess.MinLoadRate = objNewProcessAssump.MinLoadRate
        objNewProcess.RampRatePerM = objNewProcessAssump.RampRatePerM
        objNewProcess.CCSCaptureRate = objNewProcessAssump.CCSCaptureRate
        objNewProcess.DayStorageOutput = objNewProcessAssump.DayStorageOutput
        objNewProcess.EffPowerCM = objNewProcessAssump.fEffPowerCM_YS[indexYS]
        objNewProcess.EffPowerBP = objNewProcessAssump.fEffPowerBP_YS[indexYS]
        objNewProcess.EffHeatBP = objNewProcessAssump.fEffHeatBP_YS[indexYS]
        # set cost assumptions (inherit from region assumption)
        objNewProcess.CAPEX = objNewProcessAssump.fCAPEX_YS[indexYS]
        objNewProcess.OPEX = objNewProcessAssump.fOPEX_YS[indexYS]
        objNewProcess.RunningCost = objNewProcessAssump.fRunningCost_YS[indexYS]
        objNewProcess.DiscountRate = objNewProcessAssump.fDiscountRate_YS[indexYS]

        listNewPlantCandidate.append(objNewProcess)

    return listNewPlantCandidate


def getNewBuildCapacityLimit(instance, objZone, lsProcess, lsProcessPlanned, lsProcessCandidate, indexYS):
    ''' total allowed new build capacity according to capacity constraints '''
    
    iYearStep = instance.iAllYearSteps_YS[indexYS]
    lsOperationalPlants = getOperationalProcessList_DeepCopy(lsProcess, lsProcessPlanned, iYearStep)

    for indexTC, objProcess in enumerate(lsProcessCandidate):
        sProcessName = objProcess.sProcessName

        fMaxYearCapacity, fMaxNewInstallCapacity = getCapacityConstraints(instance, objZone, sProcessName, indexYS)

        # check maximum capacity constraints
        fTotalExitCapacity = 0
        for indexP, objOprProcess in enumerate(lsOperationalPlants):
            if objOprProcess.sProcessName == sProcessName:
                if objOprProcess.DeCommitTime > iYearStep and objOprProcess.CommitTime < iYearStep:
                    fTotalExitCapacity += objOprProcess.Capacity

        if fMaxNewInstallCapacity > (fMaxYearCapacity-fTotalExitCapacity):
            objProcess.fMaxAllowedNewBuildCapacity = fMaxYearCapacity-fTotalExitCapacity
        else:
            objProcess.fMaxAllowedNewBuildCapacity = fMaxNewInstallCapacity

    return


def getOperationalProcessList_DeepCopy(lsProcess, lsProcessPlanned, iYearStep):
    ''' return a combined process list which are in operation in the given year step '''
    
    listOperationalPlants = list()

    for indexP, objPlant in enumerate(lsProcess):
        if objPlant.DeCommitTime > iYearStep and objPlant.CommitTime <= iYearStep:
            listOperationalPlants.append(copy.deepcopy(objPlant))

    for indexP, objPlant in enumerate(lsProcessPlanned):
        if objPlant.DeCommitTime > iYearStep and objPlant.CommitTime <= iYearStep:
            listOperationalPlants.append(copy.deepcopy(objPlant))

    return listOperationalPlants


def getOperationalProcessList_ShallowCopy(lsProcess, lsProcessPlanned, iYearStep):
    ''' return a combined process list which are in operation in the given year step '''
    # do not change anything on the original objZone.lsProcess
    
    listOperationalPlants = list()

    for indexP, objPlant in enumerate(lsProcess):
        if objPlant.DeCommitTime > iYearStep and objPlant.CommitTime <= iYearStep:
            listOperationalPlants.append(copy.copy(objPlant))

    for indexP, objPlant in enumerate(lsProcessPlanned):
        if objPlant.DeCommitTime > iYearStep and objPlant.CommitTime <= iYearStep:
            listOperationalPlants.append(copy.copy(objPlant))

    return listOperationalPlants



def getCapacityConstraints(instance, objZone, sProcessName, indexYS):
    ''' get capacity constraints '''
    
    fMaxYearCapacity = 0
    fMaxNewInstallCapacity = 0

    iYearPeriod = instance.iAllYearSteps_YS[indexYS] - instance.iAllYearSteps_YS[indexYS-1]

    for objProcessAssump in objZone.lsProcessAssump:
        if objProcessAssump.sProcessName == sProcessName:
            fMaxYearCapacity = objProcessAssump.fMaxCapacity_YS[indexYS]
            fMaxNewInstallCapacity = objProcessAssump.fMaxBuildRate_YS[indexYS] * iYearPeriod  # takes into account the interval
            break

    return fMaxYearCapacity, fMaxNewInstallCapacity


def getNewStorageCandidate(lsProcessCandidate):
    ''' return a list of new storage process candidate '''
    
    lsNewStorageCandidate = list()

    for objProcess in list(lsProcessCandidate):
        if objProcess.sOperationMode == "Storage":
            lsNewStorageCandidate.append(copy.copy(objProcess))
            lsProcessCandidate.remove(objProcess)

    return lsNewStorageCandidate


def getNewCHPCandidate(lsProcessCandidate):
    ''' return a list of new storage process candidate '''
    
    lsNewCHPCandidate = list()

    for objProcess in list(lsProcessCandidate):
        if "CHP" in objProcess.sProcessName:
            lsNewCHPCandidate.append(copy.copy(objProcess))
            lsProcessCandidate.remove(objProcess)

    return lsNewCHPCandidate


def getOperationalPlantList(lsProcess, lsProcessPlanned, iYearStep):
    ''' return a combined plant list which are in operation in the given time period '''
    
    lsProcessOperTemp = list()

    for indexP, objProcess in enumerate(lsProcess):
        if objProcess.DeCommitTime > iYearStep and objProcess.CommitTime <= iYearStep:
            lsProcessOperTemp.append(copy.copy(objProcess))

    for indexP, objProcess in enumerate(lsProcessPlanned):
        if objProcess.DeCommitTime > iYearStep and objProcess.CommitTime <= iYearStep:
            lsProcessOperTemp.append(copy.copy(objProcess))

    return lsProcessOperTemp








