# -*- coding: utf-8 -*-

import copy
import numpy as np

import cls_misc
import model_util_gen

EquASMultiplier = [0.5, 10, 30]     # the equivilant capacity per minute multiplier of each type of ancillary service

def unitCommitment(instance, objMarket, indexYS, sMode):
    ''' daily basis unit commitment for thermal unit '''

    objMarketDup = copy.deepcopy(objMarket)

    # sum up the market residual demand
    fMarketTotalResDemand_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
    for objZone in objMarketDup.lsZone:
        fMarketTotalResDemand_TS_YS += objZone.fPowerResDemand_TS_YS
        
    for indexDay, objDay in enumerate(instance.lsDayTimeSlice):
    
        # get the time-slice with highest residual demand in the system in the day
        fDailyHighestDemand = 0
        iHighestTSIndex = 0
        for objDayTS in objDay.lsDiurnalTS:
            fMarketDemand = fMarketTotalResDemand_TS_YS[objDayTS.iTimeSliceIndex, indexYS]
            if fMarketDemand > fDailyHighestDemand:
                fDailyHighestDemand = fMarketDemand
                iHighestTSIndex = objDayTS.iTimeSliceIndex
        
        # sort variable generation cost
        objMarketDup.lsDispatchProcessIndex = sorted(objMarketDup.lsDispatchProcessIndex, key=lambda lsDispatchProcessIndex: \
                                                  lsDispatchProcessIndex.fVariableGenCost_TS[iHighestTSIndex])        
        
        # dispatch the time-slice with highest residual demand (this step make sure a lower bound of reliability requirement)
        for objProcessIndex in objMarketDup.lsDispatchProcessIndex:
            objDispatchZone = objMarketDup.lsZone[objProcessIndex.indexZone]
            
            if sMode == "ExecMode":
                lsProcess = objDispatchZone.lsProcess
            elif sMode == "PlanMode":  
                lsProcess = objDispatchZone.lsProcessOperTemp
                
            objDispatchProcess = lsProcess[objProcessIndex.indexProcess]
            # the ancillary service hasn't allocated
            model_util_gen.dispatch_thermalUnit_TS(instance, objMarketDup, objDispatchZone, objDispatchProcess, iHighestTSIndex, indexYS)

        # list of all ramp up facilities
        objMarketDup.lsAncSerProcessIndex = list()
        for indexZone, objZone in enumerate(objMarketDup.lsZone):
        
            if sMode == "ExecMode":
                lsProcess = objZone.lsProcess
            elif sMode == "PlanMode":
                lsProcess = objZone.lsProcessOperTemp
                
            sYearStep = instance.iAllYearSteps_YS[indexYS]
            for indexProcess, objProcess in enumerate(lsProcess):
                if objProcess.CommitTime <= sYearStep and objProcess.DeCommitTime > sYearStep:
                    objMarketDup.lsAncSerProcessIndex.append(cls_misc.MarketDispatchProcess(  \
                        indexZone=indexZone, indexProcess=indexProcess, sProcessName=objProcess.sProcessName, \
                        RampRatePerM=objProcess.RampRatePerM, fVariableGenCost_TS=objProcess.fVariableGenCost_TS_YS[:,indexYS] ))

        # sort system ramp up ability
        objMarketDup.lsAncSerProcessIndex = sorted(objMarketDup.lsAncSerProcessIndex, key=lambda lsAncSerProcessIndex: \
                                                  lsAncSerProcessIndex.RampRatePerM, reverse=True) 
        
        # allocate ancillary service among commited units (spinning reserve - limited ramp range)
        for objZone in objMarketDup.lsZone:
            
            if sMode == "ExecMode":
                lsProcess = objZone.lsProcess
            elif sMode == "PlanMode":  
                lsProcess = objZone.lsProcessOperTemp
            
            objZone.fASDfcRegulation_TS_YS[iHighestTSIndex, indexYS] = objZone.fASRqrRegulation_TS_YS[iHighestTSIndex, indexYS]
            objZone.fASDfc10MinReserve_TS_YS[iHighestTSIndex, indexYS] = objZone.fASRqr10MinReserve_TS_YS[iHighestTSIndex, indexYS]
            objZone.fASDfc30MinReserve_TS_YS[iHighestTSIndex, indexYS] = objZone.fASRqr30MinReserve_TS_YS[iHighestTSIndex, indexYS]
            
            for objProcessIndex in objMarketDup.lsAncSerProcessIndex:
                if objZone.sZone ==  objMarketDup.lsZone[objProcessIndex.indexZone].sZone:
                    objProcess = lsProcess[objProcessIndex.indexProcess]
                    if objProcess.iOperatoinStatus_TS_YS[iHighestTSIndex, indexYS] != 0: # the process has NOT be commited

                        for iUnit in range(int(objProcess.NoUnit)):
                            
                            if objZone.fASDfcRegulation_TS_YS[iHighestTSIndex, indexYS] > 0.001:
                                if objProcess.fHourlyPowerOutput_TS_YS[iHighestTSIndex,indexYS] > 0.001:
                                    allocateRegulationCapacity_spin(instance, objZone, objProcess, iHighestTSIndex, indexYS)
                                else:
                                    allocateRegulationCapacity_nonspin(instance, objZone, objProcess, iHighestTSIndex, indexYS)
                                    
                            elif objZone.fASDfc10MinReserve_TS_YS[iHighestTSIndex, indexYS] > 0.001:
                                if objProcess.fHourlyPowerOutput_TS_YS[iHighestTSIndex,indexYS] > 0.001:
                                    allocate10MinReserve_spin(instance, objZone, objProcess, iHighestTSIndex, indexYS)
                                else:
                                    allocate10MinReserve_nonspin(instance, objZone, objProcess, iHighestTSIndex, indexYS)
                                    
                            elif objZone.fASDfc30MinReserve_TS_YS[iHighestTSIndex, indexYS] > 0.001:
                                if objProcess.fHourlyPowerOutput_TS_YS[iHighestTSIndex,indexYS] > 0.001:
                                    allocate30MinReserve_spin(instance, objZone, objProcess, iHighestTSIndex, indexYS)
                                else:
                                    allocate30MinReserve_nonspin(instance, objZone, objProcess, iHighestTSIndex, indexYS)
            
        # commit more units if there is unserved ancillary service (non-spinning reserve)
        for objZone in objMarketDup.lsZone:
            
            if sMode == "ExecMode":
                lsProcess = objZone.lsProcess
            elif sMode == "PlanMode":  
                lsProcess = objZone.lsProcessOperTemp

            for objProcessIndex in objMarketDup.lsAncSerProcessIndex:
                if objZone.sZone ==  objMarketDup.lsZone[objProcessIndex.indexZone].sZone:
                    objProcess = lsProcess[objProcessIndex.indexProcess]
                    if objProcess.iOperatoinStatus_TS_YS[iHighestTSIndex, indexYS] == 0: # the process has NOT be commited previously
                        for iUnit in range(int(objProcess.NoUnit)):
                            if objZone.fASDfcRegulation_TS_YS[iHighestTSIndex, indexYS] > 0.001:
                                allocateRegulationCapacity_nonspin(instance, objZone, objProcess, iHighestTSIndex, indexYS)
                            elif objZone.fASDfc10MinReserve_TS_YS[iHighestTSIndex, indexYS] > 0.001:
                                allocate10MinReserve_nonspin(instance, objZone, objProcess, iHighestTSIndex, indexYS)
                            elif objZone.fASDfc30MinReserve_TS_YS[iHighestTSIndex, indexYS] > 0.001:
                                allocate30MinReserve_nonspin(instance, objZone, objProcess, iHighestTSIndex, indexYS)

        # if cannot be served by local process, commit neighbour's process
        
        # assign commit setting in the origional market object
        for indexZone, objZone in enumerate(objMarketDup.lsZone):
            
            if sMode == "ExecMode":
                for indexProcess, objProcess in enumerate(objZone.lsProcess):
                    iOperatoinStatus = objProcess.iOperatoinStatus_TS_YS[iHighestTSIndex, indexYS]
                    
                    objProcessOrigin = objMarket.lsZone[indexZone].lsProcess[indexProcess]
                    for objDayTS in objDay.lsDiurnalTS:
                        objProcessOrigin.iOperatoinStatus_TS_YS[objDayTS.iTimeSliceIndex, indexYS] = iOperatoinStatus
                
            elif sMode == "PlanMode":  
                for indexProcess, objProcess in enumerate(objZone.lsProcessOperTemp):
                    iOperatoinStatus = objProcess.iOperatoinStatus_TS_YS[iHighestTSIndex, indexYS]
                    
                    objProcessOrigin = objMarket.lsZone[indexZone].lsProcessOperTemp[indexProcess]
                    for objDayTS in objDay.lsDiurnalTS:
                        objProcessOrigin.iOperatoinStatus_TS_YS[objDayTS.iTimeSliceIndex, indexYS] = iOperatoinStatus

        for indexZone, objZone in enumerate(objMarket.lsZone):
            for objDayTS in objDay.lsDiurnalTS:
                objZone.fASDfcRegulation_TS_YS[objDayTS.iTimeSliceIndex, indexYS] = objMarketDup.lsZone[indexZone].fASDfcRegulation_TS_YS[iHighestTSIndex, indexYS]
                objZone.fASDfc10MinReserve_TS_YS[objDayTS.iTimeSliceIndex, indexYS] = objMarketDup.lsZone[indexZone].fASDfc10MinReserve_TS_YS[iHighestTSIndex, indexYS] 
                objZone.fASDfc30MinReserve_TS_YS[objDayTS.iTimeSliceIndex, indexYS] = objMarketDup.lsZone[indexZone].fASDfc30MinReserve_TS_YS[iHighestTSIndex, indexYS]

        # copy process ancillary service allocation for debuging
        for indexZone, objZone in enumerate(objMarketDup.lsZone):
            if sMode == "ExecMode":
                lsProcessDup = objZone.lsProcess
                lsProcessOri = objMarket.lsZone[indexZone].lsProcess
            elif sMode == "PlanMode":  
                lsProcessDup = objZone.lsProcessOperTemp
                lsProcessOri = objMarket.lsZone[indexZone].lsProcessOperTemp
                
            for indexProcess, objProcess in enumerate(lsProcessDup):
                iAS1 = objProcess.fASRegulation_TS_YS[iHighestTSIndex, indexYS]
                iAS2 = objProcess.fAS10MinReserve_TS_YS[iHighestTSIndex, indexYS]
                iAS3 = objProcess.fAS30MinReserve_TS_YS[iHighestTSIndex, indexYS]

                objProcessOrigin = lsProcessOri[indexProcess]
                for objDayTS in objDay.lsDiurnalTS:
                    objProcessOrigin.fASRegulation_TS_YS[objDayTS.iTimeSliceIndex, indexYS] = iAS1
                    objProcessOrigin.fAS10MinReserve_TS_YS[objDayTS.iTimeSliceIndex, indexYS] = iAS2
                    objProcessOrigin.fAS30MinReserve_TS_YS[objDayTS.iTimeSliceIndex, indexYS] = iAS3

    return



