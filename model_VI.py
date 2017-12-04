# -*- coding: utf-8 -*-

import numpy as np

import cls_misc
import model_util_gen
import model_util_trans


def dispatch_Main(objMarket, instance, indexYearStep):
    ''' the main function of dispatch '''
        
    # reset variables
    dispatch_Init(instance, objMarket, indexYearStep)

    # copy key information to market process list objMarket.lsDispatchProcessIndex
    stackMarketDispatchProcess(instance, objMarket, indexYearStep)

    # Non-dispatchable generation (all time-slice)
    dispatch_nondispatchable(instance, objMarket, indexYearStep)    
    
    # limited dispatchable generation
    dispatch_limiteddispatchable(instance, objMarket, indexYearStep)  

    # dispatch CHP
    dispatch_CHP(instance, objMarket, indexYearStep)
    
    # dispatch hydro-pump storage (HPS)
    dispatch_HPS(instance, objMarket, indexYearStep)

    # check oversupply from non-dispatchable and dispatch to neighbors
    dispatch_oversupply(instance, objMarket, indexYearStep)
    
    # thermal generation unit commitment
    unitCommitment_thermalUnit(instance, objMarket, indexYearStep)
    
    # dispatch main algorithm
    dispatch_thermalUnit(instance, objMarket, indexYearStep)

    # curtailment

    # initiate nodal price

    # calculate nodal price objDesSubregion.aNodalPrice_TS_YS


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
                    objMarket.lsDispatchProcessIndex.append(cls_misc.RegionDispatchProcess(  \
                        indexZone=indexZone, indexProcess=indexProcess, sProcessName=objProcess.sProcessName, \
                        fVariableGenCost_TS=objProcess.fVariableGenCost_TS_YS[:,indexYS]   \
                    ))
    
        for objProcess in objMarket.lsDispatchProcessIndex:
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
                            model_util_trans.updatePowerResDemandWithTrans(objMarket, objDestZone, indexTS, indexYS)
                        else:
                            bExportLoop = False
                else:   
                    # no oversupply
                    bExportLoop = False
                 
    return



def unitCommitment_thermalUnit(instance, objMarket, indexYS):
    ''' daily basis unit commitment for thermal unit '''

    # sum up the market residual demand
    fMarketTotalResDemand_TS_YS = np.zeros( (len(instance.lsTimeSlice), len(instance.iAllYearSteps_YS)) )
    for objZone in objMarket.lsZone:
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
        for objZone in objMarket.lsZone:
            objZone.fPowerResDemand_TS_YS[iHighestTSIndex,indexYS] += objZone.fASRqrRegulation_TS_YS[iHighestTSIndex,indexYS]
            objZone.fPowerResDemand_TS_YS[iHighestTSIndex,indexYS] += objZone.fASRqr10MinReserve_TS_YS[iHighestTSIndex,indexYS]
            objZone.fPowerResDemand_TS_YS[iHighestTSIndex,indexYS] += objZone.fASRqr30MinReserve_TS_YS[iHighestTSIndex,indexYS]
        
        # sort variable generation cost
        objMarket.lsDispatchProcessIndex = sorted(objMarket.lsDispatchProcessIndex, key=lambda lsDispatchProcessIndex: \
                                                  lsDispatchProcessIndex.fVariableGenCost_TS[iHighestTSIndex])
        
        # dispatch the time-slice with hightst residual demand (this step make sure a lower bound of reliability requirement)
        for objProcessIndex in objMarket.lsDispatchProcessIndex:
            objDispatchZone = objMarket.lsZone[objProcessIndex.indexZone]
            objDispatchProcess = objDispatchZone.lsProcess[objProcessIndex.indexProcess]
            dispatch_thermalUnit_TS(instance, objMarket, objDispatchZone, objDispatchProcess, iHighestTSIndex, indexYS)
    
        # arrange ancillary service among commited units
        #for objZone in objMarket.lsZone:
            # arrange regulation capacity of the zone, and calculate deficit
            # arrange 10 min reserve capacity of the zone, and calculate deficit
            # arrange 30 min reserve capacity of the zone, and calculate deficit
        
        #for objZone in objMarket.lsZone:
            # commit more units if there is unserved ancillary service
        
        #if cannot be served by local process, commit neighbour's process

        # reset output
        
        # reset residual demand


    return



