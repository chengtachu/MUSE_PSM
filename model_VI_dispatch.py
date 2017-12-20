# -*- coding: utf-8 -*-

import numpy as np

import cls_misc
import model_util
import model_util_gen
import model_util_trans
import model_util_unitcom


def dispatch_Main(objMarket, instance, indexYearStep):
    ''' the main function of dispatch '''
        
    # reset variables
    dispatch_Init(objMarket, indexYearStep)

    # copy key information to market process list objMarket.lsDispatchProcessIndex and objZone.lsCHPProcessIndex
    dispatch_ProcessIndexListInit(instance, objMarket, indexYearStep, "ExecMode")

    # Non-dispatchable generation (all time-slice)
    dispatch_nondispatchable(instance, objMarket, indexYearStep, "ExecMode")    

    # limited dispatchable generation
    dispatch_limiteddispatchable(instance, objMarket, indexYearStep, "ExecMode")  

    # dispatch CHP
    dispatch_CHP(instance, objMarket, indexYearStep, "ExecMode")

    # dispatch hydro-pump storage (HPS)
    dispatch_HPS(instance, objMarket, indexYearStep, "ExecMode")

    # check oversupply from non-dispatchable and dispatch to neighbors
    dispatch_oversupply(instance, objMarket, indexYearStep)
        
    # thermal generation unit commitment
    model_util_unitcom.unitCommitment(instance, objMarket, indexYearStep, "ExecMode")
    
    # dispatch main algorithm
    model_util_gen.dispatch_thermalUnit(instance, objMarket, indexYearStep, "ExecMode")

    # initiate nodal price
    model_util.nodeprice_Init(instance, objMarket, indexYearStep, "ExecMode")

    # calculate nodal price objDesSubregion.aNodalPrice_TS_YS
    model_util.calNodalPrice(instance, objMarket, indexYearStep)

    return



def dispatch_Plan(instance, objMarket, indexYearStep):
    ''' the main function of dispatch for planning '''
        
    # reset variables
    dispatch_Init(objMarket, indexYearStep)
    
    # copy key information to market process list objMarket.lsDispatchProcessIndex and objZone.lsCHPProcessIndex
    dispatch_ProcessIndexListInit(instance, objMarket, indexYearStep, "PlanMode")

    # Non-dispatchable generation (all time-slice)
    dispatch_nondispatchable(instance, objMarket, indexYearStep, "PlanMode")    

    # limited dispatchable generation
    dispatch_limiteddispatchable(instance, objMarket, indexYearStep, "PlanMode")  

    # dispatch CHP
    dispatch_CHP(instance, objMarket, indexYearStep, "PlanMode")

    # dispatch hydro-pump storage (HPS)
    dispatch_HPS(instance, objMarket, indexYearStep, "PlanMode")

    # check oversupply from non-dispatchable and dispatch to neighbors
    dispatch_oversupply(instance, objMarket, indexYearStep)

    # thermal generation unit commitment
    model_util_unitcom.unitCommitment(instance, objMarket, indexYearStep, "PlanMode")
    
    # dispatch main algorithm
    model_util_gen.dispatch_thermalUnit(instance, objMarket, indexYearStep, "PlanMode")

    # initiate nodal price
    model_util.nodeprice_Init(instance, objMarket, indexYearStep, "PlanMode")

    # calculate nodal price objDesSubregion.aNodalPrice_TS_YS
    model_util.calNodalPrice(instance, objMarket, indexYearStep)

    return



def dispatch_Init(objMarket, indexYearStep):
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

        objZone.fASDfcRegulation_TS_YS[:,indexYearStep] = 0
        objZone.fASDfc10MinReserve_TS_YS[:,indexYearStep] = 0
        objZone.fASDfc30MinReserve_TS_YS[:,indexYearStep] = 0

    return



