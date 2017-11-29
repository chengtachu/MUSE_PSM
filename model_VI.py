# -*- coding: utf-8 -*-

import numpy as np

import cls_misc
import model_util_gen


def dispatch_Main(objMarket, instance, indexYearStep):
    ''' the main function of dispatch '''
        
    # reset variables
    dispatch_Init(instance, objMarket, indexYearStep)

    # copy key information to market process list objMarket.lsAllDispatchPlants
    stackMarketDispatchProcess(instance, objMarket, indexYearStep)

    # Non-dispatchable generation (all time-slice)
    dispatch_nondispatchable(instance, objMarket, indexYearStep)    
    
    # limited dispatchable generation
    dispatch_limiteddispatchable(instance, objMarket, indexYearStep)  

    # dispatch CHP
    dispatch_CHP(instance, objMarket, indexYearStep)
    
    # dispatch hydro-pump storage
    

    # check oversupply and dispatch to neighbors
    
    
    # dispatch main algorithm


    # initiate nodal price


    # calculate nodal price objDesSubregion.aNodalPrice_TS_YR



    return



def dispatch_Init(instance, objMarket, indexYearStep):
    ''' reset variables  '''
    # transmission
    for objTrans in objMarket.lsTransmission:
        objTrans.fTransLineInput_TS_YS[:,indexYearStep] = 0
        objTrans.fTransLineOutput_TS_YS[:,indexYearStep] = 0
        objTrans.iLineStatus_TS_YS[:,indexYearStep] = 0

    # zone dispatch value
    for objZone in objMarket.lsZone:
        objZone.fPowerOutput_TS_YS[:,indexYearStep] = 0
        objZone.fResDemand_TS_YS[:,indexYearStep] = 0

    return


def stackMarketDispatchProcess(instance, objMarket, indexYS):
    ''' stack up dispatchable process  '''
    
    for indexZone, objZone in enumerate(objMarket.lsZone):
    
        sYearStep = instance.iAllYearSteps_YS[indexYS]
        for indexProcess, objProcess in enumerate(objZone.lsProcess):
            if objProcess.CommitTime <= sYearStep and objProcess.DeCommitTime > sYearStep:
                if objProcess.sOperationMode == "Dispatch" and "CHP" not in objProcess.sProcessName:
                    objMarket.lsAllDispatchPlants.append(cls_misc.RegionDispatchProcess(  \
                        indexZone=indexZone, indexProcess=indexProcess, sProcessName=objProcess.sProcessName, \
                        fVariableGenCost_TS=objProcess.fVariableGenCost_TS_YS[:,indexYS]   \
                    ))
    
        for objProcess in objMarket.lsAllDispatchPlants:
            objProcess.fDAOfferPrice_TS = np.zeros( len(instance.lsTimeSlice) )
        
        
    return



def dispatch_nondispatchable(instance, objMarket, indexYS):
    ''' calculate non-dispatchable generation  '''

    for indexZone, objZone in enumerate(objMarket.lsZone):

        sYearStep = instance.iAllYearSteps_YS[indexYS]
        for indexProcess, objProcess in enumerate(objZone.lsProcess):
            if objProcess.sOperationMode == "NonDispatch" and objProcess.CommitTime <= sYearStep and objProcess.DeCommitTime > sYearStep:
                    
                model_util_gen.calNonDispatchGeneration(instance, objZone, objProcess, indexYS)
    
                # add up non-dispatchable generation (MW)
                objZone.fPowerOutput_TS_YS[:,indexYS] = objZone.fPowerOutput_TS_YS[:,indexYS] + objProcess.fHourlyNetOutput_TS_YS[:,indexYS]
    
        # update residual demand
        objZone.fResDemand_TS_YS[:,indexYS] = objZone.fPowerDemand_TS_YS[:,indexYS] - objZone.fPowerOutput_TS_YS[:,indexYS]
        objZone.fResDemand_TS_YS[ objZone.fResDemand_TS_YS[:,indexYS] < 0 ,indexYS] = 0

    return



def dispatch_limiteddispatchable(instance, objMarket, indexYS):
    ''' calculate non-dispatchable generation  '''

    for indexZone, objZone in enumerate(objMarket.lsZone):

        sYearStep = instance.iAllYearSteps_YS[indexYS]
        for indexProcess, objProcess in enumerate(objZone.lsProcess):
            if objProcess.sOperationMode == "LimitDispatch" and objProcess.CommitTime <= sYearStep and objProcess.DeCommitTime > sYearStep:
                    
                model_util_gen.calLimitedDispatchGeneration(instance, objZone, objProcess, indexYS)
    
                # add up non-dispatchable generation (MW)
                objZone.fPowerOutput_TS_YS[:,indexYS] = objZone.fPowerOutput_TS_YS[:,indexYS] + objProcess.fHourlyNetOutput_TS_YS[:,indexYS]
    
        # update residual demand
        objZone.fResDemand_TS_YS[:,indexYS] = objZone.fPowerDemand_TS_YS[:,indexYS] - objZone.fPowerOutput_TS_YS[:,indexYS]
        objZone.fResDemand_TS_YS[ objZone.fResDemand_TS_YS[:,indexYS] < 0 ,indexYS] = 0

    return



def dispatch_CHP(instance, objMarket, indexYearStep):
    ''' dispatch CHP generation  '''

    # heat demand GJ -> MWh
    



    # calculate power generation



    return






