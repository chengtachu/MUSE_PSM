# -*- coding: utf-8 -*-

import copy
import numpy as np


# ----------------------------------------------------------------------------------------------------------------------
# model_fisrt_Init
# ----------------------------------------------------------------------------------------------------------------------

def model_fisrt_Init(objMarket, instance):
    ''' market initiation in first iteration '''
    
    # first time to run of the model (base year, and no output)
    if instance.iForesightStartYear == instance.iBaseYear and objMarket.MarketOutput.dicGenCapacity_YR_TC == {} :

        # create zone variables
        ZoneDemand_first_Init(objMarket, instance)

        # process variables initiation
        ZoneProcessVar_Init(objMarket, instance)

        # transmission initiation
        MarketTransmission_Init(objMarket, instance)

        if objMarket.sModel == "WM":
            # initiate generator agent 
            MarketAgent_Init(objMarket, instance)

    return



def ZoneDemand_first_Init(objMarket, instance):
    ''' create zone variables '''
        
    for objZone in objMarket.lsZone:
        
        # variable initiation
        objZone.fPowerOutput_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
        objZone.fPowerResDemand_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
        objZone.fHeatOutput_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
        objZone.fHeatResDemand_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
        
    return



def ZoneProcessVar_Init(objMarket, instance):
    ''' initiate process variables '''
        
    for objZone in objMarket.lsZone:
        for objProcess in objZone.lsProcess:

            objProcess.fGenCostPerUnit_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )

            objProcess.fHourlyPowerOutput_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
            objProcess.fHourlyHeatOutput_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
    
            objProcess.fGenerationCost_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
            objProcess.fFuelConsumption_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
            objProcess.fCarbonCost_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
            objProcess.fGenerationCost_YS = np.zeros(len(instance.iAllYearSteps_YS))
    
            objProcess.fAnnualFixedCostPerMW = 0
            objProcess.fPriceMarkUp = 0
    
            objProcess.fAnnualInvestment_YR = np.zeros(len(instance.iAllYearSteps_YS))
    
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
        objGenerator.fAnnualProfit_YR = np.zeros(len(instance.iAllYearSteps_YS))
        objGenerator.fAssetsValue_YR = np.zeros(len(instance.iAllYearSteps_YS))
        objGenerator.fNewInvestment_YR = np.zeros(len(instance.iAllYearSteps_YS))

    return


# ----------------------------------------------------------------------------------------------------------------------
# model_iter_Init
# ----------------------------------------------------------------------------------------------------------------------
    
def model_iter_Init(objMarket, instance):
    ''' market initiation for each new foresight iteration '''
    
    # calculate the required generation from power plants (include distribution loss and import/export)
    ZoneDemand_iter_Init(objMarket, instance)

    # move commit or decommit process, calculate derived cost, derated capacity
    ZoneExistProcess_Init(objMarket, instance)
        
    return


def ZoneDemand_iter_Init(objMarket, instance):
    ''' calculate the required generation from power plants (include distribution loss and import/export) '''
        
    for objZone in objMarket.lsZone:
        
        # account for power distribution loss
        objZone.fPowerDemand_TS_YS[:,instance.iFSBaseYearIndex:] = \
        objZone.fPowerDemand_TS_YS[:,instance.iFSBaseYearIndex:] * (1 + objZone.fPowerDistLossRate_YS[instance.iFSBaseYearIndex:] / 100)
    
        # account for import/export 
        objZone.fPowerDemand_TS_YS[:,instance.iFSBaseYearIndex:] = \
        objZone.fPowerDemand_TS_YS[:,instance.iFSBaseYearIndex:] - objZone.fPowerImport_TS_YS[:,instance.iFSBaseYearIndex:]

        # account for heat distribution loss
        objZone.fHeatDemand_TS_YS[:,instance.iFSBaseYearIndex:] = \
        objZone.fHeatDemand_TS_YS[:,instance.iFSBaseYearIndex:] * (1 + objZone.fHeatDistLossRate_YS[instance.iFSBaseYearIndex:] / 100)

        # convert head demand unit GJ/h -> MW
        objZone.fHeatDemand_TS_YS[:,instance.iFSBaseYearIndex:] = objZone.fHeatDemand_TS_YS[:,instance.iFSBaseYearIndex:] * 0.27778

    return


def ZoneExistProcess_Init(objMarket, instance):
    ''' move commit or decommit process, calculate derived cost, derated capacity '''
            
    # move decommited plant into decommitioned list
    for objZone in objMarket.lsZone:
        for objProcess in list(objZone.lsProcess):
            
            if objProcess.DeCommitTime <= instance.iForesightStartYear:
                objZone.lsProcessDecomm.append(copy.copy(objProcess))
                objZone.lsProcess.remove(objProcess)

        # don't move plant decommited in the future into future list, if the data read from database, they should be planned for the near future


    # calculate derived parameters for existing plants 
    for objZone in objMarket.lsZone:
        for objProcess in objZone.lsProcess:

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
    for objZone in objMarket.lsZone:
        for objProcess in objZone.lsProcess:
            if "CHP" in objProcess.sProcessName:
                # we assume all CHP process is back-pressure for now
                objProcess.fCHPPowerRatio = objProcess.EffPowerBP / (objProcess.EffPowerBP + objProcess.EffHeatBP)
                
    return



# ----------------------------------------------------------------------------------------------------------------------
# process init
# ----------------------------------------------------------------------------------------------------------------------

def process_Init(objMarket, instance):
    ''' commit and decommit process, and calculate derived variables '''
        
    # move processes in lsProcess, lsProcessDecomm and lsProcessFuture
    for objZone in objMarket.lsZone:

        # move decommited plant into decommitioned list 
        for objProcess in list(objZone.lsProcess):
            if objProcess.DeCommitTime <= instance.iForesightStartYear:
                objZone.lsProcessDecomm.append(copy.copy(objProcess))
                objZone.lsProcess.remove(objProcess)
    
        # move in new commisioned plants
        for objProcess in list(objZone.lsProcessFuture):
            if objProcess.CommitTime <= instance.iForesightStartYear:
                objZone.lsProcess.append(copy.copy(objProcess))
                objZone.lsProcessFuture.remove(objProcess)
           
            
    # calculate variable generation cost
    for objZone in objMarket.lsZone:
        
        objCountry = instance.lsRegion[objZone.iRegionIndex].lsCountry[objZone.iCountryIndex]
        
        for objProcess in list(objZone.lsProcess):
            
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
    
            # dispatchable plant (thermal generation, except some large hyro)
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