def dispatch_ProcessIndexListInit(instance, objMarket, indexYS, sMode):
    ''' stack up dispatchable process  '''

    objMarket.lsDispatchProcessIndex = list()
    for indexZone, objZone in enumerate(objMarket.lsZone):
        objZone.lsCHPProcessIndex = list()
        
        if sMode == "ExecMode":
            lsProcess = objZone.lsProcess
        elif sMode == "PlanMode":
            lsProcess = objZone.lsProcessOperTemp

        # power process to stack on market stack list
        sYearStep = instance.iAllYearSteps_YS[indexYS]
        for indexProcess, objProcess in enumerate(lsProcess):
            if objProcess.CommitTime <= sYearStep and objProcess.DeCommitTime > sYearStep:
                if objProcess.sOperationMode == "Dispatch" and "CHP" not in objProcess.sProcessName:
                    objMarket.lsDispatchProcessIndex.append(cls_misc.MarketDispatchProcess(  \
                        indexZone=indexZone, indexProcess=indexProcess, sProcessName=objProcess.sProcessName, \
                        RampRatePerM=objProcess.RampRatePerM, fVariableGenCost_TS=objProcess.fVariableGenCost_TS_YS[:,indexYS] ))
    
        for objProcess in objMarket.lsDispatchProcessIndex:
            objProcess.fDAOfferPrice_TS = np.zeros( len(instance.lsTimeSlice) )
        
        # heat process to stack on zone stack list
        for indexProcess, objProcess in enumerate(lsProcess):
            if objProcess.CommitTime <= sYearStep and objProcess.DeCommitTime > sYearStep:
                if "CHP" in objProcess.sProcessName:
                    objZone.lsCHPProcessIndex.append(cls_misc.ZoneCHPProcess(  \
                        indexProcess=indexProcess, sProcessName=objProcess.sProcessName, \
                        fVariableGenCost_TS=objProcess.fVariableGenCost_TS_YS[:,indexYS] ))
    
    return
    


def dispatch_nondispatchable(instance, objMarket, indexYS, sMode):
    ''' calculate non-dispatchable generation  '''

    for indexZone, objZone in enumerate(objMarket.lsZone):

        if sMode == "ExecMode":
            lsProcess = objZone.lsProcess
        elif sMode == "PlanMode":
            lsProcess = objZone.lsProcessOperTemp
            
        sYearStep = instance.iAllYearSteps_YS[indexYS]
        for indexProcess, objProcess in enumerate(lsProcess):
            if objProcess.CommitTime <= sYearStep and objProcess.DeCommitTime > sYearStep:
                if objProcess.sOperationMode == "NonDispatch":
                        
                    model_util_gen.calNonDispatchGeneration(instance, objZone, objProcess, indexYS)
        
                    # add up non-dispatchable generation (MW)
                    objZone.fPowerOutput_TS_YS[:,indexYS] = objZone.fPowerOutput_TS_YS[:,indexYS] + objProcess.fHourlyPowerOutput_TS_YS[:,indexYS]
                    
                    # update operation status
                    objProcess.iOperatoinStatus_TS_YS[:, indexYS] = 1 # generating
    
        # update power residual demand
        model_util.updatePowerResidualDemand_Yearly(instance, objZone, indexYS)

    return



def dispatch_limiteddispatchable(instance, objMarket, indexYS, sMode):
    ''' calculate non-dispatchable generation  '''

    for indexZone, objZone in enumerate(objMarket.lsZone):

        if sMode == "ExecMode":
            lsProcess = objZone.lsProcess
        elif sMode == "PlanMode":
            lsProcess = objZone.lsProcessOperTemp
        
        sYearStep = instance.iAllYearSteps_YS[indexYS]
        for indexProcess, objProcess in enumerate(lsProcess):
            if objProcess.CommitTime <= sYearStep and objProcess.DeCommitTime > sYearStep:
                if objProcess.sOperationMode == "LimitDispatch":
                        
                    model_util_gen.calLimitedDispatchGeneration(instance, objZone, objProcess, indexYS)
        
                    # add up non-dispatchable generation (MW)
                    objZone.fPowerOutput_TS_YS[:,indexYS] = objZone.fPowerOutput_TS_YS[:,indexYS] + objProcess.fHourlyPowerOutput_TS_YS[:,indexYS]
                    
                    # update operation status
                    objProcess.iOperatoinStatus_TS_YS[:, indexYS] = 1 # generating
    
        # update power residual demand
        model_util.updatePowerResidualDemand_Yearly(instance, objZone, indexYS)

    return