# ----------------------------------------------------------------------------
# -------------------- regulation --------------------------------------------
# ----------------------------------------------------------------------------

def allocateRegulationCapacity_spin(instance, objZone, objProcess, indexTS, indexYS):
    ''' allocate regulation capacity of the zone, and calculate deficit '''

    fCapacityUnit = objProcess.fDeratedCapacity / objProcess.NoUnit

    # storage and limited dispatchable
    if objProcess.sOperationMode in ["LimitDispatch","Storage"]:

        # assumpe max operative reserve is 20% capacity
        fMaxOperationRange = fCapacityUnit / 5        
        fMaxRampUp = fCapacityUnit * (objProcess.RampRatePerM/100) * EquASMultiplier[0]
        fMaxRampCapacity = min(fMaxOperationRange, fMaxRampUp)
            
        # allocate one unit to regulation
        objProcess.fASRegulation_TS_YS[indexTS, indexYS] += fMaxRampCapacity
        objZone.fASDfcRegulation_TS_YS[indexTS, indexYS] -= fMaxRampCapacity                 

    # dispatchable process
    elif objProcess.sOperationMode in ["Dispatch"]:
        if "NUK" not in objProcess.sProcessName:
            
            # assumpe max operative reserve is 10% capacity
            fMaxOperationRange = fCapacityUnit / 10        
            fMaxRampUp = fCapacityUnit * (objProcess.RampRatePerM/100) * EquASMultiplier[0]
            fMaxRampCapacity = min(fMaxOperationRange, fMaxRampUp)
                
            # allocate one unit to regulation
            objProcess.fASRegulation_TS_YS[indexTS, indexYS] += fMaxRampCapacity
            objZone.fASDfcRegulation_TS_YS[indexTS, indexYS] -= fMaxRampCapacity 

    return


