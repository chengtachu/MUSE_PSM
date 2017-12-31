# -*- coding: utf-8 -*-

import copy
from decimal import Decimal  

def getTotalAndNewCapacity(instance, objZone, lsAllProcess):

    vGenCapacity_YS_PR = {}
    vNewBuild_YS_PR = {}

    # initialization
    for objZoneProcess in objZone.lsProcessAssump:
        for iYearStep in instance.iFSYearSteps_YS:
            vGenCapacity_YS_PR[iYearStep, objZoneProcess.sProcessName] = 0
            vNewBuild_YS_PR[iYearStep, objZoneProcess.sProcessName] = 0

    # total capacity
    for objProcess in lsAllProcess:
        for iYearStep in instance.iFSYearSteps_YS:
            if iYearStep >= objProcess.CommitTime and iYearStep < objProcess.DeCommitTime:
                 vGenCapacity_YS_PR[iYearStep, objProcess.sProcessName] += objProcess.Capacity

    # total planned plant
    for objProcess in lsAllProcess:
        for iYearStep in instance.iFSYearSteps_YS:
            if iYearStep == objProcess.CommitTime:
                 vNewBuild_YS_PR[iYearStep, objProcess.sProcessName] += objProcess.Capacity

    return vGenCapacity_YS_PR, vNewBuild_YS_PR



def getPowerOutputAndGeneration(instance, objZone, lsAllProcess):

    vPowerOutput_YS_TS_PR = {}
    vPowerGen_YS_TS_PR = {}
    vZonePowerOutput_YS_TS = {}
    vZonePowerGen_YS_TS = {}
    vHeatOutput_YS_TS_PR = {}
    vHeatGen_YS_TS_PR = {}
    vZoneHeatOutput_YS_TS = {}
    vZoneHeatGen_YS_TS = {}

    # initialization
    for objZoneProcess in objZone.lsProcessAssump:
        for iYearStep in instance.iFSYearSteps_YS:
            for indexTS, objTimeSlice in enumerate(instance.lsTimeSlice):
                vPowerOutput_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, objZoneProcess.sProcessName] = 0
                vPowerGen_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, objZoneProcess.sProcessName] = 0
                vZonePowerOutput_YS_TS[iYearStep, objTimeSlice.iTSIndex] = 0
                vZonePowerGen_YS_TS[iYearStep, objTimeSlice.iTSIndex] = 0
                vHeatOutput_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, objZoneProcess.sProcessName] = 0
                vHeatGen_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, objZoneProcess.sProcessName] = 0
                vZoneHeatOutput_YS_TS[iYearStep, objTimeSlice.iTSIndex] = 0
                vZoneHeatGen_YS_TS[iYearStep, objTimeSlice.iTSIndex] = 0

    for objProcess in lsAllProcess:
        for indexYR, iYearStep in enumerate(instance.iFSYearSteps_YS):
            for indexTS, objTimeSlice in enumerate(instance.lsTimeSlice):
                indexYear = instance.iFSBaseYearIndex + indexYR
                if objProcess.fHourlyPowerOutput_TS_YS[indexTS, indexYear] is not 0:
                    # power output
                    fOutput = round(objProcess.fHourlyPowerOutput_TS_YS[indexTS, indexYear],2)
                    vPowerOutput_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, objProcess.sProcessName] += fOutput   # MW
                    vPowerGen_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, objProcess.sProcessName] += fOutput * objTimeSlice.iRepHoursInYear   # MWh
                    vZonePowerOutput_YS_TS[iYearStep, objTimeSlice.iTSIndex] += fOutput     # MW
                    vZonePowerGen_YS_TS[iYearStep, objTimeSlice.iTSIndex] += fOutput * objTimeSlice.iRepHoursInYear     # MWh
                    # heat output
                    fOutput = round(objProcess.fHourlyHeatOutput_TS_YS[indexTS, indexYear],2)
                    vHeatOutput_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, objProcess.sProcessName] += fOutput   # MW
                    vHeatGen_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, objProcess.sProcessName] += fOutput * objTimeSlice.iRepHoursInYear   # MWh
                    vZoneHeatOutput_YS_TS[iYearStep, objTimeSlice.iTSIndex] += fOutput   # MW
                    vZoneHeatGen_YS_TS[iYearStep, objTimeSlice.iTSIndex] += fOutput * objTimeSlice.iRepHoursInYear   # MWh
                    
    return vPowerOutput_YS_TS_PR, vPowerGen_YS_TS_PR, vZonePowerOutput_YS_TS, vZonePowerGen_YS_TS, \
            vHeatOutput_YS_TS_PR, vHeatGen_YS_TS_PR, vZoneHeatOutput_YS_TS, vZoneHeatGen_YS_TS


