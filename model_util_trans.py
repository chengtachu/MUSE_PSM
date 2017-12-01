# -*- coding: utf-8 -*-

import copy
import numpy as np

import cls_misc

def constructTrans(objMarket, instance, iHopLimit):
    ''' construct and initiate nodes and path '''
    
    # recursive
    for objZone in objMarket.lsZone:

        iExpendLevel = 1
        for indexLine, objTrans in enumerate(objMarket.lsTransmission):
            if objTrans.From == objZone.sZone:
                objNewPath = cls_misc.ConnectionPath()
                objNewPath.lsHops.append(objZone.sZone)
                objNewPath.lsHops.append(objTrans.To)

                objNewPath.sDestination = objTrans.To
                for index, objZoneDes in enumerate(objMarket.lsZone):
                    if objZoneDes.sZone == objNewPath.sDestination:
                        objNewPath.iDestZoneIndex = index
                        break

                objNewPath.iHopCount = iExpendLevel
                objNewPath.fAvailTransCapacity = np.zeros(len(instance.lsTimeSlice))
                objNewPath.fLineLoss = objTrans.FlowLossRate / 100
                # path out
                objNewPath.lsFlowPathOut.append(indexLine)
                # path in
                objNewPath.lsFlowPathIn.append(_FindPathIn(objMarket, objZone.sZone, objNewPath.sDestination))

                objZone.lsConnectPath.append(objNewPath)

                # recursive to construct next hop from destination node
                if iExpendLevel + 1 <= iHopLimit:
                    _constructNextNode(instance, objMarket, objZone, objNewPath, iExpendLevel + 1, iHopLimit)

    return



def _FindPathIn(objMarket, sZone, sDestination):
    ''' find the connection of the reverse direction '''
    
    for indexLine, objTrans in enumerate(objMarket.lsTransmission):
        if objTrans.From == sDestination:
            if objTrans.To == sZone:
                return indexLine

    return -1



def _constructNextNode(instance, objMarket, objZone, objExistPath, iExpendLevel, iHopLimit):
    ''' recursive function to construct node topology '''
    
    sCurrentNode = objExistPath.sDestination

    for indexLine, objTrans in enumerate(objMarket.lsTransmission):
        if objTrans.From == sCurrentNode:
            if objTrans.To not in objExistPath.lsHops:
                objNewPath = copy.deepcopy(objExistPath)
                objNewPath.lsHops.append(objTrans.To)

                objNewPath.sDestination = objTrans.To
                for index, objZoneDes in enumerate(objMarket.lsZone):
                    if objZoneDes.sZone == objNewPath.sDestination:
                        objNewPath.iDestZoneIndex = index
                        break

                objNewPath.iHopCount = iExpendLevel
                objNewPath.fAvailTransCapacity = np.zeros(len(instance.lsTimeSlice))
                objNewPath.fLineLoss = 1 - ( (1 - objNewPath.fLineLoss) * ( 1 - objTrans.FlowLossRate/100) )
                # path out
                objNewPath.lsFlowPathOut.append(indexLine)
                # path in
                objNewPath.lsFlowPathIn.append(_FindPathIn(objMarket, sCurrentNode, objNewPath.sDestination))

                objZone.lsConnectPath.append(objNewPath)

                # recursive to construct next hop from destination node
                if iExpendLevel + 1 <= iHopLimit:
                    _constructNextNode(instance, objMarket, objZone, objNewPath, iExpendLevel + 1, iHopLimit)

    return



def checkZonePowerBalance(objMarket, objZone, indexTS, indexYS):
    ''' check power balance of the subregion ( +:oversupply; -:shortage) '''
        
    # all connection import
    fConnImport = 0
    for index, objConnLine in enumerate(objMarket.lsTransmission): 
        if objConnLine.To == objZone.sZone:
            fConnImport += objConnLine.fTransLineOutput_TS_YS[indexTS, indexYS]

    # all connection export
    fConnExport = 0
    for index, objConnLine in enumerate(objMarket.lsTransmission): 
        if objConnLine.From == objZone.sZone:
            fConnExport += objConnLine.fTransLineInput_TS_YS[indexTS, indexYS]

    fPowerBalance = fConnImport - fConnExport + objZone.fPowerOutput_TS_YS[indexTS, indexYS] - objZone.fPowerDemand_TS_YS[indexTS, indexYS]

    return fPowerBalance



