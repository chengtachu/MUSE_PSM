# -*- coding: utf-8 -*-

import cls_misc
import io_import_util

_sFolderPath = "Data/Assumption/"


def get_RegionTechAssump(instance):
    """ load region technical assumptions (process) """
    
    for objRegion in instance.lsRegion:
    
        sFilePath = _sFolderPath + "Region_Tech/" + objRegion.sRegion + ".xlsx"
        sSheetName = "GenTech"
        dfData = io_import_util.getDataFrame(sFilePath,sSheetName)
        dfData = dfData.drop(dfData.index[0])
        
        # load technical parameter
        for index, row in dfData.iterrows():
            dicParameters = {}
            for indexPR, sParameter in enumerate(row.index[1:]) :
                dicParameters[sParameter] = row[indexPR + 1]    # first column is ProcessName
            objRegion.lsProcess.append(cls_misc.RegionGenTech(row["ProcessName"], dicParameters))
        
        # load process efficiencty parameter
        
        # update definition from instance process definition
        '''
        for objRegionGenTech in objRegion.listRegionGenTech :
            sProcessName = objRegionGenTech.sProcessName

            for indexInstanceTech, objInstanceTech in enumerate(instance.lsProcessDefObjs):
                if objInstanceTech.sProcessName == sProcessName :
                    # carrier
                    objRegionGenTech.sCarrierIn = objInstanceTech.sCarrierIn
                    # operation mode
                    objRegionGenTech.sOperationMode = objInstanceTech.sOperationMode
        '''
        
        print("")
    
    return



