# -*- coding: utf-8 -*-




#------------ time slice -------------
class TimeSlice:
    """ time slice class  """

    def __init__(self, **kwargs):
        self.iTSIndex = kwargs["TSIndex"]
        self.sMonth = kwargs["Month"]
        self.sDay = kwargs["Day"]
        self.sHour = kwargs["Hour"]
        self.iDayIndex = kwargs["DayIndex"]
        self.iRepDayInYear = kwargs["RepDayInYear"]
        self.iRepHoursInDay = kwargs["RepHoursInDay"]
        self.iRepHoursInYear = kwargs["RepHoursInYear"]
        return



#------------ commodity -------------
class Commodity:
    """ Commodity class  """

    def __init__(self, **kwargs):
        self.sCommodityName = kwargs["CommodityName"]
        self.sCategory = kwargs["Category"]
        self.fHeatRate = kwargs["HeatRate"]
        self.fEmissionFactor_CO2 = kwargs["EmissionFactor_CO2"]
        self.fFuelPrice_TS_YS = list()
        return



#------------ technology/process -------------
class ProcessDef:
    """ basic process definition class  """

    def __init__(self, **kwargs):
        self.sProcessName = kwargs["ProcessName"]
        self.sProcessType = kwargs["ProcessType"]
        self.bCCS = str(kwargs["CCS"])
        self.sProcessFullName = kwargs["ProcessFullName"]
        self.sFuel = kwargs["Fuel"]
        self.sOperationMode = kwargs["OperationMode"]
        return