def allocateRegulationCapacity_nonspin(instance, objZone, objProcess, indexTS, indexYS):
    ''' allocate regulation capacity of the zone, and calculate deficit '''

    fCapacityUnit = objProcess.fDeratedCapacity / objProcess.NoUnit
    
    # dispatchable process
    if objProcess.sOperationMode in ["Dispatch"]:
        if "NUK" not in objProcess.sProcessName:
            
            # assumpe max operative reserve is 100% capacity
            fMaxOperationRange = fCapacityUnit        
            fMaxRampUp = fCapacityUnit * (objProcess.RampRatePerM/100) * EquASMultiplier[0]
            fMaxRampCapacity = min(fMaxOperationRange, fMaxRampUp)
                
            # allocate one unit to regulation
            objProcess.fASRegulation_TS_YS[indexTS, indexYS] += fMaxRampCapacity
            objZone.fASDfcRegulation_TS_YS[indexTS, indexYS] -= fMaxRampCapacity 

            objProcess.iOperatoinStatus_TS_YS[indexTS, indexYS] = 2

    return


# ----------------------------------------------------------------------------
# -------------------- 10 minutes reserve ------------------------------------
# ----------------------------------------------------------------------------

def allocate10MinReserve_spin(instance, objZone, objProcess, indexTS, indexYS):
    ''' allocate 10 min operational reserve capacity of the zone, and calculate deficit '''
    
    fCapacityUnit = objProcess.fDeratedCapacity / objProcess.NoUnit

    # storage and limited dispatchable
    if objProcess.sOperationMode in ["LimitDispatch","Storage"]:

        # assumpe max operative reserve is 20% capacity
        fMaxOperationRange = fCapacityUnit / 5        
        fMaxRampUp = fCapacityUnit * (objProcess.RampRatePerM/100) * EquASMultiplier[1]
        fMaxRampCapacity = min(fMaxOperationRange, fMaxRampUp)
            
        # allocate one unit to regulation
        objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS] += fMaxRampCapacity
        objZone.fASDfc10MinReserve_TS_YS[indexTS, indexYS] -= fMaxRampCapacity                 

    # dispatchable process
    elif objProcess.sOperationMode in ["Dispatch"]:
        if "NUK" not in objProcess.sProcessName:
            
            # assumpe max operative reserve is 10% capacity
            fMaxOperationRange = fCapacityUnit / 10        
            fMaxRampUp = fCapacityUnit * (objProcess.RampRatePerM/100) * EquASMultiplier[1]
            fMaxRampCapacity = min(fMaxOperationRange, fMaxRampUp)
                
            # allocate one unit to regulation
            objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS] += fMaxRampCapacity
            objZone.fASDfc10MinReserve_TS_YS[indexTS, indexYS] -= fMaxRampCapacity 

    return


