# -*- coding: utf-8 -*-

import numpy as np

import io_import_util
import cls_misc


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




