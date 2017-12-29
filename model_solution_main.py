# -*- coding: utf-8 -*-

import copy

import numpy as np

import model_solution_process

def updateZoneSolution(instance, objMarket):

    for objZone in objMarket.lsZone:

        objCountry = instance.lsRegion[objZone.iRegionIndex].lsCountry[objZone.iCountryIndex]
        
        lsAllProcess = list(copy.copy(objZone.lsProcess))
        lsAllProcess.extend(copy.copy(objZone.lsProcessPlanned))

        ZoneProcessSet = [ objProcessAssump.sProcessName for objProcessAssump in objZone.lsProcessAssump ]
        ZoneProcessStrgSet = [ objProcessAssump.sProcessName for objProcessAssump in objZone.lsProcessAssump if objProcessAssump.sOperationMode == "Storage" ]
        setFSYearSteps = [ iFSYearSteps for iFSYearSteps in instance.iFSYearSteps_YS ]
        setTimeSliceSN = [ objTimeSlice.iTSIndex for objTimeSlice in instance.lsTimeSlice ]
        setCommodity = [ objCommodity.sCommodityName for objCommodity in objCountry.lsCommodity ]

        ##### power generation and balance
        # total generation capacity and new capacity  objZone.listGenPlant
        vGenCapacity_YS_PR, vNewBuild_YS_PR = model_solution_process.getTotalAndNewCapacity(instance, objZone, lsAllProcess)

        if instance.iForesightStartYear == instance.iBaseYear:
            saveSolution_YS_PR(vGenCapacity_YS_PR, objZone.ZoneOutput.dicGenCapacity_YS_PR, setFSYearSteps, ZoneProcessSet)
            saveSolution_YS_PR(vNewBuild_YS_PR, objZone.ZoneOutput.dicGenNewCapacity_YS_PR, setFSYearSteps, ZoneProcessSet)  
        else:
            # do not overwrite the foresight start year data
            saveSolution_YS_PR_ExcCurrentYear(vGenCapacity_YS_PR, objZone.ZoneOutput.dicGenCapacity_YS_PR, setFSYearSteps, ZoneProcessSet) 
            saveSolution_YS_PR_ExcCurrentYear(vNewBuild_YS_PR, objZone.ZoneOutput.dicGenNewCapacity_YS_PR, setFSYearSteps, ZoneProcessSet) 

        # power/heat output and generation
        vPowerOutput_YS_TS_PR, vPowerGen_YS_TS_PR, endPowerGen_YS_TS, vHeatOutput_YS_TS_PR, vHeatGen_YS_TS_PR, endHeatGen_YS_TS = \
            model_solution_process.getPowerOutputAndGeneration(instance, objZone, lsAllProcess)

        saveSolution_YS_TS_PR(vPowerOutput_YS_TS_PR, objZone.ZoneOutput.dicPowerOutput_YS_TS_PR, setFSYearSteps, setTimeSliceSN, ZoneProcessSet)
        saveSolution_YS_TS_PR(vPowerGen_YS_TS_PR, objZone.ZoneOutput.dicPowerGen_YS_TS_PR, setFSYearSteps, setTimeSliceSN, ZoneProcessSet)
        saveSolution_YS_TS(endPowerGen_YS_TS, objZone.ZoneOutput.dicZonePowerGen_YS_TS, setFSYearSteps, setTimeSliceSN)
        saveSolution_YS_TS_PR(vHeatOutput_YS_TS_PR, objZone.ZoneOutput.dicHeatOutput_YS_TS_PR, setFSYearSteps, setTimeSliceSN, ZoneProcessSet)
        saveSolution_YS_TS_PR(vHeatGen_YS_TS_PR, objZone.ZoneOutput.dicHeatGen_YS_TS_PR, setFSYearSteps, setTimeSliceSN, ZoneProcessSet) 
        saveSolution_YS_TS(endHeatGen_YS_TS, objZone.ZoneOutput.dicZoneHeatGen_YS_TS, setFSYearSteps, setTimeSliceSN)
        
        ##### storage
        vStrgInput_YS_TS_ST, vStrgOuput_YS_TS_ST = model_solution_process.getStoragePowerOperation(instance, objZone, lsAllProcess, ZoneProcessStrgSet)

        saveSolution_YS_TS_PR(vStrgInput_YS_TS_ST, objZone.ZoneOutput.dicStrgInput_YS_TS_ST, setFSYearSteps, setTimeSliceSN, ZoneProcessStrgSet) 
        saveSolution_YS_TS_PR(vStrgOuput_YS_TS_ST, objZone.ZoneOutput.dicStrgOutput_YS_TS_ST, setFSYearSteps, setTimeSliceSN, ZoneProcessStrgSet)

        ##### cost, fuel consumption, total emission
        vGenCAPEX_YS_PR, vGenOPEX_YS_PR, \
        vFuelCost_YS_PR, vEmissionCost_YS_PR, vRunningCost_YS_PR, vYearInvest_YS_PR, \
        vFuelConsum_YS_TS_PR, endFuelConsumption_YS_TS_CM, \
        endCO2Emission_YS, endCO2Emission_YS_TS, endEmissionCaptured_YS_TS \
            = model_solution_process.getProcessMainResult(instance, objZone, lsAllProcess)

        saveSolution_YS_PR(vGenCAPEX_YS_PR, objZone.ZoneOutput.dicGenCAPEX_YS_PR, setFSYearSteps, ZoneProcessSet) 
        saveSolution_YS_PR(vGenOPEX_YS_PR, objZone.ZoneOutput.dicGenOPEX_YS_PR, setFSYearSteps, ZoneProcessSet) 

        saveSolution_YS_PR(vRunningCost_YS_PR, objZone.ZoneOutput.dicRunningCost_YS_PR, setFSYearSteps, ZoneProcessSet) 
        saveSolution_YS_PR(vFuelCost_YS_PR, objZone.ZoneOutput.dicFuelCost_YS_PR, setFSYearSteps, ZoneProcessSet) 
        saveSolution_YS_PR(vEmissionCost_YS_PR, objZone.ZoneOutput.dicEmissionCost_YS_PR, setFSYearSteps, ZoneProcessSet) 
        saveSolution_YS_PR(vYearInvest_YS_PR, objZone.ZoneOutput.dicYearInvest_YS_PR, setFSYearSteps, ZoneProcessSet) 

        saveSolution_YS_TS_PR(vFuelConsum_YS_TS_PR, objZone.ZoneOutput.dicFuelConsum_YS_TS_PR, setFSYearSteps, setTimeSliceSN, ZoneProcessSet)
        saveSolution_YS_TS_PR(endFuelConsumption_YS_TS_CM, objZone.ZoneOutput.dicFuelConsum_YS_TS_CM, setFSYearSteps, setTimeSliceSN, setCommodity) 
        saveSolution_YS(endCO2Emission_YS, objZone.ZoneOutput.dicCO2Emission_YS, setFSYearSteps)  
        saveSolution_YS_TS(endCO2Emission_YS_TS, objZone.ZoneOutput.dicCO2Emission_YS_TS, setFSYearSteps, setTimeSliceSN)
        saveSolution_YS_TS(endEmissionCaptured_YS_TS, objZone.ZoneOutput.dicEmissionCaptured_YS_TS, setFSYearSteps, setTimeSliceSN)
        
        #### ancillary service
        vAncSerRegulation_YS_TS, vAncSer10MinReserve_YS_TS, vAncSer30MinReserve_YS_TS \
            = model_solution_process.getAncSerResult(instance, objZone, lsAllProcess)
        
        saveSolution_YS_TS(vAncSerRegulation_YS_TS, objZone.ZoneOutput.dicAncSerRegulation_YS_TS, setFSYearSteps, setTimeSliceSN) 
        saveSolution_YS_TS(vAncSer10MinReserve_YS_TS, objZone.ZoneOutput.dicAncSer10MinReserve_YS_TS, setFSYearSteps, setTimeSliceSN) 
        saveSolution_YS_TS(vAncSer30MinReserve_YS_TS, objZone.ZoneOutput.dicAncSer30MinReserve_YS_TS, setFSYearSteps, setTimeSliceSN) 
        
        #### unit commitment
        vPctCapacityCommit_YS_TS_PR, vPctCapacityGenerate_YS_TS_PR, vPctCapacityAncSer_YS_TS_PR \
            = model_solution_process.getZoneUnitCommitResult(instance, objZone, lsAllProcess, ZoneProcessSet)
            
        saveSolution_YS_TS_PR(vPctCapacityCommit_YS_TS_PR, objZone.ZoneOutput.dicPctCapacityCommit_YS_TS_PR, setFSYearSteps, setTimeSliceSN, ZoneProcessSet)
        saveSolution_YS_TS_PR(vPctCapacityGenerate_YS_TS_PR, objZone.ZoneOutput.dicPctCapacityGenerate_YS_TS_PR, setFSYearSteps, setTimeSliceSN, ZoneProcessSet)
        saveSolution_YS_TS_PR(vPctCapacityAncSer_YS_TS_PR, objZone.ZoneOutput.dicPctCapacityAncSer_YS_TS_PR, setFSYearSteps, setTimeSliceSN, ZoneProcessSet)
        
        #----------------------------------------------------
        # endogenous output
        #----------------------------------------------------

        ##### generation cost / electricity price (USD/kWh)
        endProcessLCOE_YS_PR, endPowerGenCost_YS_TS, endWholeSalePrice_YS_TS \
            = model_solution_process.cal_endGenTechCost(instance, objZone, setTimeSliceSN)
        saveSolution_YS_PR(endProcessLCOE_YS_PR, objZone.ZoneOutput.dicProcessLCOE_YS_PR, setFSYearSteps, ZoneProcessSet) 
        saveSolution_YS_TS(endPowerGenCost_YS_TS, objZone.ZoneOutput.dicPowerGenCost_YS_TS, setFSYearSteps, setTimeSliceSN) 
        saveSolution_YS_TS(endWholeSalePrice_YS_TS, objZone.ZoneOutput.dicPowerWholeSalePrice_YS_TS, setFSYearSteps, setTimeSliceSN) 
        '''
        #----------------------------------------------------
        # Agent-based model
        #----------------------------------------------------

        # day-ahead market price, real-time market price
        endDayAheadMarketPrice_YS_TS, endRealTimeMarketPrice_YS_TS = _get_endMarketNodalPrice(instance, objZone, setTimeSliceSN)
        model_process.saveSolution_YS_TS(endDayAheadMarketPrice_YS_TS, objZone.ZoneOutput.dicDAMNodalPrice_YS_TS, setFSYearSteps, setTimeSliceSN) 
        model_process.saveSolution_YS_TS(endRealTimeMarketPrice_YS_TS, objZone.ZoneOutput.dicRTMNodalPrice_YS_TS, setFSYearSteps, setTimeSliceSN) 

        '''
        
    return
        


