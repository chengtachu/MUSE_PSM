# -*- coding: utf-8 -*-

import numpy as np

import cls_misc
import model_util_gen


def dispatch_Main(objMarket, instance, indexYearStep):
    ''' the main function of dispatch '''
        
    # reset variables
    dispatch_Init(instance, objMarket, indexYearStep)

    # copy key information to market process list objMarket.lsAllDispatchProcessIndex
    stackMarketDispatchProcess(instance, objMarket, indexYearStep)

    # Non-dispatchable generation (all time-slice)
    dispatch_nondispatchable(instance, objMarket, indexYearStep)    
    
    # limited dispatchable generation
    dispatch_limiteddispatchable(instance, objMarket, indexYearStep)  

    # dispatch CHP
    dispatch_CHP(instance, objMarket, indexYearStep)
    
    # dispatch hydro-pump storage (HPS)
    dispatch_HPS(instance, objMarket, indexYearStep)

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
        objZone.fPowerResDemand_TS_YS[:,indexYearStep] = 0
        objZone.fHeatOutput_TS_YS[:,indexYearStep] = 0
        objZone.fHeatResDemand_TS_YS[:,indexYearStep] = 0

    return


def stackMarketDispatchProcess(instance, objMarket, indexYS):
    ''' stack up dispatchable process  '''
    
    for indexZone, objZone in enumerate(objMarket.lsZone):
    
        # power process to stack on market stack list
        sYearStep = instance.iAllYearSteps_YS[indexYS]
        for indexProcess, objProcess in enumerate(objZone.lsProcess):
            if objProcess.CommitTime <= sYearStep and objProcess.DeCommitTime > sYearStep:
                if objProcess.sOperationMode == "Dispatch" and "CHP" not in objProcess.sProcessName:
                    objMarket.lsAllDispatchProcessIndex.append(cls_misc.RegionDispatchProcess(  \
                        indexZone=indexZone, indexProcess=indexProcess, sProcessName=objProcess.sProcessName, \
                        fVariableGenCost_TS=objProcess.fVariableGenCost_TS_YS[:,indexYS]   \
                    ))
    
        for objProcess in objMarket.lsAllDispatchProcessIndex:
            objProcess.fDAOfferPrice_TS = np.zeros( len(instance.lsTimeSlice) )
        
        # heat process to stack on zone stack list
        for indexProcess, objProcess in enumerate(objZone.lsProcess):
            if objProcess.CommitTime <= sYearStep and objProcess.DeCommitTime > sYearStep:
                if "CHP" in objProcess.sProcessName:
                    objZone.lsCHPProcessIndex.append(cls_misc.ZoneCHPProcess(  \
                        indexProcess=indexProcess, sProcessName=objProcess.sProcessName, \
                        fVariableGenCost_TS=objProcess.fVariableGenCost_TS_YS[:,indexYS]   \
                    ))
        
    return



def dispatch_nondispatchable(instance, objMarket, indexYS):
    ''' calculate non-dispatchable generation  '''

    for indexZone, objZone in enumerate(objMarket.lsZone):

        sYearStep = instance.iAllYearSteps_YS[indexYS]
        for indexProcess, objProcess in enumerate(objZone.lsProcess):
            if objProcess.sOperationMode == "NonDispatch" and objProcess.CommitTime <= sYearStep and objProcess.DeCommitTime > sYearStep:
                    
                model_util_gen.calNonDispatchGeneration(instance, objZone, objProcess, indexYS)
    
                # add up non-dispatchable generation (MW)
                objZone.fPowerOutput_TS_YS[:,indexYS] = objZone.fPowerOutput_TS_YS[:,indexYS] + objProcess.fHourlyPowerOutput_TS_YS[:,indexYS]
    
    # update power residual demand
    model_util_gen.updatePowerResidualDemand_Yearly(instance, objMarket, indexYS)

    return



def dispatch_limiteddispatchable(instance, objMarket, indexYS):
    ''' calculate non-dispatchable generation  '''

    for indexZone, objZone in enumerate(objMarket.lsZone):

        sYearStep = instance.iAllYearSteps_YS[indexYS]
        for indexProcess, objProcess in enumerate(objZone.lsProcess):
            if objProcess.sOperationMode == "LimitDispatch" and objProcess.CommitTime <= sYearStep and objProcess.DeCommitTime > sYearStep:
                    
                model_util_gen.calLimitedDispatchGeneration(instance, objZone, objProcess, indexYS)
    
                # add up non-dispatchable generation (MW)
                objZone.fPowerOutput_TS_YS[:,indexYS] = objZone.fPowerOutput_TS_YS[:,indexYS] + objProcess.fHourlyPowerOutput_TS_YS[:,indexYS]
    
    # update power residual demand
    model_util_gen.updatePowerResidualDemand_Yearly(instance, objMarket, indexYS)

    return