def findExportPathIndex(objMarket, objZone, indexTS, indexYS):
    ''' find the best path to export '''
        
    sDestination = ""
    fLineLoss = 1
    iHigestResidualDemand = 0
    iPathIndex = -1

    # find the destination and path in the condition: 1.higest residual demand 2.lowest loss 3.path available
    for index, objConnPath in enumerate(objZone.lsConnectPath): 
        
        objDestZone = objMarket.lsZone[objConnPath.iDestZoneIndex]

        if objConnPath.sDestination is not sDestination:
            if objDestZone.fPowerResDemand_TS_YS[indexTS, indexYS] > iHigestResidualDemand:
                if _testAllTransAvailble(objMarket.lsTransmission, objConnPath.lsFlowPathOut, indexTS, indexYS):
                    sDestination = objConnPath.sDestination
                    fLineLoss = objConnPath.fLineLoss
                    iHigestResidualDemand = objDestZone.fPowerResDemand_TS_YS[indexTS, indexYS]
                    iPathIndex = index
        else:   # path for the same destination node
            if objConnPath.fLineLoss < fLineLoss:
                if _testAllTransAvailble(objMarket.lsTransmission, objConnPath.lsFlowPathOut, indexTS, indexYS):
                    fLineLoss = objConnPath.fLineLoss
                    iHigestResidualDemand = objDestZone.fPowerResDemand_TS_YS[indexTS, indexYS]
                    iPathIndex = index

    return iPathIndex



def _testAllTransAvailble(lsTransmission, lsFlowPathOut, indexTS, indexYS):
    ''' test if all cross-zone transmission on the path is available '''
    
    bAllLineAvailble = True
    for iLineIndex in lsFlowPathOut:
        iLineIndex = int(iLineIndex)
        if lsTransmission[iLineIndex].iLineStatus_TS_YS[indexTS, indexYS] != 0:
            bAllLineAvailble = False
            break

    return bAllLineAvailble



def calPathMaxInjection(objMarket, objZone, iPathIndex, fSupplyBlock, indexTS, indexYS):
    ''' calculate the max injection of the selected path '''
    
    # residual demand of destination, calculate the line loss
    objDestZone = objMarket.lsZone[objZone.lsConnectPath[iPathIndex].iDestZoneIndex]
    fDestResidualDemand = objDestZone.fPowerResDemand_TS_YS[indexTS, indexYS]
    for iLineIndex in objZone.lsConnectPath[iPathIndex].lsFlowPathOut:
        fDestResidualDemand = fDestResidualDemand/(1-objMarket.lsTransmission[iLineIndex].FlowLossRate/100)

    # find the line with lowest input capacity, calculate the line loss
    fMaxPathCapacity = 999999
    iMaxInputLineIndex = 0
    for iLineIndex in objZone.lsConnectPath[iPathIndex].lsFlowPathOut:
        fLineAvailCapacity = objMarket.lsTransmission[iLineIndex].fTransAccCapacity_YS[indexYS] \
        - objMarket.lsTransmission[iLineIndex].fTransLineInput_TS_YS[indexTS, indexYS]
        if fLineAvailCapacity < fMaxPathCapacity:
            fMaxPathCapacity = fLineAvailCapacity
            iMaxInputLineIndex = iLineIndex
            
    # calculate the line loss from the capacity limit line back to export node
    for iLineIndex in objZone.lsConnectPath[iPathIndex].lsFlowPathOut:
        if iLineIndex is not iMaxInputLineIndex:
            fMaxPathCapacity = fMaxPathCapacity/(1-objMarket.lsTransmission[iLineIndex].FlowLossRate/100)
        else:
            break

    fPathMaxInput = min(fSupplyBlock, fDestResidualDemand, fMaxPathCapacity)

    return max(0, fPathMaxInput)



