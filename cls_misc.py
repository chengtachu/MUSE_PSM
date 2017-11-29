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

class DayTimeSlice:
    """ time slice class  """

    def __init__(self, **kwargs):
        self.MonthDay = kwargs["MonthDay"]
        self.lsDiurnalTS = list()
        return

class DiurnalTimeSlice:
    """ time slice class  """

    def __init__(self, **kwargs):
        self.iTimeSliceIndex = kwargs["iTimeSliceIndex"]
        self.iRepHoursInYear = kwargs["iRepHoursInYear"]
        self.iRepHoursInDay = kwargs["iRepHoursInDay"]
        self.fValue = 0
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


class RegionProcessAssump(ProcessDef):
    """ regional process class assumption  """

    def __init__(self, ProcessName, dicParameters):
        # basic technical assumption for region
        self.sProcessName = ProcessName
        for sParameter, value in dicParameters.items():
            setattr(self, sParameter, value)
        return


class RegionDispatchProcess(ProcessDef):
    """ regional dispatchable process class """

    def __init__(self, **kwargs):
        # basic technical assumption
        self.indexZone = kwargs["indexZone"]
        self.indexProcess = kwargs["indexProcess"]
        self.sProcessName = kwargs["sProcessName"]
        
        ### simulation parameters
        self.fVariableGenCost_TS = kwargs["fVariableGenCost_TS"]      # USD/kWh
        self.fDAOfferPrice_TS = 0                   # USD/kW
        return



class ZoneProcess(ProcessDef):
    """ regional process class  """

    def __init__(self, Company, ProcessName, ProcessID, dicParameters):
        # basic technical assumption for region
        self.sCompany = Company
        self.sProcessName = ProcessName
        self.sProcessID = ProcessID
        for sParameter, value in dicParameters.items():
            setattr(self, sParameter, value)
            ''' ---- assumptions ---- '''
            # fDeratedCapacity      (MW)
            # fAnnualCapex          (MillionUSD / year)
            # fAnnualFixedCost      (MillionUSD / year)
                    
        ''' ---- variables ---- '''
        # fVariableGenCost_TS_YS
              
        # fHourlyNetOutput_TS_YS
        
        # fGenerationCost_TS_YS
        # fFuelConsumption_TS_YS
        # fCarbonCost_TS_YS
        # fGenerationCost_YS
        # fAnnualFixedCostPerMW
        # fAnnualInvestment_YR
        
        # fDAMarketVolumn_TS_YS
        # fDAOfferPrice_TS_YS

        return



#------------ transmission -------------
class Transmission:
    """ cross-subregion transmission class  """

    def __init__(self, dicParameters):
        for sParameter, value in dicParameters.items():
            setattr(self, sParameter, value)

        ### simulation parameters
        self.fTransLineInput_TS_YS = None   # MW
        self.fTransLineOutput_TS_YS = None  # MW

        self.fTransNewBuild_YS = None       # MW
        self.fTransAccCapacity_YS = None    # MW

        self.iLineStatus_TS_YS = None       # 0:Normal, 1:Congest

        return


class ConnectionPath:
    """ cross-zone connection topology  """

    def __init__(self):
        # basic technical assumption
        self.sDestination = None
        self.iDestZoneIndex = None
        self.iHopCount = 0
        self.lsHops = list()
        self.lsFlowPathOut = list()
        self.lsFlowPathIn = list()
        self.fDistance = None
        self.fAvailTransCapacity = None
        self.fLineLoss = None

        return