def allocate10MinReserve_nonspin(instance, objZone, objProcess, indexTS, indexYS):
    ''' allocate 10 min operational reserve capacity of the zone, and calculate deficit '''

    fCapacityUnit = objProcess.fDeratedCapacity / objProcess.NoUnit
    
    # dispatchable process
    if objProcess.sOperationMode in ["Dispatch"]:
        if "NUK" not in objProcess.sProcessName:
            
            # assumpe max operative reserve is 100% capacity
            fMaxOperationRange = fCapacityUnit    
            
            # assumpe max operative reserve for CHP is 10% capacity
            if "CHP" in objProcess.sProcessName:
                fMaxOperationRange = fCapacityUnit / 10            
            
            fMaxRampUp = fCapacityUnit * (objProcess.RampRatePerM/100) * EquASMultiplier[1]
            fMaxRampCapacity = min(fMaxOperationRange, fMaxRampUp)
                
            # allocate one unit to regulation
            objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS] += fMaxRampCapacity
            objZone.fASDfc10MinReserve_TS_YS[indexTS, indexYS] -= fMaxRampCapacity 

            objProcess.iOperatoinStatus_TS_YS[indexTS, indexYS] = 2
            
    return


# ----------------------------------------------------------------------------
# -------------------- 30 minutes reserve ------------------------------------
# ----------------------------------------------------------------------------

