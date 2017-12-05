# -*- coding: utf-8 -*-

import copy
import numpy as np

import model_util_gen

def unitCommitment(instance, objMarket, indexYS):
    ''' daily basis unit commitment for thermal unit '''

    objMarketDup = copy.deepcopy(objMarket)

    # sum up the market residual demand
    fMarketTotalResDemand_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
    for objZone in objMarketDup.lsZone:
        fMarketTotalResDemand_TS_YS += objZone.fPowerResDemand_TS_YS
        
    for indexDay, objDay in enumerate(instance.lsDayTimeSlice):
    
        # get the time-slice with highest residual demand
        fDailyHighestDemand = 0
        iHighestTSIndex = 0
        for indexTS, objDayTS in enumerate(objDay.lsDiurnalTS):
            fMarketDemand = fMarketTotalResDemand_TS_YS[objDayTS.iTimeSliceIndex, indexYS]
            if fMarketDemand > fDailyHighestDemand:
                fDailyHighestDemand = fMarketDemand
                iHighestTSIndex = objDayTS.iTimeSliceIndex
        
        # add required ancillary service capacity to residual demand 
        for objZone in objMarketDup.lsZone:
            objZone.fPowerResDemand_TS_YS[iHighestTSIndex,indexYS] += objZone.fASRqrRegulation_TS_YS[iHighestTSIndex,indexYS]
            objZone.fPowerResDemand_TS_YS[iHighestTSIndex,indexYS] += objZone.fASRqr10MinReserve_TS_YS[iHighestTSIndex,indexYS]
            objZone.fPowerResDemand_TS_YS[iHighestTSIndex,indexYS] += objZone.fASRqr30MinReserve_TS_YS[iHighestTSIndex,indexYS]
        
        # sort variable generation cost
        objMarketDup.lsDispatchProcessIndex = sorted(objMarketDup.lsDispatchProcessIndex, key=lambda lsDispatchProcessIndex: \
                                                  lsDispatchProcessIndex.fVariableGenCost_TS[iHighestTSIndex])
        
        # dispatch the time-slice with hightst residual demand (this step make sure a lower bound of reliability requirement)
        for objProcessIndex in objMarketDup.lsDispatchProcessIndex:
            objDispatchZone = objMarketDup.lsZone[objProcessIndex.indexZone]
            objDispatchProcess = objDispatchZone.lsProcess[objProcessIndex.indexProcess]
            model_util_gen.dispatch_thermalUnit_TS(instance, objMarketDup, objDispatchZone, objDispatchProcess, iHighestTSIndex, indexYS)
    
        # allocate ancillary service among commited units (spinning reserve - limited ramp range)
        for objZone in objMarketDup.lsZone:
            lsProcessDup = copy.deepcopy(objZone.lsProcess)
            # sort the zone process by ramp up ability
            lsProcessDup = sorted(lsProcessDup, key=lambda lsProcessDup: lsProcessDup.RampRatePerM, reverse=True)
            
            # allocate regulation capacity of the zone, and calculate deficit
            allocateRegulationCapacity_spin(instance, objMarketDup, objZone, lsProcessDup, iHighestTSIndex, indexYS)
            # allocate 10 min operational reserve capacity of the zone, and calculate deficit
            allocate10MinReserve_spin(instance, objMarketDup, objZone, lsProcessDup, iHighestTSIndex, indexYS)
            # allocate 30 min operational reserve capacity of the zone, and calculate deficit
            allocate30MinReserve_spin(instance, objMarketDup, objZone, lsProcessDup, iHighestTSIndex, indexYS)
            
        # commit more units if there is unserved ancillary service (non-spinning reserve)
        for objZone in objMarketDup.lsZone:
            
            lsProcessDup = copy.deepcopy(objZone.lsProcess)
            # sort the zone process by ramp up ability
            lsProcessDup = sorted(lsProcessDup, key=lambda lsProcessDup: lsProcessDup.RampRatePerM, reverse=True)   
            
            # allocate regulation capacity of the zone
            if objZone.fASDfcRegulation_TS_YS[iHighestTSIndex, indexYS] > 0.001:
                allocateRegulationCapacity_nonspin(instance, objMarketDup, objZone, lsProcessDup, iHighestTSIndex, indexYS)
            # allocate 10 min operational reserve capacity of the zone, non-spinning reserve
            if objZone.fASDfc10MinReserve_TS_YS[iHighestTSIndex, indexYS] > 0.001:
                allocate10MinReserve_nonspin(instance, objMarketDup, objZone, lsProcessDup, iHighestTSIndex, indexYS)
            # allocate 30 min operational reserve capacity of the zone, non-spinning reserve
            if objZone.fASDfc30MinReserve_TS_YS[iHighestTSIndex, indexYS] > 0.001:
                allocate30MinReserve_nonspin(instance, objMarketDup, objZone, lsProcessDup, iHighestTSIndex, indexYS)

            # update process operation mode to original process list
            for objProcessDup in lsProcessDup:
                for objProcess in objZone.lsProcess:
                    if objProcessDup.sProcessID == objProcess.sProcessID:
                        objProcess.iOperatoinStatus_TS_YS[iHighestTSIndex, indexYS] = objProcessDup.iOperatoinStatus_TS_YS[iHighestTSIndex, indexYS]
                        break

        # if cannot be served by local process, commit neighbour's process
        

        # assign commit setting in the origional market object
        for indexZone, objZone in enumerate(objMarketDup.lsZone):
            for indexProcess, objProcess in enumerate(objZone.lsProcess):
                iOperatoinStatus = objProcess.iOperatoinStatus_TS_YS[iHighestTSIndex, indexYS]
                
                objProcessOrigin = objMarket.lsZone[indexZone].lsProcess[indexProcess]
                for indexTS, objDayTS in enumerate(objDay.lsDiurnalTS):
                    objProcessOrigin.iOperatoinStatus_TS_YS[objDayTS.iTimeSliceIndex, indexYS] = iOperatoinStatus
                    
    return


