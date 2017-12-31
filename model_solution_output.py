# -*- coding: utf-8 -*-

import numpy as np

import io_export

def outputZoneSolution(instance, objMarket):

    # create folder
    io_export.CheckMarketFolderAndDeleteExistFiles(objMarket.sMarket + "_Zone")

    setTimeSliceSN = [ objTimeSlice.iTSIndex for objTimeSlice in instance.lsTimeSlice ]

    simulatedYearStep_YS = []
    for iYearStep in instance.iAllYearSteps_YS:
        if iYearStep <= instance.iFSYearSteps_YS[-1]:
            simulatedYearStep_YS.append(iYearStep)

    for objZone in objMarket.lsZone:
        
        objCountry = instance.lsRegion[objZone.iRegionIndex].lsCountry[objZone.iCountryIndex]
        
        ZoneProcessSet = [ objProcessAssump.sProcessName for objProcessAssump in objZone.lsProcessAssump ]
        ZoneProcessStrgSet = [ objProcessAssump.sProcessName for objProcessAssump in objZone.lsProcessAssump if objProcessAssump.sOperationMode == "Storage" ]
        setCommodity = [ objCommodity.sCommodityName for objCommodity in objCountry.lsCommodity ]

        listOutput = objZone.ZoneOutput.__dict__.keys()
        for dataItem in listOutput:
            tableOutput = []
            dataTable = getattr(objZone.ZoneOutput, dataItem)

            if bool(dataTable): # check if the dictionary is empty (don't change the order)
                if "_YS_TS_PR" in dataItem:
                    tableOutput =  DictToArray_X_Y_Z(dataTable, simulatedYearStep_YS, setTimeSliceSN, ZoneProcessSet)
                elif "_YS_TS_ST" in dataItem:
                    tableOutput =  DictToArray_X_Y_Z(dataTable, simulatedYearStep_YS, setTimeSliceSN, ZoneProcessStrgSet)
                elif "_YS_TS_CM" in dataItem:
                    tableOutput =  DictToArray_X_Y_Z(dataTable, simulatedYearStep_YS, setTimeSliceSN, setCommodity)
                elif "_YS_PR" in dataItem:
                    tableOutput =  DictToArray_X_Y(dataTable, simulatedYearStep_YS, ZoneProcessSet)
                elif "_YS_TS" in dataItem:
                    tableOutput =  DictToArray_X_Y(dataTable, simulatedYearStep_YS, setTimeSliceSN)
                elif "_YS" in dataItem:
                    tableOutput =  DictToArray_X(dataTable, simulatedYearStep_YS)

                io_export.TableOutputToCSV(objMarket.sMarket + "_Zone", tableOutput, objZone.sZone + "_" + dataItem)



def outputMarketSolution(instance, objMarket):

    # create folder
    io_export.CheckMarketFolderAndDeleteExistFiles(objMarket.sMarket)

    simulatedYearStep_YS = []
    for iYearStep in instance.iAllYearSteps_YS:
        if iYearStep <= instance.iFSYearSteps_YS[-1]:
            simulatedYearStep_YS.append(iYearStep)

    setTimeSlice = [ objTimeSlice.iTSIndex for objTimeSlice in instance.lsTimeSlice ]
    setMarketProcess = [ objProcessAssump.sProcessName for objProcessAssump in instance.lsProcessDefObjs ]
    setMarketProcessStrg = [ objProcessAssump.sProcessName for objProcessAssump in instance.lsProcessDefObjs if objProcessAssump.sOperationMode == "Storage"]
    setCommodity = [ objCommodity.sCommodityName for objCommodity in instance.lsCommodity ]
    setTransmission = [ objTrsm.PowerFlowID for objTrsm in objMarket.lsTransmission ]
    #setGenerator = [ objGenerator.sGeneratorID for objGenerator in objMarket.listGenerator ]

    listOutput = objMarket.MarketOutput.__dict__.keys()
    for dataItem in listOutput:
        tableOutput = []
        dataTable = getattr(objMarket.MarketOutput, dataItem)

        if bool(dataTable): # check if the dictionary is empty (don't change the order)
            if "_YS_TS_PR" in dataItem:
                tableOutput =  DictToArray_X_Y_Z(dataTable, simulatedYearStep_YS, setTimeSlice, setMarketProcess)
            elif "_YS_TS_ST" in dataItem:
                tableOutput =  DictToArray_X_Y_Z(dataTable, simulatedYearStep_YS, setTimeSlice, setMarketProcessStrg)
            elif "_YS_TS_CM" in dataItem:
                tableOutput =  DictToArray_X_Y_Z(dataTable, simulatedYearStep_YS, setTimeSlice, setCommodity)
            elif "_YS_TS_TR" in dataItem:
                tableOutput =  DictToArray_X_Y_Z(dataTable, simulatedYearStep_YS, setTimeSlice, setTransmission)
            #elif "_YS_PR_GR" in dataItem:
            #    tableOutput =  DictToArray_X_Y_Z(dataTable, simulatedYearStep_YS, RegionTechSet, setGenerator)
            elif "_YS_PR" in dataItem:
                tableOutput =  DictToArray_X_Y(dataTable, simulatedYearStep_YS, setMarketProcess)
            elif "_YS_TS" in dataItem:
                tableOutput =  DictToArray_X_Y(dataTable, simulatedYearStep_YS, setTimeSlice)
            elif "_YS_TR" in dataItem:
                tableOutput =  DictToArray_X_Y(dataTable, simulatedYearStep_YS, setTransmission)
            #elif "_YS_GR" in dataItem:
            #    tableOutput =  DictToArray_X_Y(dataTable, simulatedYearStep_YS, setGenerator)
            elif "_YS" in dataItem:
                tableOutput =  DictToArray_X(dataTable, simulatedYearStep_YS)

            io_export.TableOutputToCSV(objMarket.sMarket, tableOutput, dataItem)