def updateMarketSolution(instance, objMarket):

    #----------------------------------------------------
    # aggregate subregion output
    #----------------------------------------------------

    for indexZone, objZone in enumerate(objMarket.lsZone):

        objCountry = instance.lsRegion[objZone.iRegionIndex].lsCountry[objZone.iCountryIndex]
        
        setFSYearSteps = [ iFSYearSteps for iFSYearSteps in instance.iFSYearSteps_YS ]
        setTimeSliceSN = [ objTimeSlice.iTSIndex for objTimeSlice in instance.lsTimeSlice ]
        setMarketProcess = [ objProcessAssump.sProcessName for objProcessAssump in instance.lsProcessDefObjs ]
        setMarketProcessStrg = [ objProcessAssump.sProcessName for objProcessAssump in instance.lsProcessDefObjs if objProcessAssump.sOperationMode == "Storage"]
        setCommodity = [ objCommodity.sCommodityName for objCommodity in objCountry.lsCommodity ]        
        
        ##### power/heat generation and balance
        sumMarketVariable_X_Y(objZone.ZoneOutput.dicGenCapacity_YS_PR, objMarket.MarketOutput.dicGenCapacity_YS_PR, setFSYearSteps, setMarketProcess, indexZone )
        sumMarketVariable_X_Y(objZone.ZoneOutput.dicGenNewCapacity_YS_PR, objMarket.MarketOutput.dicGenNewCapacity_YS_PR, setFSYearSteps, setMarketProcess, indexZone )
        sumMarketVariable_X_Y_Z(objZone.ZoneOutput.dicPowerGen_YS_TS_PR, objMarket.MarketOutput.dicPowerGen_YS_TS_PR, setFSYearSteps, setTimeSliceSN, setMarketProcess, indexZone )
        sumMarketVariable_X_Y_Z(objZone.ZoneOutput.dicPowerOutput_YS_TS_PR, objMarket.MarketOutput.dicPowerOutput_YS_TS_PR, setFSYearSteps, setTimeSliceSN, setMarketProcess, indexZone )
        sumMarketVariable_X_Y_Z(objZone.ZoneOutput.dicHeatGen_YS_TS_PR, objMarket.MarketOutput.dicHeatGen_YS_TS_PR, setFSYearSteps, setTimeSliceSN, setMarketProcess, indexZone )
        sumMarketVariable_X_Y_Z(objZone.ZoneOutput.dicHeatOutput_YS_TS_PR, objMarket.MarketOutput.dicHeatOutput_YS_TS_PR, setFSYearSteps, setTimeSliceSN, setMarketProcess, indexZone )

        ##### storage
        sumMarketVariable_X_Y_Z(objZone.ZoneOutput.dicStrgInput_YS_TS_ST, objMarket.MarketOutput.dicStrgInput_YS_TS_ST, setFSYearSteps, setTimeSliceSN, setMarketProcessStrg, indexZone )
        sumMarketVariable_X_Y_Z(objZone.ZoneOutput.dicStrgOutput_YS_TS_ST, objMarket.MarketOutput.dicStrgOutput_YS_TS_ST, setFSYearSteps, setTimeSliceSN, setMarketProcessStrg, indexZone )

        ##### cost
        sumMarketVariable_X_Y(objZone.ZoneOutput.dicYearInvest_YS_PR, objMarket.MarketOutput.dicYearInvest_YS_PR, setFSYearSteps, setMarketProcess, indexZone )
        sumMarketVariable_X_Y(objZone.ZoneOutput.dicGenCAPEX_YS_PR, objMarket.MarketOutput.dicGenCAPEX_YS_PR, setFSYearSteps, setMarketProcess, indexZone )
        sumMarketVariable_X_Y(objZone.ZoneOutput.dicGenOPEX_YS_PR, objMarket.MarketOutput.dicGenOPEX_YS_PR, setFSYearSteps, setMarketProcess, indexZone )
        sumMarketVariable_X_Y(objZone.ZoneOutput.dicFuelCost_YS_PR, objMarket.MarketOutput.dicFuelCost_YS_PR, setFSYearSteps, setMarketProcess, indexZone )
        sumMarketVariable_X_Y(objZone.ZoneOutput.dicEmissionCost_YS_PR, objMarket.MarketOutput.dicEmissionCost_YS_PR, setFSYearSteps, setMarketProcess, indexZone )
        sumMarketVariable_X_Y(objZone.ZoneOutput.dicRunningCost_YS_PR, objMarket.MarketOutput.dicRunningCost_YS_PR, setFSYearSteps, setMarketProcess, indexZone )

        ##### fuel (MWh)
        sumMarketVariable_X_Y_Z(objZone.ZoneOutput.dicFuelConsum_YS_TS_PR, objMarket.MarketOutput.dicFuelConsum_YS_TS_PR, setFSYearSteps, setTimeSliceSN, setMarketProcess, indexZone )
 
        ##### ancillary service (MW)
        sumMarketVariable_X_Y(objZone.ZoneOutput.dicAncSerRegulation_YS_TS, objMarket.MarketOutput.dicAncSerRegulation_YS_TS, setFSYearSteps, setTimeSliceSN, indexZone )
        sumMarketVariable_X_Y(objZone.ZoneOutput.dicAncSer10MinReserve_YS_TS, objMarket.MarketOutput.dicAncSer10MinReserve_YS_TS, setFSYearSteps, setTimeSliceSN, indexZone )
        sumMarketVariable_X_Y(objZone.ZoneOutput.dicAncSer30MinReserve_YS_TS, objMarket.MarketOutput.dicAncSer30MinReserve_YS_TS, setFSYearSteps, setTimeSliceSN, indexZone )
            
        #----------------------------------------------------
        # endogenous output
        #----------------------------------------------------

        ##### generation
        sumMarketVariable_X_Y(objZone.ZoneOutput.dicZonePowerGen_YS_TS, objMarket.MarketOutput.dicMarketPowerGen_YS_TS, setFSYearSteps, setTimeSliceSN, indexZone )
        sumMarketVariable_X_Y(objZone.ZoneOutput.dicZoneHeatGen_YS_TS, objMarket.MarketOutput.dicMarketHeatGen_YS_TS, setFSYearSteps, setTimeSliceSN, indexZone )
        
        ##### generation cost LCOE (USD/kWh)
        model_solution_process.getMarketProcessLCOE_YS_PR(objMarket.MarketOutput.dicPowerGen_YS_TS_PR, objMarket.MarketOutput.dicYearInvest_YS_PR, \
                                                           objMarket.MarketOutput.dicProcessLCOE_YS_PR, setFSYearSteps, setTimeSliceSN, setMarketProcess )

        ##### do not update here if the methodology is SRMC
        ## electricity price (USD/kWh)
        model_solution_process.getMarketPowerGenCost_YS_TS(objMarket.MarketOutput.dicPowerGen_YS_TS_PR, objMarket.MarketOutput.dicProcessLCOE_YS_PR, objMarket.MarketOutput.dicPowerGenCost_YS_TS, setFSYearSteps, setTimeSliceSN, setMarketProcess )
        ## Whole Sale price (USD/kWh)
        pWholeSalePriceMarkUp_YS= {}    # preserve for future modification
        for sYearStep in setFSYearSteps:
            pWholeSalePriceMarkUp_YS[sYearStep] = 0
        model_solution_process.cal_RegionWholeSalePrice_YS_TS(objMarket.MarketOutput.dicPowerGenCost_YS_TS, pWholeSalePriceMarkUp_YS, objMarket.MarketOutput.dicPowerWholeSalePrice_YS_TS, setFSYearSteps, setTimeSliceSN )

        ##### emission (M.Tonnes/Year)
        sumMarketVariable_X(objZone.ZoneOutput.dicCO2Emission_YS, objMarket.MarketOutput.dicCO2Emission_YS, setFSYearSteps, indexZone)
        sumMarketVariable_X_Y(objZone.ZoneOutput.dicCO2Emission_YS_TS, objMarket.MarketOutput.dicCO2Emission_YS_TS, setFSYearSteps, setTimeSliceSN, indexZone )
        sumMarketVariable_X_Y(objZone.ZoneOutput.dicEmissionCaptured_YS_TS, objMarket.MarketOutput.dicEmissionCaptured_YS_TS, setFSYearSteps, setTimeSliceSN, indexZone )

        ##### fuel consumption (MWh)
        sumMarketVariable_X_Y_Z(objZone.ZoneOutput.dicFuelConsum_YS_TS_CM, objMarket.MarketOutput.dicFuelConsum_YS_TS_CM, setFSYearSteps, setTimeSliceSN, setCommodity, indexZone )


    #### unit commitment
    model_solution_process.getMarketUnitCommitResult(instance, objMarket)

    #----------------------------------------------------
    # transmisson output
    #----------------------------------------------------

    setTransmission = [ objTrsm.PowerFlowID for objTrsm in objMarket.lsTransmission ]

    for sTrans in setTransmission:
        for iYearStep in setFSYearSteps:
            objMarket.MarketOutput.dicTransCapacity_YS_TR[iYearStep, sTrans] = 0
            objMarket.MarketOutput.dicTransNewCapacity_YS_TR[iYearStep, sTrans] = 0
            objMarket.MarketOutput.dicTransCAPEX_YS_TR[iYearStep, sTrans] = 0
            objMarket.MarketOutput.dicTransOPEX_YS_TR[iYearStep, sTrans] = 0
            for sTimeSlice in setTimeSliceSN:
                objMarket.MarketOutput.dicTransUsage_YS_TS_TR[iYearStep, sTimeSlice, sTrans] = 0

    vTransCapacity_YS_TR, vTransNewCapacity_YS_TR, vTransCAPEX_YS_TR, vTransOPEX_YS_TR, vTransUsage_YS_TS_TR = \
        model_solution_process.getTransmissionResult(instance, objMarket, setTransmission)

    saveSolution_YS_PR(vTransCapacity_YS_TR, objMarket.MarketOutput.dicTransCapacity_YS_TR, instance.iFSYearSteps_YS, setTransmission)
    saveSolution_YS_PR(vTransNewCapacity_YS_TR, objMarket.MarketOutput.dicTransNewCapacity_YS_TR, instance.iFSYearSteps_YS, setTransmission)
    saveSolution_YS_PR(vTransCAPEX_YS_TR, objMarket.MarketOutput.dicTransCAPEX_YS_TR, instance.iFSYearSteps_YS, setTransmission)
    saveSolution_YS_PR(vTransOPEX_YS_TR, objMarket.MarketOutput.dicTransOPEX_YS_TR, instance.iFSYearSteps_YS, setTransmission)
    saveSolution_YS_TS_PR(vTransUsage_YS_TS_TR, objMarket.MarketOutput.dicTransUsage_YS_TS_TR, instance.iFSYearSteps_YS, setTimeSliceSN, setTransmission) 


    #----------------------------------------------------
    # Agent Generator
    #----------------------------------------------------
    '''
    objMarket.listGenerator = sorted(objMarket.listGenerator, key=lambda listGenerator: listGenerator.sGeneratorID)
    setGenerator = [ objGenerator.sGeneratorID for objGenerator in objMarket.listGenerator ]

    for sGeneratorID in setGenerator:
        for iYearStep in setFSYearSteps:
            objMarket.MarketOutput.dicGeneratorProfit_YS_GR[iYearStep, sGeneratorID] = 0
            for objGenTech in objMarket.listRegionGenTech:
                objMarket.MarketOutput.dicGeneratorCapacity_YS_PR_GR[iYearStep, objGenTech.sGenTechID, sGeneratorID] = 0

    vGeneratorProfit_YS_GR, vGeneratorCapacity_YS_PR_GR = model_solution_process._getGeneratorResult(instance, objMarket)

    saveSolution_YS_PR(vGeneratorProfit_YS_GR, objMarket.MarketOutput.dicGeneratorProfit_YS_GR, instance.iFSYearSteps_YS, setGenerator)
    saveSolution_YS_TS_PR(vGeneratorCapacity_YS_PR_GR, objMarket.MarketOutput.dicGeneratorCapacity_YS_PR_GR, instance.iFSYearSteps_YS, setMarketProcess, setGenerator) 
    '''
    
    return
    