def dispatch_thermalUnit(instance, objMarket, indexYS):
    ''' dispatch thermal units '''

    # for each day

        # sort variable generation cost

        # dispatch with the commited units

    return



def dispatch_thermalUnit_TS(instance, objMarket, objZone, objProcess, indexTS, indexYS):
    ''' dispatch thermal units for only given time slice '''

    fMustRunOutput = objProcess.fDeratedCapacity * (objProcess.MinLoadRate / 100)
    fExportOutput = 0

    if objZone.fPowerResDemand_TS_YS[indexTS, indexYS] > 0.001:
        # commit this process
        objProcess.iOperatoinStatus_TS_YS[indexTS, indexYS] = 2
        if objProcess.fDeratedCapacity > objZone.fPowerResDemand_TS_YS[indexTS, indexYS]:   # MW
            # residual demand can be served
            objProcess.fHourlyPowerOutput_TS_YS[indexTS,indexYS] = objZone.fPowerResDemand_TS_YS[indexTS, indexYS]
            objZone.fPowerOutput_TS_YS[indexTS,indexYS] += objZone.fPowerResDemand_TS_YS[indexTS, indexYS]
            objZone.fPowerResDemand_TS_YS[indexTS, indexYS] = 0
            fExportOutput = objProcess.fDeratedCapacity - objProcess.fHourlyPowerOutput_TS_YS[indexTS,indexYS]
        else:
            # dispatch all output
            objProcess.fHourlyPowerOutput_TS_YS[indexTS,indexYS] = objProcess.fDeratedCapacity
            objZone.fPowerResDemand_TS_YS[indexTS, indexYS] -= objProcess.fDeratedCapacity
            objZone.fPowerOutput_TS_YS[indexTS,indexYS] += objProcess.fDeratedCapacity
    else :
        # no local residual demand, check export
        fExportOutput = objProcess.fDeratedCapacity

    # export the generation (local residual demand has to be 0 here)
    while fExportOutput > 1:
        # find the path and node to export (-1: no path to export)
        iPathIndex = model_util_trans.findExportPathIndex(objMarket, objZone, indexTS, indexYS)
        if iPathIndex is not -1:
            # calculate the max injection of the selected path
            fMaxInput = model_util_trans.calPathMaxInjection(objMarket, objZone, iPathIndex, fExportOutput, indexTS, indexYS)
            # dispatch the generation (the max injection may be lower because of reduced opsite direction transmit)
            model_util_trans.calPathExport(objMarket, objZone, iPathIndex, fMaxInput, indexTS, indexYS)
            fExportOutput = fExportOutput - fMaxInput

            # update local generation
            objProcess.fHourlyPowerOutput_TS_YS[indexTS,indexYS] += fMaxInput
            objZone.fPowerOutput_TS_YS[indexTS,indexYS] += fMaxInput
                    
            # update the residual demand
            objDestZone = objMarket.lsZone[objZone.lsConnectPath[iPathIndex].iDestZoneIndex]
            model_util_trans.calResidualDemandWithConn(objMarket, objDestZone, indexTS, indexYS)

        else:
            # all line is full, break the loop
            fExportOutput = 0
            # check must-run block (this might cause over generation), need to maintain at least must-run level
            if objProcess.fHourlyPowerOutput_TS_YS[indexTS,indexYS] < fMustRunOutput:
                objZone.fPowerOutput_TS_YS[indexTS,indexYS] += (fMustRunOutput - objProcess.fHourlyPowerOutput_TS_YS[indexTS,indexYS])
                objProcess.fHourlyPowerOutput_TS_YS[indexTS,indexYS] = fMustRunOutput
            
    return