def getStoragePowerOperation(instance, objZone, lsAllProcess, ZoneStrgProcessSet):

    vStrgInput_YS_TS_ST = {}
    vStrgOuput_YS_TS_ST = {}

    # initialization
    for sStorageTech in ZoneStrgProcessSet:
        for iYearStep in instance.iFSYearSteps_YS:
            for indexTS, objTimeSlice in enumerate(instance.lsTimeSlice):
                vStrgInput_YS_TS_ST[iYearStep, objTimeSlice.iTSIndex, sStorageTech] = 0
                vStrgOuput_YS_TS_ST[iYearStep, objTimeSlice.iTSIndex, sStorageTech] = 0

    for objProcess in lsAllProcess:
        if objProcess.sProcessName in ZoneStrgProcessSet:
            for indexYR, iYearStep in enumerate(instance.iFSYearSteps_YS):
                indexYear = instance.iFSBaseYearIndex + indexYR
                for indexTS, objTimeSlice in enumerate(instance.lsTimeSlice):
                    if objProcess.fHourlyPowerOutput_TS_YS[indexTS, indexYear] > 0: # output
                        vStrgOuput_YS_TS_ST[iYearStep, objTimeSlice.iTSIndex, objProcess.sProcessName] += objProcess.fHourlyPowerOutput_TS_YS[indexTS, indexYear]   # MW
                    else:   # input
                        vStrgInput_YS_TS_ST[iYearStep, objTimeSlice.iTSIndex, objProcess.sProcessName] += objProcess.fHourlyPowerOutput_TS_YS[indexTS, indexYear]   # MW

    return vStrgInput_YS_TS_ST, vStrgOuput_YS_TS_ST