#------------------------------------------------------------------
# save subregion solution variables to region/subregion object
#------------------------------------------------------------------

def saveSolution_YS(dicData, targetDictionary, setYearStep):

    for sYearStep in setYearStep:
        if type(dicData) is dict:
            targetDictionary[sYearStep] = round(dicData[sYearStep], 4)
        else:
            targetDictionary[sYearStep] = round(dicData[sYearStep].value, 4)


def saveSolution_YS_PR(dicData, targetDictionary, setYearStep, setProcess):

    for sProcess in setProcess:
        for sYearStep in setYearStep:
            if type(dicData) is dict:
                targetDictionary[sYearStep, sProcess] = round(dicData[sYearStep, sProcess], 4)
            else:
                targetDictionary[sYearStep, sProcess] = round(dicData[sYearStep, sProcess].value, 4)


def saveSolution_YS_PR_ExcCurrentYear(dicData, targetDictionary, setYearStep, setProcess):

    listYR = list(setYearStep)
    listYR.pop(0)
    # skip the first year period
    for sProcess in setProcess:
        for sYearStep in setYearStep:
            if type(dicData) is dict:
                targetDictionary[sYearStep, sProcess] = round(dicData[sYearStep, sProcess], 4)
            else:
                targetDictionary[sYearStep, sProcess] = round(dicData[sYearStep, sProcess].value, 4)