def dispatch_CHP(instance, objMarket, indexYS, sMode):
    ''' dispatch CHP generation  '''

    # update heat residual demand
    for indexZone, objZone in enumerate(objMarket.lsZone):
        objZone.fHeatResDemand_TS_YS[:,indexYS] = objZone.fHeatDemand_TS_YS[:,indexYS] - objZone.fHeatOutput_TS_YS[:,indexYS]
            
    # dispatch heat and power generation
    for indexZone, objZone in enumerate(objMarket.lsZone):

        if sMode == "ExecMode":
            lsProcess = objZone.lsProcess
        elif sMode == "PlanMode":
            lsProcess = objZone.lsProcessOperTemp
        
        for indexTS, objTS in enumerate(instance.lsTimeSlice):    
            # sort zone CHP list by cost
            objZone.lsCHPProcessIndex = sorted(objZone.lsCHPProcessIndex, key=lambda lsCHPProcessIndex: lsCHPProcessIndex.fVariableGenCost_TS[indexTS])

            for indProcess, objProcess in enumerate(objZone.lsCHPProcessIndex):
                objCHP = lsProcess[objProcess.indexProcess]
                fHeatOutput = objCHP.fDeratedCapacity / objCHP.fCHPPowerToHeatRate
                fPowerOutput = objCHP.fDeratedCapacity
                
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
                    # update operation status
                    objCHP.iOperatoinStatus_TS_YS[indexTS, indexYS] = 1  # generating

                elif fHeatResDemand > 0.001:
                    # heat output
                    objCHP.fHourlyHeatOutput_TS_YS[indexTS,indexYS] = fHeatResDemand
                    objZone.fHeatOutput_TS_YS[indexTS,indexYS] = objZone.fHeatOutput_TS_YS[indexTS,indexYS] + objCHP.fHourlyHeatOutput_TS_YS[indexTS,indexYS]
                    objZone.fHeatResDemand_TS_YS[indexTS,indexYS] = objZone.fHeatDemand_TS_YS[indexTS,indexYS] - objZone.fHeatOutput_TS_YS[indexTS,indexYS]
                    # power output
                    objCHP.fHourlyPowerOutput_TS_YS[indexTS,indexYS] = fHeatResDemand * (fPowerOutput/fHeatOutput)
                    objZone.fPowerOutput_TS_YS[indexTS,indexYS] = objZone.fPowerOutput_TS_YS[indexTS,indexYS] + objCHP.fHourlyPowerOutput_TS_YS[indexTS,indexYS]
                    # update operation status
                    objCHP.iOperatoinStatus_TS_YS[indexTS, indexYS] = 1 # generating
                    
                else:
                    # update operation status
                    objCHP.iOperatoinStatus_TS_YS[indexTS, indexYS] = 2 # commited
                
        # update power residual demand
        model_util.updatePowerResidualDemand_Yearly(instance, objZone, indexYS)
                
    return



def dispatch_HPS(instance, objMarket, indexYS, sMode):
    ''' dispatch hydro-pump storage (HPS)  '''

    for indexZone, objZone in enumerate(objMarket.lsZone):

        if sMode == "ExecMode":
            lsProcess = objZone.lsProcess
        elif sMode == "PlanMode":
            lsProcess = objZone.lsProcessOperTemp
            
        sYearStep = instance.iAllYearSteps_YS[indexYS]
        for indexProcess, objProcess in enumerate(lsProcess):
            if objProcess.CommitTime <= sYearStep and objProcess.DeCommitTime > sYearStep:
                if objProcess.sOperationMode == "Storage":
                        
                    model_util_gen.calHPSOperation(instance, objZone, objProcess, indexYS)
        
                    # add up non-dispatchable generation (MW)
                    objZone.fPowerOutput_TS_YS[:,indexYS] = objZone.fPowerOutput_TS_YS[:,indexYS] + objProcess.fHourlyPowerOutput_TS_YS[:,indexYS]
        
                    # update power residual demand
                    model_util.updatePowerResidualDemand_Yearly(instance, objZone, indexYS)
 
                    # update operation status
                    objProcess.iOperatoinStatus_TS_YS[:, indexYS] = 1  # generating
    
    return



def dispatch_oversupply(instance, objMarket, indexYS):
    ''' check oversupply and export to neighbor zone  '''

    for indexZone, objZone in enumerate(objMarket.lsZone):
        for indexTS, objTS in enumerate(instance.lsTimeSlice):
        
            # export condistion test: 1.local power output > demand profile 2.find an export destination
            bExportLoop = True
            while bExportLoop:

                fOversupplyBlock = model_util_trans.checkZonePowerBalance(objMarket, objZone, indexTS, indexYS)
                if fOversupplyBlock > 0.001:    # need to use a small number because sometime it is non-zero without oversupply

                    # find the path and node to export
                    iPathIndex = model_util_trans.findExportPathIndex(objMarket, objZone, indexTS, indexYS)
                
                    if iPathIndex is -1:    # no path to export oversupply
                        bExportLoop = False
                    else:
                        # calculate the max injection of the selected path
                        fMaxInput = model_util_trans.calPathMaxInjection(objMarket, objZone, iPathIndex, fOversupplyBlock, indexTS, indexYS)
                        if fMaxInput > 1:   # to aviod loop because of the output saved from line loss
                            # dispatch the generation (the max injection may be lower because of reduced opposite direction transmit)
                            model_util_trans.calPathExport(objMarket, objZone, iPathIndex, fMaxInput, indexTS, indexYS)
                            # update the residual demand of the destination
                            objDestZone = objMarket.lsZone[objZone.lsConnectPath[iPathIndex].iDestZoneIndex]
                            model_util.updatePowerResDemandWithTrans(objMarket, objDestZone, indexTS, indexYS)
                        else:
                            bExportLoop = False
                else:   
                    # no oversupply
                    bExportLoop = False
                 
    return