def getProcessMainResult(instance, objZone, lsAllProcess):

    objCountry = instance.lsRegion[objZone.iRegionIndex].lsCountry[objZone.iCountryIndex]
    setZoneCommodity = [objCommodity.sCommodityName for objCommodity in objCountry.lsCommodity]
    
    vGenCAPEX_YS_PR = {}
    vGenOPEX_YS_PR = {}
    vFuelCost_YS_PR = {}
    vEmissionCost_YS_PR = {}
    vRunningCost_YS_PR = {}
    vYearInvest_YS_PR = {}
    vFuelConsum_YS_TS_PR = {}
    endFuelConsumption_YS_TS_CM = {}
    endCO2Emission_YS = {}
    endCO2Emission_YS_TS = {}
    endEmissionCaptured_YS_TS = {}

    #------------------------------------------------
    # initialization
    for objZoneProcess in objZone.lsProcessAssump:
        for iYearStep in instance.iFSYearSteps_YS:
            vGenCAPEX_YS_PR[iYearStep, objZoneProcess.sProcessName] = 0
            vGenOPEX_YS_PR[iYearStep, objZoneProcess.sProcessName] = 0
            vFuelCost_YS_PR[iYearStep, objZoneProcess.sProcessName] = 0
            vEmissionCost_YS_PR[iYearStep, objZoneProcess.sProcessName] = 0
            vRunningCost_YS_PR[iYearStep, objZoneProcess.sProcessName] = 0
            vYearInvest_YS_PR[iYearStep, objZoneProcess.sProcessName] = 0
            for indexTS, objTimeSlice in enumerate(instance.lsTimeSlice):
                vFuelConsum_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, objZoneProcess.sProcessName] = 0

    for iYearStep in instance.iFSYearSteps_YS:
        endCO2Emission_YS[iYearStep] = 0
        for indexTS, objTimeSlice in enumerate(instance.lsTimeSlice):
            endCO2Emission_YS_TS[iYearStep, objTimeSlice.iTSIndex] = 0
            endEmissionCaptured_YS_TS[iYearStep, objTimeSlice.iTSIndex] = 0
            for sFuel in setZoneCommodity:
                endFuelConsumption_YS_TS_CM[iYearStep, objTimeSlice.iTSIndex, sFuel] = 0

    #-------------------------------------------------
    # main parameters
    for objProcess in lsAllProcess:

        # get the carrier object
        for indexP, objCommodity in enumerate(objCountry.lsCommodity):
            if objCommodity.sCommodityName == objProcess.sFuel:
                objFuel = objCommodity
                break

        for indexYR, iYearStep in enumerate(instance.iFSYearSteps_YS):
            indexYear = instance.iFSBaseYearIndex + indexYR

            if objProcess.CommitTime <= iYearStep and objProcess.DeCommitTime > iYearStep:

                # MillionUSD / year 
                vGenCAPEX_YS_PR[iYearStep, objProcess.sProcessName] += objProcess.fAnnualCapex
                vGenOPEX_YS_PR[iYearStep, objProcess.sProcessName] += (objProcess.fAnnualFixedCost - objProcess.fAnnualCapex)

                for indexTS, objTimeSlice in enumerate(instance.lsTimeSlice):
                    if objProcess.fHourlyPowerOutput_TS_YS[indexTS, indexYear] > 0:

                        fPlantGeneratoin = objProcess.fHourlyPowerOutput_TS_YS[indexTS, indexYear] * objTimeSlice.iRepHoursInYear    # MWh
                        fPlantGeneratoin = float('{:.2f}'.format(Decimal(fPlantGeneratoin)))

                        # MWh * USD/kWh / 1000 = M.USD
                        vRunningCost_YS_PR[iYearStep, objProcess.sProcessName] += fPlantGeneratoin * float(objProcess.RunningCost) / 1000

                        # fuel cost, emission cost and fuel consumption for dispatchable
                        if objProcess.sOperationMode == "Dispatch":

                            #----------------- fuel consumption ------------
                            fProcessEff = max(objProcess.EffPowerCM, objProcess.EffPowerBP)
                            fFuelConsumption = fPlantGeneratoin / (fProcessEff / 100)  # MWh
                            vFuelConsum_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, objProcess.sProcessName] += fFuelConsumption # MWh
                            endFuelConsumption_YS_TS_CM[iYearStep, objTimeSlice.iTSIndex, objFuel.sCommodityName] += fFuelConsumption # MWh

                            #----------------- fuel cost ------------
                            # get fuel price (USD/LOE)
                            fFuelPrice = objFuel.fFuelPrice_TS_YS[indexTS,indexYear]
                            # conver fuel cost from (USD/LOE) to (USD/kWh)  
                            # fFuelPrice = fFuelPrice / 10.46  USD/LOE -> USD/kWh
                            # fFuelPrice = fFuelPrice / 277.8  MUSD/PJ -> MUSD/GWh = USD/kWh
                            fFuelPrice = fFuelPrice / 10.46

                            vFuelCost_YS_PR[iYearStep, objProcess.sProcessName] += fFuelConsumption * fFuelPrice / 1000  # M.USD 

                            #-------------- emission cost ------------
                            fCCSCaptureRate = objProcess.CCSCaptureRate / 100
                            fEmissionFactor = objFuel.fEmissionFactor_CO2
                            fFuelConsumption = fFuelConsumption * 0.0000036         # MWh -> PJ
                            fCarbonCost = objCountry.fCarbonCost_YS[indexYear]

                            # M.Tonne/PJ * PJ * USD/Tonne = M.USD
                            if objFuel.sCategory != "biofuel":
                                vEmissionCost_YS_PR[iYearStep, objProcess.sProcessName] += fEmissionFactor * fFuelConsumption * (1-fCCSCaptureRate) * fCarbonCost
                            else:
                                vEmissionCost_YS_PR[iYearStep, objProcess.sProcessName] += fEmissionFactor * fFuelConsumption * (1-fCCSCaptureRate) * fCarbonCost
                                vEmissionCost_YS_PR[iYearStep, objProcess.sProcessName] += fEmissionFactor * fFuelConsumption * fCCSCaptureRate * fCarbonCost * -1

                            # emission (M.Tonnes/Year)
                            if objFuel.sCategory != "biofuel":
                                endCO2Emission_YS[iYearStep] += fEmissionFactor * fFuelConsumption * (1-fCCSCaptureRate)
                                endCO2Emission_YS_TS[iYearStep, objTimeSlice.iTSIndex] += fEmissionFactor * fFuelConsumption * (1-fCCSCaptureRate)
                                endEmissionCaptured_YS_TS[iYearStep, objTimeSlice.iTSIndex] += fEmissionFactor * fFuelConsumption * fCCSCaptureRate
                            else:
                                endCO2Emission_YS[iYearStep] += fEmissionFactor * fFuelConsumption * (1-fCCSCaptureRate)
                                endCO2Emission_YS[iYearStep] += fEmissionFactor * fFuelConsumption * fCCSCaptureRate * -1
                                endCO2Emission_YS_TS[iYearStep, objTimeSlice.iTSIndex] += fEmissionFactor * fFuelConsumption * (1-fCCSCaptureRate)
                                endCO2Emission_YS_TS[iYearStep, objTimeSlice.iTSIndex] += fEmissionFactor * fFuelConsumption * fCCSCaptureRate * -1
                                endEmissionCaptured_YS_TS[iYearStep, objTimeSlice.iTSIndex] += fEmissionFactor * fFuelConsumption * fCCSCaptureRate

    # total year investment
    for objZoneProcess in objZone.lsProcessAssump:
        for iYearStep in instance.iFSYearSteps_YS:
            vYearInvest_YS_PR[iYearStep, objZoneProcess.sProcessName] += vGenCAPEX_YS_PR[iYearStep, objZoneProcess.sProcessName]
            vYearInvest_YS_PR[iYearStep, objZoneProcess.sProcessName] += vGenOPEX_YS_PR[iYearStep, objZoneProcess.sProcessName]
            vYearInvest_YS_PR[iYearStep, objZoneProcess.sProcessName] += vRunningCost_YS_PR[iYearStep, objZoneProcess.sProcessName]
            vYearInvest_YS_PR[iYearStep, objZoneProcess.sProcessName] += vFuelCost_YS_PR[iYearStep, objZoneProcess.sProcessName]
            vYearInvest_YS_PR[iYearStep, objZoneProcess.sProcessName] += vEmissionCost_YS_PR[iYearStep, objZoneProcess.sProcessName]

    return vGenCAPEX_YS_PR, vGenOPEX_YS_PR, vFuelCost_YS_PR, vEmissionCost_YS_PR, vRunningCost_YS_PR, vYearInvest_YS_PR, \
        vFuelConsum_YS_TS_PR, endFuelConsumption_YS_TS_CM, endCO2Emission_YS, endCO2Emission_YS_TS, endEmissionCaptured_YS_TS



