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
    
        # arrange ancillary service among commited units
        for objZone in objMarketDup.lsZone:
            lsProcessDup = copy.deepcopy(objZone.lsProcess)
            # sort the zone process by ramp up ability
            lsProcessDup = sorted(lsProcessDup, key=lambda lsProcessDup: lsProcessDup.RampRatePerM, reverse=True)
            
            # arrange regulation capacity of the zone, and calculate deficit
            allocateRegulationCapacity_opr(objMarketDup, objZone, lsProcessDup, iHighestTSIndex, indexYS)
            # arrange 10 min operational reserve capacity of the zone, and calculate deficit
            allocate10MinReserve_opr(objMarketDup, objZone, lsProcessDup, iHighestTSIndex, indexYS)
            # arrange 30 min operational reserve capacity of the zone, and calculate deficit
            allocate30MinReserve_opr(objMarketDup, objZone, lsProcessDup, iHighestTSIndex, indexYS)
         
        # commit more units if there is unserved ancillary service

        #if cannot be served by local process, commit neighbour's process


        # assign commit setting in the origional market object
        for indexZone, objZone in enumerate(objMarketDup.lsZone):
            for indexProcess, objProcess in enumerate(objZone.lsProcess):
                iOperatoinStatus = objProcess.iOperatoinStatus_TS_YS[iHighestTSIndex, indexYS]
                
                objProcessOrigin = objMarket.lsZone[indexZone].lsProcess[indexProcess]
                for indexTS, objDayTS in enumerate(objDay.lsDiurnalTS):
                    objProcessOrigin.iOperatoinStatus_TS_YS[objDayTS.iTimeSliceIndex, indexYS] = iOperatoinStatus
                    
    return



def allocateRegulationCapacity_opr(objMarket, objZone, lsProcessDup, indexTS, indexYS):
    ''' arrange regulation capacity of the zone, and calculate deficit '''
    
    objZone.fASDfcRegulation_TS_YS[indexTS, indexYS] = objZone.fASRqrRegulation_TS_YS[indexTS, indexYS]
    
    # storage and limited dispatchable
    for objProcess in lsProcessDup:
        if objZone.fASDfcRegulation_TS_YS[indexTS, indexYS] > 0:
            if objProcess.sOperationMode in ["LimitDispatch","Storage"]:
                # check if previous allocated
                if (objProcess.fASRegulation_TS_YS[indexTS, indexYS] + objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS] \
                    + objProcess.fAS30MinReserve_TS_YS[indexTS, indexYS]) == 0:
                    # assume the regulation requirement is for 30 seconds
                    fTotalRampUp = objProcess.Capacity * (objProcess.RampRatePerM/100) / 2
                    fTotalRampUp = min(objProcess.Capacity/20, fTotalRampUp) # assumpe max operative reserve is 20% capacity
                    objProcess.fASRegulation_TS_YS[indexTS, indexYS] = fTotalRampUp
                    objZone.fASDfcRegulation_TS_YS[indexTS, indexYS] -= objProcess.fASRegulation_TS_YS[indexTS, indexYS]
                    print(objZone.fASDfcRegulation_TS_YS[indexTS, indexYS])
                    print(objZone.sZone, "reg", objProcess.sProcessName, objProcess.fASRegulation_TS_YS[indexTS, indexYS])
        else:
            break
        
    # dispatchable process
    for objProcess in lsProcessDup:
        if objZone.fASDfcRegulation_TS_YS[indexTS, indexYS] > 0:
            if objProcess.sOperationMode in ["Dispatch"] and \
            objProcess.iOperatoinStatus_TS_YS[indexTS, indexYS] == 2 : # the process has to be commited
                if "NUK" not in objProcess.sProcessName and "CHP" not in objProcess.sProcessName:
                    # check if previous allocated
                    if (objProcess.fASRegulation_TS_YS[indexTS, indexYS] + objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS] \
                            + objProcess.fAS30MinReserve_TS_YS[indexTS, indexYS]) == 0:
                            # assume the regulation requirement is for 30 seconds
                            objProcess.fASRegulation_TS_YS[indexTS, indexYS] = objProcess.Capacity * (objProcess.RampRatePerM/100) / 2
                            objZone.fASDfcRegulation_TS_YS[indexTS, indexYS] -= objProcess.fASRegulation_TS_YS[indexTS, indexYS]
                            print(objZone.fASDfcRegulation_TS_YS[indexTS, indexYS])
                            print(objZone.sZone, "reg", objProcess.sProcessName, objProcess.fASRegulation_TS_YS[indexTS, indexYS])
        else:
            break

    return



def allocate10MinReserve_opr(objMarket, objZone, lsProcessDup, indexTS, indexYS):
    ''' arrange 10 min operational reserve capacity of the zone, and calculate deficit '''
    
    objZone.fASDfc10MinReserve_TS_YS[indexTS, indexYS] = objZone.fASRqr10MinReserve_TS_YS[indexTS, indexYS]
    
    # storage and limited dispatchable
    for objProcess in lsProcessDup:
        if objZone.fASDfc10MinReserve_TS_YS[indexTS, indexYS] > 0:
            if objProcess.sOperationMode in ["LimitDispatch","Storage"]:
                # check if previous allocated
                if (objProcess.fASRegulation_TS_YS[indexTS, indexYS] + objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS] \
                    + objProcess.fAS30MinReserve_TS_YS[indexTS, indexYS]) == 0:
                    fTotalRampUp = objProcess.Capacity * (objProcess.RampRatePerM/100) * 10
                    fTotalRampUp = min(objProcess.Capacity/20, fTotalRampUp) # assumpe max operative reserve is 20% capacity
                    objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS] = fTotalRampUp
                    objZone.fASDfc10MinReserve_TS_YS[indexTS, indexYS] -= objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS]
                    print(objZone.fASDfc10MinReserve_TS_YS[indexTS, indexYS])
                    print(objZone.sZone, "10min", objProcess.sProcessName, objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS])
        else:
            break
        
    # dispatchable process
    for objProcess in lsProcessDup:
        if objZone.fASDfc10MinReserve_TS_YS[indexTS, indexYS] > 0:
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
                        print(objZone.fASDfc10MinReserve_TS_YS[indexTS, indexYS])
                        print(objZone.sZone, "10min", objProcess.sProcessName, objProcess.fAS10MinReserve_TS_YS[indexTS, indexYS])
        else:
            break

    return



def allocate30MinReserve_opr(objMarket, objZone, lsProcessDup, indexTS, indexYS):
    ''' arrange 30 min operational reserve capacity of the zone, and calculate deficit '''
    
    objZone.fASDfc30MinReserve_TS_YS[indexTS, indexYS] = objZone.fASRqr30MinReserve_TS_YS[indexTS, indexYS]
    
    # dispatchable process
    for objProcess in lsProcessDup:
        if objZone.fASDfc30MinReserve_TS_YS[indexTS, indexYS] > 0:
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
                        print(objZone.fASDfc30MinReserve_TS_YS[indexTS, indexYS])
                        print(objZone.sZone, "30min", objProcess.sProcessName, objProcess.fAS30MinReserve_TS_YS[indexTS, indexYS])
        else:
            break

    return



