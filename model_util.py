# -*- coding: utf-8 -*-

import copy
import numpy as np

def model_Init(objMarket, instance):
    ''' market initiation '''
    
    # first time to run of the model (base year, and no output)
    if instance.iForesightStartYear == instance.iBaseYear and objMarket.MarketOutput.dicGenCapacity_YR_TC == {} :

        # calculate the required generation from power plants (include distribution loss and import/export)
        ZoneDemand_Init(objMarket, instance)

        # move commit or decommit process, calculate derived cost, derated capacity
        ZoneExistProcess_Init(objMarket, instance)
        
        # process variables initiation
        ZoneProcess_Init(objMarket, instance)

        # transmission cost initiation
        MarketTransCost_Init(objMarket, instance)

        if objMarket.sModel == "WM":
            # initiate generator agent 
            MarketAgent_Init(objMarket, instance)

        print("")

    return



def ZoneDemand_Init(objMarket, instance):
    ''' calculate the required generation from power plants (include distribution loss and import/export) '''
        
    for objZone in objMarket.lsZone:
        
        # account for power distribution loss
        objZone.fPowerDemand_TS_YS[instance.iFSBaseYearIndex:,:] = \
        objZone.fPowerDemand_TS_YS[instance.iFSBaseYearIndex:,:] * (1 + objZone.fPowerLossRatio_YS[instance.iFSBaseYearIndex:] / 100)
    
        # account for import/export 
        objZone.fPowerDemand_TS_YS[instance.iFSBaseYearIndex:,:] = \
        objZone.fPowerDemand_TS_YS[instance.iFSBaseYearIndex:,:] - objZone.fPowerImport_TS_YS[instance.iFSBaseYearIndex:,:]

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

    return



def ZoneProcess_Init(objMarket, instance):
    ''' initiate process variables '''
        
    for objZone in objMarket.lsZone:
        for objProcess in objZone.lsProcess:

            objProcess.fGenCostPerUnit_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )

            objProcess.fHourNetGeneration_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
    
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



def MarketTransCost_Init(objMarket, instance):
    ''' initialize transmission cost paratemer '''
    
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

    return



def MarketAgent_Init(objMarket, instance):
    ''' initialize GenCo agents '''
    
    for objGenerator in objMarket.lsGenerator:
        objGenerator.fAnnualProfit_YR = np.zeros(len(instance.iAllYearSteps_YS))
        objGenerator.fAssetsValue_YR = np.zeros(len(instance.iAllYearSteps_YS))
        objGenerator.fNewInvestment_YR = np.zeros(len(instance.iAllYearSteps_YS))

    return