def getAncSerResult(instance, objZone, lsAllProcess):

    vAncSerRegulation_YS_TS = {}
    vAncSer10MinReserve_YS_TS = {}
    vAncSer30MinReserve_YS_TS = {}
    
    # initialization
    for iYearStep in instance.iFSYearSteps_YS:
        for objTimeSlice in instance.lsTimeSlice:
            vAncSerRegulation_YS_TS[iYearStep, objTimeSlice.iTSIndex] = 0
            vAncSer10MinReserve_YS_TS[iYearStep, objTimeSlice.iTSIndex] = 0
            vAncSer30MinReserve_YS_TS[iYearStep, objTimeSlice.iTSIndex] = 0

    for objProcess in lsAllProcess:
        for indexYR, iYearStep in enumerate(instance.iFSYearSteps_YS):
            indexYear = instance.iFSBaseYearIndex + indexYR
            for indexTS, objTimeSlice in enumerate(instance.lsTimeSlice):
                vAncSerRegulation_YS_TS[iYearStep, objTimeSlice.iTSIndex] += round(objProcess.fASRegulation_TS_YS[indexTS, indexYear],2)
                vAncSer10MinReserve_YS_TS[iYearStep, objTimeSlice.iTSIndex] += round(objProcess.fAS10MinReserve_TS_YS[indexTS, indexYear],2)
                vAncSer30MinReserve_YS_TS[iYearStep, objTimeSlice.iTSIndex] += round(objProcess.fAS30MinReserve_TS_YS[indexTS, indexYear],2)
                
    return vAncSerRegulation_YS_TS, vAncSer10MinReserve_YS_TS, vAncSer30MinReserve_YS_TS