# ----------------------------------------------------------------------------
# -------------------- regulation --------------------------------------------
# ----------------------------------------------------------------------------

def allocateRegulationCapacity_spin(instance, objMarket, objZone, lsProcessDup, indexTS, indexYS):
    ''' allocate regulation capacity of the zone, and calculate deficit '''
    
    objZone.fASDfcRegulation_TS_YS[indexTS, indexYS] = objZone.fASRqrRegulation_TS_YS[indexTS, indexYS]
    sYearStep = instance.iAllYearSteps_YS[indexYS]
    
    # storage and limited dispatchable
    for objProcess in lsProcessDup:
        if objProcess.CommitTime <= sYearStep and objProcess.DeCommitTime > sYearStep:
        
            if objZone.fASDfcRegulation_TS_YS[indexTS, indexYS] > 0.001:
                if objProcess.sOperationMode in ["LimitDispatch","Storage"]:
                    # check if previous allocated
                    if (objProcess.fASRegulation_TS_YS[indexTS, indexYS] + objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS] \
                        + objProcess.fAS30MinReserve_TS_YS[indexTS, indexYS]) == 0:
                        # assume the regulation requirement is for 30 seconds
                        fTotalRampUp = objProcess.Capacity * (objProcess.RampRatePerM/100) / 2
                        fTotalRampUp = min(objProcess.Capacity/20, fTotalRampUp) # assumpe max operative reserve is 20% capacity
                        objProcess.fASRegulation_TS_YS[indexTS, indexYS] = fTotalRampUp
                        objZone.fASDfcRegulation_TS_YS[indexTS, indexYS] -= objProcess.fASRegulation_TS_YS[indexTS, indexYS]
    
            else:
                break
        
    # dispatchable process
    for objProcess in lsProcessDup:
        if objProcess.CommitTime <= sYearStep and objProcess.DeCommitTime > sYearStep:
        
            if objZone.fASDfcRegulation_TS_YS[indexTS, indexYS] > 0.001:
                if objProcess.sOperationMode in ["Dispatch"] and \
                objProcess.iOperatoinStatus_TS_YS[indexTS, indexYS] == 2 : # the process has to be commited
                    if "NUK" not in objProcess.sProcessName and "CHP" not in objProcess.sProcessName:
                        # check if previous allocated
                        if (objProcess.fASRegulation_TS_YS[indexTS, indexYS] + objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS] \
                                + objProcess.fAS30MinReserve_TS_YS[indexTS, indexYS]) == 0:
                                # assume the regulation requirement is for 30 seconds
                                objProcess.fASRegulation_TS_YS[indexTS, indexYS] = objProcess.Capacity * (objProcess.RampRatePerM/100) / 2
                                objZone.fASDfcRegulation_TS_YS[indexTS, indexYS] -= objProcess.fASRegulation_TS_YS[indexTS, indexYS]
            else:
                break

    return


