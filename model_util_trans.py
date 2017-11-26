# -*- coding: utf-8 -*-

import copy
import numpy as np

import cls_misc

def constructConnectTopology(objMarket, instance, iHopLimit):
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
                for index, objZone in enumerate(objMarket.lsZone):
                    if objZone.sZone == objNewPath.sDestination:
                        objNewPath.iDestZoneIndex = index
                        break

                objNewPath.iHopCount = iExpendLevel
                objNewPath.fAvailTransCapacity = np.zeros(len(instance.lsTimeSlice))
                objNewPath.fLineLoss = objTrans.LossRate / 100
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
            if objTrans.To not in objExistPath.listHops:
                objNewPath = copy.deepcopy(objExistPath)
                objNewPath.lsHops.append(objTrans.To)

                objNewPath.sDestination = objTrans[indexLine].To
                for index, objZone in enumerate(objMarket.lsZone):
                    if objZone.sZone == objNewPath.sDestination:
                        objNewPath.iDestZoneIndex = index
                        break

                objNewPath.iHopCount = iExpendLevel
                objNewPath.fAvailTransCapacity = np.zeros(len(instance.lsTimeSlice))
                objNewPath.fLineLoss = 1 - ( (1 - objNewPath.fLineLoss) * ( 1 - objTrans.LossRate/100) )
                # path out
                objNewPath.lsFlowPathOut.append(indexLine)
                # path in
                objNewPath.lsFlowPathIn.append(_FindPathIn(objMarket, objZone.sZone, objNewPath.sDestination))

                objZone.lsConnectPath.append(objNewPath)

                # recursive to construct next hop from destination node
                if iExpendLevel + 1 <= iHopLimit:
                    _constructNextNode(instance, objMarket, objZone, objNewPath, iExpendLevel + 1, iHopLimit)

    return