def saveSolution_YS_TS(dicData, targetDictionary, setYearStep, setTimeSliceSN):

    for sTimeSliceIndex in setTimeSliceSN:
        for sYearStep in setYearStep:
            if type(dicData) is dict:
                targetDictionary[sYearStep, sTimeSliceIndex] = round(dicData[sYearStep, sTimeSliceIndex], 4)
            else:
                targetDictionary[sYearStep, sTimeSliceIndex] = round(dicData[sYearStep, sTimeSliceIndex].value, 4)


def saveSolution_YS_TS_PR(dicData, targetDictionary, setYearStep, setTimeSliceSN, setProcess):

    for sProcess in setProcess:
        for sYearStep in setYearStep:
            for sTimeSliceIndex in setTimeSliceSN:
                if type(dicData) is dict:
                    targetDictionary[sYearStep, sTimeSliceIndex, sProcess] = round(dicData[sYearStep, sTimeSliceIndex, sProcess], 4)
                else:
                    targetDictionary[sYearStep, sTimeSliceIndex, sProcess] = round(dicData[sYearStep, sTimeSliceIndex, sProcess].value, 4)



#------------------------------------------------------------------
# update region solution variables
#------------------------------------------------------------------

def sumMarketVariable_X(dicData, targetDictionary, setYS, indexZone):

    for iYearStep in setYS:
        if iYearStep not in targetDictionary:
            targetDictionary[iYearStep] = 0
        if indexZone == 0:
            targetDictionary[iYearStep] = 0  # initialize
        if iYearStep in dicData:
            targetDictionary[iYearStep] += round(dicData[iYearStep], 4)