def allocateRegulationCapacity_nonspin(instance, objMarket, objZone, lsProcessDup, indexTS, indexYS):
    ''' allocate regulation capacity of the zone, and calculate deficit '''

    sYearStep = instance.iAllYearSteps_YS[indexYS]

    # dispatchable process for non-spinning reserve
    for objProcess in lsProcessDup:
        if objProcess.CommitTime <= sYearStep and objProcess.DeCommitTime > sYearStep:
            
            if objZone.fASDfcRegulation_TS_YS[indexTS, indexYS] > 0.001:
                if objProcess.sOperationMode in ["Dispatch"] and \
                objProcess.iOperatoinStatus_TS_YS[indexTS, indexYS] == 0 : # the process has NOT be commited
                    if "NUK" not in objProcess.sProcessName and "CHP" not in objProcess.sProcessName:
                        # check if previous allocated
                        if (objProcess.fASRegulation_TS_YS[indexTS, indexYS] + objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS] \
                            + objProcess.fAS30MinReserve_TS_YS[indexTS, indexYS]) == 0:
                            # assume the regulation requirement is for 30 seconds
                            objProcess.fASRegulation_TS_YS[indexTS, indexYS] = objProcess.Capacity * (objProcess.RampRatePerM/100) / 2
                            objZone.fASDfcRegulation_TS_YS[indexTS, indexYS] -= objProcess.fASRegulation_TS_YS[indexTS, indexYS]
                            objProcess.iOperatoinStatus_TS_YS[indexTS, indexYS] = 2
            else:
                break

    return


# ----------------------------------------------------------------------------
# -------------------- 10 minutes reserve ------------------------------------
# ----------------------------------------------------------------------------

def allocate10MinReserve_spin(instance, objMarket, objZone, lsProcessDup, indexTS, indexYS):
    ''' allocate 10 min operational reserve capacity of the zone, and calculate deficit '''
    
    objZone.fASDfc10MinReserve_TS_YS[indexTS, indexYS] = objZone.fASRqr10MinReserve_TS_YS[indexTS, indexYS]
    sYearStep = instance.iAllYearSteps_YS[indexYS]
        
    # storage and limited dispatchable
    for objProcess in lsProcessDup:
        if objProcess.CommitTime <= sYearStep and objProcess.DeCommitTime > sYearStep:
        
            if objZone.fASDfc10MinReserve_TS_YS[indexTS, indexYS] > 0.001:
                if objProcess.sOperationMode in ["LimitDispatch","Storage"]:
                    # check if previous allocated
                    if (objProcess.fASRegulation_TS_YS[indexTS, indexYS] + objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS] \
                        + objProcess.fAS30MinReserve_TS_YS[indexTS, indexYS]) == 0:
                        fTotalRampUp = objProcess.Capacity * (objProcess.RampRatePerM/100) * 10
                        fTotalRampUp = min(objProcess.Capacity/20, fTotalRampUp) # assumpe max operative reserve is 20% capacity
                        objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS] = fTotalRampUp
                        objZone.fASDfc10MinReserve_TS_YS[indexTS, indexYS] -= objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS]
            else:
                break
        
    # dispatchable process
    for objProcess in lsProcessDup:
        if objProcess.CommitTime <= sYearStep and objProcess.DeCommitTime > sYearStep:
        
            if objZone.fASDfc10MinReserve_TS_YS[indexTS, indexYS] > 0.001:
                if objProcess.sOperationMode in ["Dispatch"] and \
                objProcess.iOperatoinStatus_TS_YS[indexTS, indexYS] == 2 : # the process has to be commited
                    if "NUK" not in objProcess.sProcessName and "CHP" not in objProcess.sProcessName:
                        # check if previous allocated
                        if (objProcess.fASRegulation_TS_YS[indexTS, indexYS] + objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS] \
                                + objProcess.fAS30MinReserve_TS_YS[indexTS, indexYS]) == 0:
                            fTotalRampUp = objProcess.Capacity * (objProcess.RampRatePerM/100) * 10
                            fTotalRampUp = min(objProcess.Capacity/10, fTotalRampUp) # assumpe max operative reserve is 10% capacity
                            objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS] = fTotalRampUp
                            objZone.fASDfc10MinReserve_TS_YS[indexTS, indexYS] -= objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS]
            else:
                break

    return