def getZoneUnitCommitResult(instance, objZone, lsAllProcess, ZoneProcessSet):

    vPctCapacityCommit_YS_TS_PR = {}
    vPctCapacityGenerate_YS_TS_PR = {}
    vPctCapacityAncSer_YS_TS_PR = {}
    
    # initialization
    for sProcessName in ZoneProcessSet:
        for iYearStep in instance.iFSYearSteps_YS:            
            for indexTS, objTimeSlice in enumerate(instance.lsTimeSlice):
                vPctCapacityCommit_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, sProcessName] = 0
                vPctCapacityGenerate_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, sProcessName] = 0
                vPctCapacityAncSer_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, sProcessName] = 0

    for objProcess in lsAllProcess:
        for indexYR, iYearStep in enumerate(instance.iFSYearSteps_YS):
            indexYear = instance.iFSBaseYearIndex + indexYR

            for indexTS, objTimeSlice in enumerate(instance.lsTimeSlice):
                # committed capacity
                if objProcess.iOperatoinStatus_TS_YS[indexTS, indexYear] != 0:
                    vPctCapacityCommit_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, objProcess.sProcessName] += objProcess.fDeratedCapacity
                # generation
                vPctCapacityGenerate_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, objProcess.sProcessName] += objProcess.fHourlyPowerOutput_TS_YS[indexTS, indexYear]
                # ancillary service allocated
                vPctCapacityAncSer_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, objProcess.sProcessName] += objProcess.fASRegulation_TS_YS[indexTS, indexYear]
                vPctCapacityAncSer_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, objProcess.sProcessName] += objProcess.fAS10MinReserve_TS_YS[indexTS, indexYear]
                vPctCapacityAncSer_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, objProcess.sProcessName] += objProcess.fAS30MinReserve_TS_YS[indexTS, indexYear]
                
    for sProcessName in ZoneProcessSet:
        for indexYR, iYearStep in enumerate(instance.iFSYearSteps_YS):
            indexYear = instance.iFSBaseYearIndex + indexYR
            for indexTS, objTimeSlice in enumerate(instance.lsTimeSlice):
                if objZone.ZoneOutput.dicGenCapacity_YS_PR[iYearStep, sProcessName] > 0:
                    vPctCapacityCommit_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, sProcessName] = round(vPctCapacityCommit_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, sProcessName] \
                            / objZone.ZoneOutput.dicGenCapacity_YS_PR[iYearStep, sProcessName] * 100, 2)
                    vPctCapacityGenerate_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, sProcessName] = round(vPctCapacityGenerate_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, sProcessName] \
                            / objZone.ZoneOutput.dicGenCapacity_YS_PR[iYearStep, sProcessName] * 100, 2)
                    vPctCapacityAncSer_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, sProcessName] = round(vPctCapacityAncSer_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, sProcessName] \
                            / objZone.ZoneOutput.dicGenCapacity_YS_PR[iYearStep, sProcessName] * 100, 2)
                
    return vPctCapacityCommit_YS_TS_PR, vPctCapacityGenerate_YS_TS_PR, vPctCapacityAncSer_YS_TS_PR



def getAggregateUnitCommitResult(instance, objMarket):

    vPctCapacityCommit_YS_TS_PR = {}
    vPctCapacityGenerate_YS_TS_PR = {}
    vPctCapacityAncSer_YS_TS_PR = {}
    
    setMarketProcess = [ objProcessAssump.sProcessName for objProcessAssump in instance.lsProcessDefObjs ]
    setFSYearSteps = [ iFSYearSteps for iFSYearSteps in instance.iFSYearSteps_YS ]
    setTimeSliceSN = [ objTimeSlice.iTSIndex for objTimeSlice in instance.lsTimeSlice ]
    
    MarketOutput = objMarket.MarketOutput
    
    # market value initialization
    for sProcessName in setMarketProcess:
        for iYearStep in instance.iFSYearSteps_YS:
            for iTSIndex in setTimeSliceSN:
                if (iYearStep, iTSIndex, sProcessName) not in MarketOutput.dicPctCapacityCommit_YS_TS_PR:
                    MarketOutput.dicPctCapacityCommit_YS_TS_PR[iYearStep, iTSIndex, sProcessName] = 0 
                if (iYearStep, iTSIndex, sProcessName) not in MarketOutput.dicPctCapacityGenerate_YS_TS_PR:
                    MarketOutput.dicPctCapacityGenerate_YS_TS_PR[iYearStep, iTSIndex, sProcessName] = 0 
                if (iYearStep, iTSIndex, sProcessName) not in MarketOutput.dicPctCapacityAncSer_YS_TS_PR:
                    MarketOutput.dicPctCapacityAncSer_YS_TS_PR[iYearStep, iTSIndex, sProcessName] = 0   
    
    
    for indexZone, objZone in enumerate(objMarket.lsZone):

        lsAllProcess = list(copy.copy(objZone.lsProcess))
        lsAllProcess.extend(copy.copy(objZone.lsProcessPlanned))

        ZoneProcessSet = [ objProcessAssump.sProcessName for objProcessAssump in objZone.lsProcessAssump ]
    
        # zone value initialization
        for sProcessName in ZoneProcessSet:
            for iYearStep in setFSYearSteps:            
                for iTSIndex in setTimeSliceSN:
                    vPctCapacityCommit_YS_TS_PR[iYearStep, iTSIndex, sProcessName] = 0
                    vPctCapacityGenerate_YS_TS_PR[iYearStep, iTSIndex, sProcessName] = 0
                    vPctCapacityAncSer_YS_TS_PR[iYearStep, iTSIndex, sProcessName] = 0
    
        for objProcess in lsAllProcess:
            for indexYR, iYearStep in enumerate(instance.iFSYearSteps_YS):
                indexYear = instance.iFSBaseYearIndex + indexYR
    
                for indexTS, objTimeSlice in enumerate(instance.lsTimeSlice):
                    # committed capacity
                    if objProcess.iOperatoinStatus_TS_YS[indexTS, indexYear] != 0:
                        vPctCapacityCommit_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, objProcess.sProcessName] += objProcess.fDeratedCapacity
                    # generation
                    vPctCapacityGenerate_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, objProcess.sProcessName] += objProcess.fHourlyPowerOutput_TS_YS[indexTS, indexYear]
                    # ancillary service allocated
                    vPctCapacityAncSer_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, objProcess.sProcessName] += objProcess.fASRegulation_TS_YS[indexTS, indexYear]
                    vPctCapacityAncSer_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, objProcess.sProcessName] += objProcess.fAS10MinReserve_TS_YS[indexTS, indexYear]
                    vPctCapacityAncSer_YS_TS_PR[iYearStep, objTimeSlice.iTSIndex, objProcess.sProcessName] += objProcess.fAS30MinReserve_TS_YS[indexTS, indexYear]    
        
    # update market values
    for sProcessName in setMarketProcess:
        for indexYR, iYearStep in enumerate(instance.iFSYearSteps_YS):
            for iTSIndex in setTimeSliceSN:
                fMarketProcessCapacity = MarketOutput.dicGenCapacity_YS_PR[iYearStep, sProcessName]
                if fMarketProcessCapacity > 0:
                    
                    MarketOutput.dicPctCapacityCommit_YS_TS_PR[iYearStep, iTSIndex, sProcessName] = \
                        round(vPctCapacityCommit_YS_TS_PR[iYearStep, iTSIndex, sProcessName] / fMarketProcessCapacity * 100, 2)
                        
                    MarketOutput.dicPctCapacityGenerate_YS_TS_PR[iYearStep, iTSIndex, sProcessName] = \
                        round(vPctCapacityGenerate_YS_TS_PR[iYearStep, iTSIndex, sProcessName] / fMarketProcessCapacity * 100, 2)
                        
                    MarketOutput.dicPctCapacityAncSer_YS_TS_PR[iYearStep, iTSIndex, sProcessName] = \
                        round(vPctCapacityAncSer_YS_TS_PR[iYearStep, iTSIndex, sProcessName] / fMarketProcessCapacity * 100, 2)

    return