def calPathExport(objMarket, objZone, iPathIndex, fMaxInput, indexTS, indexYS):
    ''' calculate and update the transmission volume on the path from the injection zone '''
    # the max injection may be lower because of reduced opsite direction transmit
    # algorithm checked, 100% correct!!!

    # calculate reduced loss
    fLineInput = fMaxInput
    fReducedInjection = 0   # reduced injection because of reduced flow on reverse direction
    for iLineSeq, iLineIndex in enumerate(objZone.lsConnectPath[iPathIndex].lsFlowPathOut): 

        iReverseLineIndex = objZone.lsConnectPath[iPathIndex].lsFlowPathIn[iLineSeq]
        fReverseFlowInput = objMarket.lsTransmission[iReverseLineIndex].fTransLineInput_TS_YS[indexTS, indexYS]
   
        fLineInput = fLineInput * (1-objMarket.lsTransmission[iLineIndex].FlowLossRate/100)   # the output of the line

        # the reduced power transmit from the other end of the line (100% sure this algorithm is correct)
        if fReverseFlowInput > 0.00001:     # need to use a small number to avoid a bug
            if fLineInput > fReverseFlowInput:
                # reduce all reverse flow
                fReducedInjection += fReverseFlowInput * (objMarket.lsTransmission[iReverseLineIndex].FlowLossRate/100)
                fReducedInjection += (fReverseFlowInput / (1-objMarket.lsTransmission[iLineIndex].FlowLossRate/100)) - fReverseFlowInput
            else:   
                # noly reduce part of the reverse flow
                fReducedInjection += fLineInput * (objMarket.lsTransmission[iReverseLineIndex].FlowLossRate/100)
                fReducedInjection += (fLineInput / (1-objMarket.lsTransmission[iLineIndex].FlowLossRate/100)) - fLineInput

    fMaxInput = fMaxInput - fReducedInjection

    # calculate the flow on the lines
    fLineInput = fMaxInput
    for iLineSeq, iLineIndex in enumerate(objZone.lsConnectPath[iPathIndex].lsFlowPathOut): 

        iReverseLineIndex = objZone.lsConnectPath[iPathIndex].lsFlowPathIn[iLineSeq]
        fReverseFlowInput = objMarket.lsTransmission[iReverseLineIndex].fTransLineInput_TS_YS[indexTS, indexYS]   
        fReverseFlowOutput = objMarket.lsTransmission[iReverseLineIndex].fTransLineOutput_TS_YS[indexTS, indexYS]          

        if fReverseFlowInput > 0.001:   # need to use a small number to avoid a bug
            # flow on reverse direction (no flow on current direction)
            if fLineInput > fReverseFlowOutput:
                # line injection higher than reverse flow
                fLineInput = fLineInput - fReverseFlowOutput
                objMarket.lsTransmission[iLineIndex].fTransLineInput_TS_YS[indexTS, indexYS] = fLineInput
                fLineInput = fLineInput * (1-objMarket.lsTransmission[iLineIndex].FlowLossRate/100)
                objMarket.lsTransmission[iLineIndex].fTransLineOutput_TS_YS[indexTS, indexYS] = fLineInput
                # add back the reverse input (***very important***)
                fLineInput = fLineInput + fReverseFlowInput
                # set reverse flow 0
                objMarket.lsTransmission[iReverseLineIndex].fTransLineInput_TS_YS[indexTS, indexYS] = 0  
                objMarket.lsTransmission[iReverseLineIndex].fTransLineOutput_TS_YS[indexTS, indexYS] = 0
            else:
                # line injection smaller than reverse flow
                # set current line flow 0
                objMarket.lsTransmission[iLineIndex].fTransLineInput_TS_YS[indexTS, indexYS] = 0
                objMarket.lsTransmission[iLineIndex].fTransLineOutput_TS_YS[indexTS, indexYS] = 0
                # reduced reverse flow
                objMarket.lsTransmission[iReverseLineIndex].fTransLineOutput_TS_YS[indexTS, indexYS] = fReverseFlowOutput - fLineInput
                objMarket.lsTransmission[iReverseLineIndex].fTransLineInput_TS_YS[indexTS, indexYS] = fReverseFlowInput - (fLineInput / (1-objMarket.lsTransmission[iReverseLineIndex].FlowLossRate/100))
                # add back the reverse input (***very important***)
                fLineInput = fLineInput * (1-objMarket.lsTransmission[iLineIndex].FlowLossRate/100)
        else:
            # no flow on reverse direction
            objMarket.lsTransmission[iLineIndex].fTransLineInput_TS_YS[indexTS, indexYS] += fLineInput
            fLineInput = fLineInput * (1-objMarket.lsTransmission[iLineIndex].FlowLossRate/100)
            objMarket.lsTransmission[iLineIndex].fTransLineOutput_TS_YS[indexTS, indexYS] += fLineInput

        # check the line congestion
        if objMarket.lsTransmission[iLineIndex].fTransAccCapacity_YS[indexYS] - objMarket.lsTransmission[iLineIndex].fTransLineInput_TS_YS[indexTS, indexYS] < 0.001:
            objMarket.lsTransmission[iLineIndex].iLineStatus_TS_YS[indexTS, indexYS] = 1

    return



def calResidualDemandWithTrans(objMarket, objZone, indexTS, indexYS):
    ''' calculate residual demand considering cross-zone import/export '''
    
    # all connection import
    fConnImport = 0
    for index, objConnLine in enumerate(objMarket.lsTransmission): 
        if objConnLine.To == objZone.sZone:
            fConnImport += objConnLine.fTransLineOutput_TS_YS[indexTS, indexYS]

    # all connection export
    fConnExport = 0
    for index, objConnLine in enumerate(objMarket.lsTransmission): 
        if objConnLine.From == objZone.sZone:
            fConnExport += objConnLine.fTransLineInput_TS_YS[indexTS, indexYS]

    fResidualDemand = objZone.fPowerDemand_TS_YS[indexTS, indexYS] - objZone.fPowerOutput_TS_YS[indexTS, indexYS] - fConnImport + fConnExport

    if fResidualDemand > 0.01:
        objZone.fPowerResDemand_TS_YS[indexTS, indexYS] = fResidualDemand
    else :
        objZone.fPowerResDemand_TS_YS[indexTS, indexYS] = 0

    return