#------------------------------------------------------------------
# Output solution to file
#------------------------------------------------------------------

def DictToArray_X(dicData, setYS):

    aNewData = np.zeros(len(setYS))

    # copy dictionary to array
    for IndexYS, sIndexYS in enumerate(setYS):
        if type(dicData) is dict:
            aNewData[IndexYS] = round(dicData[sIndexYS], 3)
        else:
            aNewData[IndexYS] = round(dicData[sIndexYS].value, 3)

    # append head at the first row
    aDataHeader = np.empty( [len(setYS)], dtype=object)
    for IndexYS, sIndexYS in enumerate(setYS):
        aDataHeader[IndexYS] = sIndexYS

    aFullTable = np.vstack([aDataHeader, aNewData])

    return aFullTable


def DictToArray_X_Y(dicData, setYS, setPR):

    aNewData = np.zeros((len(setPR), len(setYS)))

    # copy dictionary to array
    for IndexPR, sIndexPR in enumerate(setPR):
        for IndexYS, sIndexYS in enumerate(setYS):
            if type(dicData) is dict:
                aNewData[IndexPR, IndexYS] = round(dicData[sIndexYS, sIndexPR], 3)
            else:
                aNewData[IndexPR, IndexYS] = round(dicData[sIndexYS, sIndexPR].value, 3)

    # append index at the first column
    aDataWithIndex = np.empty( [len(setPR), len(setYS)+1], dtype=object)
    for IndexPR, sIndexPR in enumerate(setPR):
        aDataWithIndex[IndexPR, 0] = sIndexPR
        for IndexYS, sIndexYS in enumerate(setYS):
            aDataWithIndex[IndexPR, IndexYS + 1] = aNewData[IndexPR, IndexYS]

    # append head at the first row
    aDataHeader = np.empty( [len(setYS)+1], dtype=object)
    aDataHeader[0] = ""
    for IndexYS, sIndexYS in enumerate(setYS):
        aDataHeader[IndexYS+1] = sIndexYS

    aFullTable = np.vstack([aDataHeader, aDataWithIndex])

    return aFullTable


def DictToArray_X_Y_Z(dicData, setYS, IndexTS, setPR):

    aFullTable = np.empty( [len(setYS)+1], dtype=object)  # need to add an empty row to initialize object
    
    for IndexPR, sIndexPR in enumerate(setPR):

        aNewData = np.zeros((len(IndexTS), len(setYS)))

        # copy dictionary to array
        for indexTS, sIndexTS in enumerate(IndexTS):
            for IndexYS, sIndexYS in enumerate(setYS):
                if type(dicData) is dict:
                    aNewData[indexTS, IndexYS] = round(dicData[sIndexYS, sIndexTS, sIndexPR], 3)
                else:
                    aNewData[indexTS, IndexYS] = round(dicData[sIndexYS, sIndexTS, sIndexPR].value, 3)

        # append index at the first column
        aDataWithIndex = np.empty( [len(IndexTS), len(setYS)+1], dtype=object)
        for indexTS, sIndexTS in enumerate(IndexTS):
            aDataWithIndex[indexTS, 0] = sIndexTS
            for IndexYS, sIndexYS in enumerate(setYS):
                aDataWithIndex[indexTS, IndexYS + 1] = aNewData[indexTS, IndexYS]

        # append head at the first row
        aDataHeader = np.empty( [len(setYS)+1], dtype=object)
        aDataHeader[0] = sIndexPR
        for IndexYS, sIndexYS in enumerate(setYS):
            aDataHeader[IndexYS+1] = sIndexYS

        aTable = np.vstack([aDataHeader, aDataWithIndex])

        aFullTable = np.vstack([aFullTable, aTable])

    aFullTable = np.delete(aFullTable, 0, 0)    # delete first row

    return aFullTable