def getProcessGenerationCost(instance, objZone, setTimeSliceSN):

    objMarket = instance.lsMarket[objZone.iMarketIndex]

    endProcessLCOE_YS_PR = {}
    endPowerGenCost_YS_TS = {}
    endWholeSalePrice_YS_TS = {}

    # initialization
    for objZoneProcess in objZone.lsProcessAssump:
        for iYearStep in instance.iFSYearSteps_YS:
            endProcessLCOE_YS_PR[iYearStep, objZoneProcess.sProcessName] = 0

    for iYearStep in instance.iFSYearSteps_YS:
        for sTimeSliceSN in setTimeSliceSN:
            endPowerGenCost_YS_TS[iYearStep, sTimeSliceSN] = 0
            endWholeSalePrice_YS_TS[iYearStep, sTimeSliceSN] = 0

    # annual generation cost of each technology (LCOE)
    for iYearStep in instance.iFSYearSteps_YS:
        for objZoneProcess in objZone.lsProcessAssump:
            fGenerationTechCost = 0
            fYearInvest =  objZone.ZoneOutput.dicYearInvest_YS_PR[iYearStep, objZoneProcess.sProcessName]  # M.USD
            fYearGeneration = sum(objZone.ZoneOutput.dicPowerGen_YS_TS_PR[iYearStep, sTimeSlice, objZoneProcess.sProcessName] for sTimeSlice in setTimeSliceSN) # MWh
            if fYearGeneration > 0:
                fGenerationTechCost = fYearInvest / fYearGeneration * 1000  # USD/KWh

            endProcessLCOE_YS_PR[iYearStep, objZoneProcess.sProcessName] = round(fGenerationTechCost, 4)

    # average generation cost of the subregoin - LCOE approach for vertical integrated system
    if objMarket.sModel == "VI":
        for iYearStep in instance.iFSYearSteps_YS:
            for sTimeSliceSN in setTimeSliceSN:
                fWeightedCost = 0
                fTotalGeneration = objZone.ZoneOutput.dicZonePowerGen_YS_TS[iYearStep, sTimeSliceSN]
                if fTotalGeneration > 0:
                    for objZoneProcess in objZone.lsProcessAssump:
                        fWeightedCost += endProcessLCOE_YS_PR[iYearStep, objZoneProcess.sProcessName] * objZone.ZoneOutput.dicPowerGen_YS_TS_PR[iYearStep, sTimeSliceSN, objZoneProcess.sProcessName] / fTotalGeneration
                endPowerGenCost_YS_TS[iYearStep, sTimeSliceSN] = round(fWeightedCost, 4)
    # marginal generation cost of the subregoin - profit approach for wholesale market
    elif objMarket.sModel == "WM":
        for indexYR, iYearStep in enumerate(instance.iFSYearSteps_YS):
            indexYear = instance.iFSBaseYearIndex + indexYR
            for indexTS, objTimeSlice in enumerate(instance.lsTimeSlice):
                fMarginalGenCost = objZone.aMarginalGenCost_TS_YS[indexTS, indexYear]
                endPowerGenCost_YS_TS[iYearStep, objTimeSlice.iTSIndex] = round(fMarginalGenCost, 4)

    # wholesale price
    for iYearStep in instance.iFSYearSteps_YS:
        for sTimeSliceSN in setTimeSliceSN:
            endWholeSalePrice_YS_TS[iYearStep, sTimeSliceSN] = endPowerGenCost_YS_TS[iYearStep, sTimeSliceSN]

    return endProcessLCOE_YS_PR, endPowerGenCost_YS_TS, endWholeSalePrice_YS_TS


