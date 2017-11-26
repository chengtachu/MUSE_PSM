# -*- coding: utf-8 -*-

import copy


def model_Init(objMarket, instance):
    ''' market initiation '''
    
    # first time to run of the model (base year, and no output)
    if instance.iForesightStartYear == instance.iBaseYear and objMarket.MarketOutput.dicGenCapacity_YR_TC == {} :

        # calculate the required generation from power plants (include distribution loss and import/export)
        ZoneDemand_Init(objMarket, instance)

        # aggregate plant with the same type and commit or decommit in the same period
        ZoneExistProcess_Init(objMarket, instance)
        
        # calculate derived parameters for existing plants (fixed cost, derated capacity)
        ZoneExistProcess(objSubregion.listGenPlant)

        print("")

    return



def ZoneDemand_Init(objMarket, instance):
    ''' calculate the required generation from power plants (include distribution loss and import/export) '''
        
    for objZone in objMarket.lsZone:
        
        # account for power distribution loss
        objZone.fPowerDemand_TS_YS[instance.iFSBaseYearIndex:,:] = \
        objZone.fPowerDemand_TS_YS[instance.iFSBaseYearIndex:,:] * (1 + objZone.fPowerLossRatio_YS[instance.iFSBaseYearIndex:] / 100)
    
        # account for import/export 
        objZone.fPowerDemand_TS_YS[instance.iFSBaseYearIndex:,:] = \
        objZone.fPowerDemand_TS_YS[instance.iFSBaseYearIndex:,:] + objZone.fPowerImport_TS_YS[instance.iFSBaseYearIndex:,:]
    
    return



def ZoneExistProcess_Init(objMarket, instance):
    ''' calculate the zone demand from power plants (include distribution loss and import/export) '''
            
    # move decommited plant into decommitioned list
    for objZone in objMarket.lsZone:
        for objProcess in list(objZone.lsProcess):
            if objProcess.DeCommitTime <= instance.iForesightStartYear:
                objZone.listGenPlantDecom.append(copy.copy(objProcess))
                objZone.listGenPlant.remove(objProcess)

    # don't move plant decommited in the future into future list, if the data read from database, they should be planned for the near future

            
    return