def allocate30MinReserve_spin(instance, objZone, objProcess, indexTS, indexYS):
    ''' allocate 30 min operational reserve capacity of the zone, and calculate deficit '''
    
    fCapacityUnit = objProcess.fDeratedCapacity / objProcess.NoUnit

    # dispatchable process
    if objProcess.sOperationMode in ["Dispatch"]:
                
        # assumpe max operative reserve is 10% capacity
        fMaxOperationRange = fCapacityUnit / 10        
        fMaxRampUp = fCapacityUnit * (objProcess.RampRatePerM/100) * EquASMultiplier[2]
        fMaxRampCapacity = min(fMaxOperationRange, fMaxRampUp)
            
        # allocate one unit to regulation
        objProcess.fAS30MinReserve_TS_YS[indexTS, indexYS] += fMaxRampCapacity
        objZone.fASDfc30MinReserve_TS_YS[indexTS, indexYS] -= fMaxRampCapacity 

    return


def allocate30MinReserve_nonspin(instance, objZone, objProcess, indexTS, indexYS):
    ''' allocate 30 min operational reserve capacity of the zone, and calculate deficit '''

    fCapacityUnit = objProcess.fDeratedCapacity / objProcess.NoUnit
    
    # dispatchable process
    if objProcess.sOperationMode in ["Dispatch"]:
        if "NUK" not in objProcess.sProcessName:
            
            # assumpe max operative reserve is 100% capacity
            fMaxOperationRange = fCapacityUnit
            
            # assumpe max operative reserve for CHP is 10% capacity
            if "CHP" in objProcess.sProcessName:
                fMaxOperationRange = fCapacityUnit / 10
                
            fMaxRampUp = fCapacityUnit * (objProcess.RampRatePerM/100) * EquASMultiplier[2]
            fMaxRampCapacity = min(fMaxOperationRange, fMaxRampUp)
                
            # allocate one unit to regulation
            objProcess.fAS30MinReserve_TS_YS[indexTS, indexYS] += fMaxRampCapacity
            objZone.fASDfc30MinReserve_TS_YS[indexTS, indexYS] -= fMaxRampCapacity 

            objProcess.iOperatoinStatus_TS_YS[indexTS, indexYS] = 2

    return