def getTransmissionResult(instance, objMarket, setTransmission):

    vTransCapacity_YS_TR = {}
    vTransNewCapacity_YS_TR = {}
    vTransCAPEX_YS_TR = {}
    vTransOPEX_YS_TR = {}
    vTransUsage_YS_TS_TR = {}

    # initialization
    for sTrans in setTransmission:
        for iYearStep in instance.iFSYearSteps_YS:
            vTransCapacity_YS_TR[iYearStep, sTrans] = 0
            vTransNewCapacity_YS_TR[iYearStep, sTrans] = 0
            vTransCAPEX_YS_TR[iYearStep, sTrans] = 0
            vTransOPEX_YS_TR[iYearStep, sTrans] = 0
            for indexTS, objTimeSlice in enumerate(instance.lsTimeSlice):
                vTransUsage_YS_TS_TR[iYearStep, objTimeSlice.iTSIndex, sTrans] = 0

    for index, objTransFlow in enumerate(objMarket.lsTransmission):
        for indexYR, iYearStep in enumerate(instance.iFSYearSteps_YS):
            indexYear = instance.iFSBaseYearIndex + indexYR
            vTransCapacity_YS_TR[iYearStep, objTransFlow.PowerFlowID] = objTransFlow.fTransAccCapacity_YS[indexYear]
            vTransNewCapacity_YS_TR[iYearStep, objTransFlow.PowerFlowID] = objTransFlow.fTransNewBuild_YS[indexYear]
            vTransCAPEX_YS_TR[iYearStep, objTransFlow.PowerFlowID] = objTransFlow.CAPEX * objTransFlow.fCRF * objTransFlow.fTransAccCapacity_YS[indexYear]  / 1000 # M.USD
            vTransOPEX_YS_TR[iYearStep, objTransFlow.PowerFlowID] = objTransFlow.OPEX * objTransFlow.fTransAccCapacity_YS[indexYear] / 1000  # M.USD

            for indexTS, objTimeSlice in enumerate(instance.lsTimeSlice):
                vTransUsage_YS_TS_TR[iYearStep, objTimeSlice.iTSIndex, objTransFlow.PowerFlowID] = objTransFlow.fTransLineInput_TS_YS[indexTS, indexYear]

    return vTransCapacity_YS_TR, vTransNewCapacity_YS_TR, vTransCAPEX_YS_TR, vTransOPEX_YS_TR, vTransUsage_YS_TS_TR


