# -*- coding: utf-8 -*-


import cls_misc


def dispatch_Main(objMarket, instance, indexYearStep):
    ''' the main function of dispatch '''
        
    # initialization
    dispatch_Init(instance, objMarket, indexYearStep)

    # copy key information to market process list objMarket.lsAllDispatchPlants
    objMarket.lsAllDispatchPlants = list()
    for objZone in objMarket.lsZone:
        StackMarketDispatchProcess(instance, objMarket, objZone.lsProcess, indexYearStep)

    # dispatch CHP


    # dispatch must-run plants and calculate Non-dispatchable generation (all time-slice)
    
    
    # dispatch hydro-pump storage


    # check oversupply and dispatch to neighbors
    
    # dispatch main algorithm


    # initiate nodal price


    # calculate nodal price objDesSubregion.aNodalPrice_TS_YR



    return



def dispatch_Init(instance, objMarket, indexYearStep):

    # initialize transmission
    for objTrans in objMarket.lsTransmission:
        objTrans.fTransLineInput_TS_YS[:,indexYearStep] = 0
        objTrans.fTransLineOutput_TS_YS[:,indexYearStep] = 0
        objTrans.iLineStatus_TS_YS[:,indexYearStep] = 0

    # initialize zone dispatch value
    for objZone in objMarket.lsZone:
        objZone.fPowerOutput_TS_YS[:,indexYearStep] = 0
        objZone.fResDemand_TS_YS[:,indexYearStep] = 0



def StackMarketDispatchProcess(instance, objMarket, lsProcess, indexYS):

    sYearStep = instance.iAllYearSteps_YS[indexYS]
    for indexP, objProcess in enumerate(lsProcess):
        if objProcess.CommitTime <= sYearStep and objProcess.DeCommitTime > sYearStep:
            if objProcess.sOperationMode == "Dispatch" and "CHP" not in objProcess.sProcessName:
                objMarket.lsAllDispatchPlants.append(cls_misc.RegionPlant(  \
                    iPlantIndex=indexP, sPlantID=objPlant.sPlantID, \
                    sGenTechID=objPlant.sGenTechID, iTechIndex=objPlant.iTechIndex, fGenCostPerUnit=objPlant.fGenCostPerUnit_YR[indexTimePeriod]   \
                ))

    for indexP, objPlant in enumerate(objMarket.lsAllDispatchPlants):
        objPlant.fDAOfferPrice_TS = np.zeros( len(instance.listTimeSlice) )
        
        
        