def allocate10MinReserve_nonspin(instance, objMarket, objZone, lsProcessDup, indexTS, indexYS):
    ''' allocate 10 min operational reserve capacity of the zone, and calculate deficit '''
            
    sYearStep = instance.iAllYearSteps_YS[indexYS]
    
    # dispatchable process
    for objProcess in lsProcessDup:
        if objProcess.CommitTime <= sYearStep and objProcess.DeCommitTime > sYearStep:
        
            if objZone.fASDfc10MinReserve_TS_YS[indexTS, indexYS] > 0.001:
                if objProcess.sOperationMode in ["Dispatch"] and \
                objProcess.iOperatoinStatus_TS_YS[indexTS, indexYS] == 0 : # the process has to be commited
                    if "NUK" not in objProcess.sProcessName and "CHP" not in objProcess.sProcessName:
                        # check if previous allocated
                        if (objProcess.fASRegulation_TS_YS[indexTS, indexYS] + objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS] \
                            + objProcess.fAS30MinReserve_TS_YS[indexTS, indexYS]) == 0:
                            # check if previous allocated
                            fTotalRampUp = objProcess.Capacity * (objProcess.RampRatePerM/100) * 10
                            fTotalRampUp = min(objProcess.Capacity, fTotalRampUp) # assumpe max operative reserve is 10% capacity
                            objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS] = fTotalRampUp
                            objZone.fASDfc10MinReserve_TS_YS[indexTS, indexYS] -= objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS]
                            objProcess.iOperatoinStatus_TS_YS[indexTS, indexYS] = 2
            else:
                break

    return


# ----------------------------------------------------------------------------
# -------------------- 30 minutes reserve ------------------------------------
# ----------------------------------------------------------------------------

def allocate30MinReserve_spin(instance, objMarket, objZone, lsProcessDup, indexTS, indexYS):
    ''' allocate 30 min operational reserve capacity of the zone, and calculate deficit '''
    
    objZone.fASDfc30MinReserve_TS_YS[indexTS, indexYS] = objZone.fASRqr30MinReserve_TS_YS[indexTS, indexYS]
    sYearStep = instance.iAllYearSteps_YS[indexYS]

    # dispatchable process
    for objProcess in lsProcessDup:
        if objProcess.CommitTime <= sYearStep and objProcess.DeCommitTime > sYearStep:
            
            if objZone.fASDfc30MinReserve_TS_YS[indexTS, indexYS] > 0.001:
                if objProcess.sOperationMode in ["Dispatch"] and \
                objProcess.iOperatoinStatus_TS_YS[indexTS, indexYS] == 2 : # the process has to be commited
                    if "CHP" not in objProcess.sProcessName:
                        # check if previous allocated
                        if (objProcess.fASRegulation_TS_YS[indexTS, indexYS] + objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS] \
                                + objProcess.fAS30MinReserve_TS_YS[indexTS, indexYS]) == 0:
                            fTotalRampUp = objProcess.Capacity * (objProcess.RampRatePerM/100) * 30
                            fTotalRampUp = min(objProcess.Capacity/10, fTotalRampUp) # assumpe max operative reserve is 10% capacity
                            objProcess.fAS30MinReserve_TS_YS[indexTS, indexYS] = fTotalRampUp
                            objZone.fASDfc30MinReserve_TS_YS[indexTS, indexYS] -= objProcess.fAS30MinReserve_TS_YS[indexTS, indexYS]
            else:
                break

    return


def allocate30MinReserve_nonspin(instance, objMarket, objZone, lsProcessDup, indexTS, indexYS):
    ''' allocate 30 min operational reserve capacity of the zone, and calculate deficit '''
    
    sYearStep = instance.iAllYearSteps_YS[indexYS]
    
    # dispatchable process
    for objProcess in lsProcessDup:
        if objProcess.CommitTime <= sYearStep and objProcess.DeCommitTime > sYearStep:
            
            if objZone.fASDfc30MinReserve_TS_YS[indexTS, indexYS] > 0.001:
                if objProcess.sOperationMode in ["Dispatch"] and \
                objProcess.iOperatoinStatus_TS_YS[indexTS, indexYS] == 0 : # the process has to be commited
                    if "CHP" not in objProcess.sProcessName:
                        # check if previous allocated
                        if (objProcess.fASRegulation_TS_YS[indexTS, indexYS] + objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS] \
                            + objProcess.fAS30MinReserve_TS_YS[indexTS, indexYS]) == 0:
                            fTotalRampUp = objProcess.Capacity * (objProcess.RampRatePerM/100) * 30
                            fTotalRampUp = min(objProcess.Capacity, fTotalRampUp) # assumpe max operative reserve is 10% capacity
                            objProcess.fAS30MinReserve_TS_YS[indexTS, indexYS] = fTotalRampUp
                            objZone.fASDfc30MinReserve_TS_YS[indexTS, indexYS] -= objProcess.fAS30MinReserve_TS_YS[indexTS, indexYS]
                            objProcess.iOperatoinStatus_TS_YS[indexTS, indexYS] = 2
            else:
                break

    return