'''
def get_endMarketNodalPrice(instance, objZone, setTimeSliceSN):

    objMarket = instance.lsMarket[objZone.iMarketIndex]

    endDayAheadMarketPrice_YS_TS = {}
    endRealTimeMarketPrice_YS_TS = {}

    # initiation
    for iYearStep in instance.iFSYearSteps_YS:
        for sTimeSliceSN in setTimeSliceSN:
            endDayAheadMarketPrice_YS_TS[iYearStep, sTimeSliceSN] = 0
            endRealTimeMarketPrice_YS_TS[iYearStep, sTimeSliceSN] = 0

    if objMarket.sModel == "AgentBasedPoolMarket" or objMarket.sModel == "AgentBasedPowerExchange":
        for indexYR, iYearStep in enumerate(instance.iFSYearSteps_YS):
            indexYear = instance.iFSBaseYearIndex + indexYR
            for indexTS, objTimeSlice in enumerate(instance.lsTimeSlice):
                endDayAheadMarketPrice_YS_TS[iYearStep, objTimeSlice.iTSIndex] = round(objZone.aDAMNodalPrice_TS_YS[indexTS,indexYear], 4)
                endRealTimeMarketPrice_YS_TS[iYearStep, objTimeSlice.iTSIndex] = round(objZone.aNodalPrice_TS_YS[indexTS,indexYear], 4)

    return endDayAheadMarketPrice_YS_TS, endRealTimeMarketPrice_YS_TS



def getGeneratorResult(instance, objMarket):

    setGenerator = [ objGenerator.sGeneratorID for objGenerator in objMarket.listGenerator ]

    vGeneratorProfit_YS_GR = {}
    vGeneratorCapacity_YS_PR_GR = {}

    # initiation
    for sGeneratorID in setGenerator:
        for iYearStep in instance.iFSYearSteps_YS:
            vGeneratorProfit_YS_GR[iYearStep, sGeneratorID] = 0
            for objGenTech in objMarket.listRegionGenTech:
                vGeneratorCapacity_YS_PR_GR[iYearStep, objGenTech.sProcessName, sGeneratorID] = 0

    if objMarket.sModel == "AgentBasedPoolMarket" or objMarket.sModel == "AgentBasedPowerExchange":

        for indexYR, iYearStep in enumerate(instance.iFSYearSteps_YS):
            indexYear = instance.iFSBaseYearIndex + indexYR
            for indexGR, objGenerator in enumerate(objMarket.listGenerator):
                # generator profit
                vGeneratorProfit_YS_GR[iYearStep, objGenerator.sGeneratorID] = round(objMarket.listGenerator[indexGR].fAnnualProfit_YS[indexYear], 4)

                # capacity
                for iSubregionIndex in objMarket.listSubregionIndex:
                    objZone = instance.listSubregionObjs[iSubregionIndex]                
                    
                    lsAllProcess = list(copy.copy(objZone.listGenPlant))
                    lsAllProcess.extend(copy.copy(objZone.listGenPlantFuture))

                    for objProcess in lsAllProcess:
                        if iYearStep >= objProcess.CommitTime and iYearStep < objProcess.DeCommitTime:
                            if objProcess.sGeneratorID == objGenerator.sGeneratorID:
                                vGeneratorCapacity_YS_PR_GR[iYearStep,objProcess.sProcessName,objGenerator.sGeneratorID] += objProcess.fCapacity

    return vGeneratorProfit_YS_GR, vGeneratorCapacity_YS_PR_GR 
'''



def getMarketProcessLCOE_YS_PR(dicPowerGen_YS_TS_PR, dicYearInvest_YS_PR, targetDictionary, setYS, IndexTS, setProcess):

    for iYearStep in setYS:
        for sProcess in setProcess:
            if (iYearStep, sProcess) not in targetDictionary:
                targetDictionary[iYearStep, sProcess] = 0 
            if (iYearStep, sProcess) in dicYearInvest_YS_PR: # if the subregion doesn't include the technology, then skip
                fYearGeneration = sum(dicPowerGen_YS_TS_PR[iYearStep, sTimeSlice, sProcess] for sTimeSlice in IndexTS)
                if fYearGeneration > 0: # M.USD / MWh * 1000 = USD/kWh
                    targetDictionary[iYearStep, sProcess] = round(  dicYearInvest_YS_PR[iYearStep, sProcess] / fYearGeneration * 1000, 4)

    return


def getMarketPowerGenCost_YS_TS(dicPowerGen_YS_TS_PR, dicProcessLCOE_YS_PR, targetDictionary, setYS, IndexTS, setProcess):

    for iYearStep in setYS:
        for sIndexTS in IndexTS :

            fWeightedCost = 0
            fTotalGeneration_YS_TS = sum(dicPowerGen_YS_TS_PR[iYearStep, sIndexTS, sProcess] for sProcess in setProcess)

            if fTotalGeneration_YS_TS > 0:
                for sProcess in setProcess:
                    fWeightedCost += dicProcessLCOE_YS_PR[iYearStep, sProcess] * dicPowerGen_YS_TS_PR[iYearStep, sIndexTS, sProcess] / fTotalGeneration_YS_TS
                
            targetDictionary[iYearStep, sIndexTS] = round( fWeightedCost, 4)

    return


def getRegionWholeSalePrice_YS_TS(dicPowerGenCost_YS_TS, pWholeSalePriceMarkUp_YS, targetDictionary, setYS, IndexTS):

    for iYearStep in setYS:
        for sIndexTS in IndexTS :
            targetDictionary[iYearStep, sIndexTS] = round( dicPowerGenCost_YS_TS[iYearStep, sIndexTS] * (1 + pWholeSalePriceMarkUp_YS[iYearStep] / 100), 4)

    return



