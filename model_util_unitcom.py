# -*- coding: utf-8 -*-

import copy
import numpy as np

import cls_misc
import model_util_gen

def unitCommitment(instance, objMarket, indexYS, sMode):
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
        for objDayTS in objDay.lsDiurnalTS:
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
        
        # dispatch the time-slice with highest residual demand (this step make sure a lower bound of reliability requirement)
        for objProcessIndex in objMarketDup.lsDispatchProcessIndex:
            objDispatchZone = objMarketDup.lsZone[objProcessIndex.indexZone]
            
            if sMode == "ExecMode":
                lsProcess = objDispatchZone.lsProcess
            elif sMode == "PlanMode":  
                lsProcess = objDispatchZone.lsProcessOperTemp
                
            objDispatchProcess = lsProcess[objProcessIndex.indexProcess]
            model_util_gen.dispatch_thermalUnit_TS(instance, objMarketDup, objDispatchZone, objDispatchProcess, iHighestTSIndex, indexYS)

        # restructure lsDispatchProcessIndex (to include all ramp up facilities)
        objMarketDup.lsDispatchProcessIndex = list()
        for indexZone, objZone in enumerate(objMarketDup.lsZone):
        
            if sMode == "ExecMode":
                lsProcess = objZone.lsProcess
            elif sMode == "PlanMode":
                lsProcess = objZone.lsProcessOperTemp
                
            sYearStep = instance.iAllYearSteps_YS[indexYS]
            for indexProcess, objProcess in enumerate(lsProcess):
                if objProcess.CommitTime <= sYearStep and objProcess.DeCommitTime > sYearStep:
                    objMarketDup.lsDispatchProcessIndex.append(cls_misc.MarketDispatchProcess(  \
                        indexZone=indexZone, indexProcess=indexProcess, sProcessName=objProcess.sProcessName, \
                        RampRatePerM=objProcess.RampRatePerM, fVariableGenCost_TS=objProcess.fVariableGenCost_TS_YS[:,indexYS] ))

        # sort system ramp up ability
        objMarketDup.lsDispatchProcessIndex = sorted(objMarketDup.lsDispatchProcessIndex, key=lambda lsDispatchProcessIndex: \
                                                  lsDispatchProcessIndex.RampRatePerM, reverse=True) 
        
        # allocate ancillary service among commited units (spinning reserve - limited ramp range)
        for objZone in objMarketDup.lsZone:
            
            if sMode == "ExecMode":
                lsProcess = objZone.lsProcess
            elif sMode == "PlanMode":  
                lsProcess = objZone.lsProcessOperTemp
            
            # allocate regulation capacity of the zone, and calculate deficit
            allocateRegulationCapacity_spin(instance, objMarketDup, objZone, lsProcess, iHighestTSIndex, indexYS)
            # allocate 10 min operational reserve capacity of the zone, and calculate deficit
            allocate10MinReserve_spin(instance, objMarketDup, objZone, lsProcess, iHighestTSIndex, indexYS)
            # allocate 30 min operational reserve capacity of the zone, and calculate deficit
            allocate30MinReserve_spin(instance, objMarketDup, objZone, lsProcess, iHighestTSIndex, indexYS)
            
        # commit more units if there is unserved ancillary service (non-spinning reserve)
        for objZone in objMarketDup.lsZone:
            
            if sMode == "ExecMode":
                lsProcess = objZone.lsProcess
            elif sMode == "PlanMode":  
                lsProcess = objZone.lsProcessOperTemp

            # allocate regulation capacity of the zone
            if objZone.fASDfcRegulation_TS_YS[iHighestTSIndex, indexYS] > 0.001:
                allocateRegulationCapacity_nonspin(instance, objMarketDup, objZone, lsProcess, iHighestTSIndex, indexYS)
            # allocate 10 min operational reserve capacity of the zone, non-spinning reserve
            if objZone.fASDfc10MinReserve_TS_YS[iHighestTSIndex, indexYS] > 0.001:
                allocate10MinReserve_nonspin(instance, objMarketDup, objZone, lsProcess, iHighestTSIndex, indexYS)
            # allocate 30 min operational reserve capacity of the zone, non-spinning reserve
            if objZone.fASDfc30MinReserve_TS_YS[iHighestTSIndex, indexYS] > 0.001:
                allocate30MinReserve_nonspin(instance, objMarketDup, objZone, lsProcess, iHighestTSIndex, indexYS)

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

def allocateRegulationCapacity_spin(instance, objMarket, objZone, lsProcess, indexTS, indexYS):
    ''' allocate regulation capacity of the zone, and calculate deficit '''
    
    objZone.fASDfcRegulation_TS_YS[indexTS, indexYS] = objZone.fASRqrRegulation_TS_YS[indexTS, indexYS]

    lsProcessIndex = objMarket.lsDispatchProcessIndex
    
    # storage and limited dispatchable
    for objProcessIndex in lsProcessIndex:
        if objZone.sZone ==  objMarket.lsZone[objProcessIndex.indexZone].sZone:
            objProcess = lsProcess[objProcessIndex.indexProcess]
        
            if objZone.fASDfcRegulation_TS_YS[indexTS, indexYS] > 0.001:
                if objProcess.sOperationMode in ["LimitDispatch","Storage"]:
                    # check if previous allocated
                    if (objProcess.fASRegulation_TS_YS[indexTS, indexYS] + objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS] \
                        + objProcess.fAS30MinReserve_TS_YS[indexTS, indexYS]) == 0:
                        # assume the regulation requirement is for 30 seconds
                        fTotalRampUp = objProcess.Capacity * (objProcess.RampRatePerM/100) / 2
                        fTotalRampUp = min(objProcess.Capacity/5, fTotalRampUp) # assumpe max operative reserve is 20% capacity
                        objProcess.fASRegulation_TS_YS[indexTS, indexYS] = fTotalRampUp
                        objZone.fASDfcRegulation_TS_YS[indexTS, indexYS] -= objProcess.fASRegulation_TS_YS[indexTS, indexYS]
    
            else:
                break
        
    # dispatchable process
    for objProcessIndex in lsProcessIndex:
        if objZone.sZone ==  objMarket.lsZone[objProcessIndex.indexZone].sZone:
            objProcess = lsProcess[objProcessIndex.indexProcess]
    
            if objZone.fASDfcRegulation_TS_YS[indexTS, indexYS] > 0.001:
                if objProcess.sOperationMode in ["Dispatch"] and \
                objProcess.iOperatoinStatus_TS_YS[indexTS, indexYS] != 0 : # the process has to be commited
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