def dispatch_CHP(instance, objMarket, indexYS):
    ''' dispatch CHP generation  '''

    # update heat residual demand
    for indexZone, objZone in enumerate(objMarket.lsZone):
        objZone.fHeatResDemand_TS_YS[:,indexYS] = objZone.fHeatDemand_TS_YS[:,indexYS] - objZone.fHeatOutput_TS_YS[:,indexYS]
            
    # dispatch heat and power generation
    for indexZone, objZone in enumerate(objMarket.lsZone):
        for indexTS, objTS in enumerate(instance.lsTimeSlice):
            
            # sort zone CHP list by cost
            objZone.lsCHPProcessIndex = sorted(objZone.lsCHPProcessIndex, key=lambda lsCHPProcessIndex: lsCHPProcessIndex.fVariableGenCost_TS[indexTS])

            for indProcess, objProcess in enumerate(objZone.lsCHPProcessIndex):
                objCHP = objZone.lsProcess[objProcess.indexProcess]
                fHeatOutput = objCHP.fDeratedCapacity * (1-objCHP.fCHPPowerRatio)
                fPowerOutput = objCHP.fDeratedCapacity * objCHP.fCHPPowerRatio
                
                fHeatResDemand = objZone.fHeatResDemand_TS_YS[indexTS, indexYS]
                  
                ''' fixed ratio of power and heat generation '''
                if fHeatOutput <= fHeatResDemand:
                    # heat output
                    objCHP.fHourlyHeatOutput_TS_YS[indexTS,indexYS] = fHeatOutput
                    objZone.fHeatOutput_TS_YS[indexTS,indexYS] = objZone.fHeatOutput_TS_YS[indexTS,indexYS] + objCHP.fHourlyHeatOutput_TS_YS[indexTS,indexYS]
                    objZone.fHeatResDemand_TS_YS[indexTS,indexYS] = objZone.fHeatDemand_TS_YS[indexTS,indexYS] - objZone.fHeatOutput_TS_YS[indexTS,indexYS]
                    # power output
                    objCHP.fHourlyPowerOutput_TS_YS[indexTS,indexYS] = fPowerOutput
                    objZone.fPowerOutput_TS_YS[indexTS,indexYS] = objZone.fPowerOutput_TS_YS[indexTS,indexYS] + objCHP.fHourlyPowerOutput_TS_YS[indexTS,indexYS]

                elif fHeatResDemand > 0:
                    # heat output
                    objCHP.fHourlyHeatOutput_TS_YS[indexTS,indexYS] = fHeatResDemand
                    objZone.fHeatOutput_TS_YS[indexTS,indexYS] = objZone.fHeatOutput_TS_YS[indexTS,indexYS] + objCHP.fHourlyHeatOutput_TS_YS[indexTS,indexYS]
                    objZone.fHeatResDemand_TS_YS[indexTS,indexYS] = objZone.fHeatDemand_TS_YS[indexTS,indexYS] - objZone.fHeatOutput_TS_YS[indexTS,indexYS]
                    # power output
                    objCHP.fHourlyPowerOutput_TS_YS[indexTS,indexYS] = fHeatResDemand * (fPowerOutput/fHeatOutput)
                    objZone.fPowerOutput_TS_YS[indexTS,indexYS] = objZone.fPowerOutput_TS_YS[indexTS,indexYS] + objCHP.fHourlyPowerOutput_TS_YS[indexTS,indexYS]

                    break
                
    # update power residual demand
    model_util_gen.updatePowerResidualDemand_Yearly(instance, objMarket, indexYS)
                
    return



def dispatch_HPS(instance, objMarket, indexYS):
    ''' dispatch hydro-pump storage (HPS)  '''

    for indexZone, objZone in enumerate(objMarket.lsZone):

        sYearStep = instance.iAllYearSteps_YS[indexYS]
        for indexProcess, objProcess in enumerate(objZone.lsProcess):
            if objProcess.sOperationMode == "Storage" and objProcess.CommitTime <= sYearStep and objProcess.DeCommitTime > sYearStep:
                    
                model_util_gen.calHPSOperation(instance, objZone, objProcess, indexYS)
    
                # add up non-dispatchable generation (MW)
                objZone.fPowerOutput_TS_YS[:,indexYS] = objZone.fPowerOutput_TS_YS[:,indexYS] + objProcess.fHourlyPowerOutput_TS_YS[:,indexYS]
    
                # update power residual demand
                model_util_gen.updatePowerResidualDemand_Yearly(instance, objMarket, indexYS)
 
    return



