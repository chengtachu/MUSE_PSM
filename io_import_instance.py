# -*- coding: utf-8 -*-

import numpy as np

import io_import_util
import cls_misc
import cls_region
import cls_market


class Import_Instance_Config:
    """ create an object to hold instance config in dataframe  """

    def __init__(self):
        
        strFilePath = "Data/" + "InstanceConfig.xlsx"
        
        ### import all instance config sheets
        self.dfMainInfo = io_import_util.getDataFrame(strFilePath,"MainInfo")
        self.dfStructure = io_import_util.getDataFrame(strFilePath,"Structure")
        self.dfMarket = io_import_util.getDataFrame(strFilePath,"Market")
        self.dfYearSteps = io_import_util.getDataFrame(strFilePath,"YearSteps")
        self.dfTimeSlice = io_import_util.getDataFrame(strFilePath,"TimeSlice")
        self.dfCommodity = io_import_util.getDataFrame(strFilePath,"Commodity")
        self.dfProcess = io_import_util.getDataFrame(strFilePath,"Process")
        self.dfGenerator = io_import_util.getDataFrame(strFilePath,"Generator")

        return



def get_MainInfo(objInstanceConfig):
    """ load basic configurations  """
    
    dfMainInfo = objInstanceConfig.dfMainInfo.set_index("ItemName")
    iBaseYear = int(dfMainInfo.loc["BaseYear","ItemValue"])
    sInstanceDesc = str(dfMainInfo.loc["InstanceDescription","ItemValue"])
    iForesight = int(dfMainInfo.loc["Foresight","ItemValue"])
    
    return iBaseYear, sInstanceDesc, iForesight



def get_AllYearSteps(objInstanceConfig):
    """ load all year steps configurations  """
    
    iYearSteps_YS = np.array(objInstanceConfig.dfYearSteps.columns.values[1:].tolist())

    return iYearSteps_YS



def get_TimeSlice(objInstanceConfig):
    """ get time-slice settings """
    
    lsTimeSlice = list()
    for index, row in objInstanceConfig.dfTimeSlice.iterrows():
        lsTimeSlice.append(cls_misc.TimeSlice(TSIndex=row["TSIndex"],Month=row["Month"],Day=row["Day"],Hour=row["Hour"], \
                                              DayIndex=row["DayIndex"],RepDayInYear=row["RepDayInYear"],RepHoursInDay=row["RepHoursInDay"], \
                                              RepHoursInYear=row["RepHoursInYear"]))

    return lsTimeSlice



def get_Commodity(objInstanceConfig):
    """ get commodities settings """
    
    lsCommodity = list()
    for index, row in objInstanceConfig.dfCommodity.iterrows():
        lsCommodity.append(cls_misc.Commodity(CommodityName=row["CommodityName"],Category=row["Category"],HeatRate=row["HeatRate"],\
                                              EmissionFactor_CO2=row["EmissionFactor_CO2"]))
    return lsCommodity



def get_ProcessDef(objInstanceConfig):
    """ get process definition settings """
    
    lsProcessDef = list()
    for index, row in objInstanceConfig.dfProcess.iterrows():
        lsProcessDef.append(cls_misc.ProcessDef(ProcessName=row["ProcessName"], ProcessType=row["ProcessType"], CCS=row["CCS"], \
                                                              ProcessFullName=row["ProcessFullName"], Fuel=row["Fuel"], \
                                                              OperationMode=row["OperationMode"]))
    return lsProcessDef



def get_Region(objInstanceConfig):
    """ get region/country/zone structure """
    
    # get region object
    lsRegionObj = list()


    # create region object
    dfRegion = objInstanceConfig.dfStructure.drop_duplicates("Region")

    for sRegion in dfRegion.loc[:,"Region"]:
        lsRegionObj.append(cls_region.Region(sRegion))


    # create country object      
    dfCountry = objInstanceConfig.dfStructure.drop_duplicates("Country")

    for index, row in dfCountry.iterrows():
        Region = row["Region"]
        Country = row["Country"]
        
        for objRegion in lsRegionObj:
            if Region == objRegion.sRegion:
                objRegion.lsCountry.append(cls_region.Country(Country))
                break

    # append zone list
    for index, row in objInstanceConfig.dfStructure.iterrows():
        Region = row["Region"]
        Country = row["Country"]
        Zone = row["Zone"]
    
        for objRegion in lsRegionObj:
            for objCountry in objRegion.lsCountry:
                if Country == objCountry.sCountry:
                    objCountry.sZone_ZN.append(Zone)
                    break

    return lsRegionObj


def get_Market(objInstanceConfig):
    """ get market/zone structure """
    
    # get market object
    lsMarket = list()

    # create region object
    dfMarket = objInstanceConfig.dfStructure.drop_duplicates("Market")

    for sMarket in dfMarket.loc[:,"Market"]:
        lsMarket.append(cls_market.Market(sMarket))

    # create zone object      
    for index, row in objInstanceConfig.dfStructure.iterrows():
        Market = row["Market"]
        Zone = row["Zone"]

        for objMarket in lsMarket:
            if Market == objMarket.sMarket:
                objMarket.lsZone.append(cls_market.Zone(Zone))
                break
                
    return lsMarket