def allocateRegulationCapacity_nonspin(instance, objMarket, objZone, lsProcess, indexTS, indexYS):
    ''' allocate regulation capacity of the zone, and calculate deficit '''

    lsProcessIndex = objMarket.lsDispatchProcessIndex
    
    # dispatchable process for non-spinning reserve
    for objProcessIndex in lsProcessIndex:
        if objZone.sZone ==  objMarket.lsZone[objProcessIndex.indexZone].sZone:
            objProcess = lsProcess[objProcessIndex.indexProcess]
            
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

def allocate10MinReserve_spin(instance, objMarket, objZone, lsProcess, indexTS, indexYS):
    ''' allocate 10 min operational reserve capacity of the zone, and calculate deficit '''
    
    objZone.fASDfc10MinReserve_TS_YS[indexTS, indexYS] = objZone.fASRqr10MinReserve_TS_YS[indexTS, indexYS]

    lsProcessIndex = objMarket.lsDispatchProcessIndex
    
    # storage and limited dispatchable
    for objProcessIndex in lsProcessIndex:
        if objZone.sZone ==  objMarket.lsZone[objProcessIndex.indexZone].sZone:
            objProcess = lsProcess[objProcessIndex.indexProcess]

            if objZone.fASDfc10MinReserve_TS_YS[indexTS, indexYS] > 0.001:
                if objProcess.sOperationMode in ["LimitDispatch","Storage"]:
                    # check if previous allocated
                    if (objProcess.fASRegulation_TS_YS[indexTS, indexYS] + objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS] \
                        + objProcess.fAS30MinReserve_TS_YS[indexTS, indexYS]) == 0:
                        fTotalRampUp = objProcess.Capacity * (objProcess.RampRatePerM/100) * 10
                        fTotalRampUp = min(objProcess.Capacity/5, fTotalRampUp) # assumpe max operative reserve is 20% capacity
                        objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS] = fTotalRampUp
                        objZone.fASDfc10MinReserve_TS_YS[indexTS, indexYS] -= objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS]
            else:
                break
        
    # dispatchable process
    for objProcessIndex in lsProcessIndex:
        if objZone.sZone ==  objMarket.lsZone[objProcessIndex.indexZone].sZone:
            objProcess = lsProcess[objProcessIndex.indexProcess]

            if objZone.fASDfc10MinReserve_TS_YS[indexTS, indexYS] > 0.001:
                if objProcess.sOperationMode in ["Dispatch"] and \
                objProcess.iOperatoinStatus_TS_YS[indexTS, indexYS] != 0 : # the process has to be commited
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


def allocate10MinReserve_nonspin(instance, objMarket, objZone, lsProcess, indexTS, indexYS):
    ''' allocate 10 min operational reserve capacity of the zone, and calculate deficit '''
            
    lsProcessIndex = objMarket.lsDispatchProcessIndex
    
    # dispatchable process
    for objProcessIndex in lsProcessIndex:
        if objZone.sZone ==  objMarket.lsZone[objProcessIndex.indexZone].sZone:
            objProcess = lsProcess[objProcessIndex.indexProcess]

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

def allocate30MinReserve_spin(instance, objMarket, objZone, lsProcess, indexTS, indexYS):
    ''' allocate 30 min operational reserve capacity of the zone, and calculate deficit '''
    
    objZone.fASDfc30MinReserve_TS_YS[indexTS, indexYS] = objZone.fASRqr30MinReserve_TS_YS[indexTS, indexYS]

    lsProcessIndex = objMarket.lsDispatchProcessIndex
    
    # dispatchable process
    for objProcessIndex in lsProcessIndex:
        if objZone.sZone ==  objMarket.lsZone[objProcessIndex.indexZone].sZone:
            objProcess = lsProcess[objProcessIndex.indexProcess]

            if objZone.fASDfc30MinReserve_TS_YS[indexTS, indexYS] > 0.001:
                if objProcess.sOperationMode in ["Dispatch"] and \
                objProcess.iOperatoinStatus_TS_YS[indexTS, indexYS] != 0 : # the process has to be commited
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


def allocate30MinReserve_nonspin(instance, objMarket, objZone, lsProcess, indexTS, indexYS):
    ''' allocate 30 min operational reserve capacity of the zone, and calculate deficit '''

    lsProcessIndex = objMarket.lsDispatchProcessIndex
    
    # dispatchable process
    for objProcessIndex in lsProcessIndex:
        if objZone.sZone ==  objMarket.lsZone[objProcessIndex.indexZone].sZone:
            objProcess = lsProcess[objProcessIndex.indexProcess]
            
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