def sumMarketVariable_X_Y(dicData, targetDictionary, setYS, setProcess, indexZone):

    for sProcess in setProcess:
        for iYearStep in setYS:
            if (iYearStep, sProcess) not in targetDictionary:
                targetDictionary[iYearStep, sProcess] = 0
            if indexZone == 0:
                targetDictionary[iYearStep, sProcess] = 0  # initialize    
            if (iYearStep, sProcess) in dicData: # if the subregion doesn't include the technology, then skip
                targetDictionary[iYearStep, sProcess] += round(dicData[iYearStep, sProcess], 4)


def sumMarketVariable_X_Y_Z(dicData, targetDictionary, setYS, IndexTS, setProcess, indexZone):

    for sProcess in setProcess:
        for iYearStep in setYS:
            for sIndexTS in IndexTS:
                if (iYearStep, sIndexTS, sProcess) not in targetDictionary:
                    targetDictionary[iYearStep, sIndexTS, sProcess] = 0  
                if indexZone == 0:
                    targetDictionary[iYearStep, sIndexTS, sProcess] = 0  # initialize 
                if (iYearStep, sIndexTS, sProcess) in dicData: # if the subregion doesn't include the technology, then skip
                    targetDictionary[iYearStep, sIndexTS, sProcess] += round(dicData[iYearStep, sIndexTS, sProcess], 4)




