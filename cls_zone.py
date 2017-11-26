# -*- coding: utf-8 -*-


import model_util

class Zone:
    """ create an country object  """

    def __init__(self, Zone):
        self.sZone = Zone
        self.iRegionIndex = 0
        self.iCountryIndex = 0
        self.lsProcessAssump = list()       # a list of process assumption in this zone
        self.lsProcess = list()             # a list of exist process in current modelling
        self.lsProcessFuture = list()       # a list of future process
        self.lsProcessDecomm = list()       # a list of decommited process
        self.CountryOutput = CountryOutput()
        return


class CountryOutput:

    def __init__(self):

        ##### model variable output

        self.dicGenCapacity_YR_TC = {}
        self.dicGenNewCapacity_YR_TC = {}

        self.dicGeneration_YR_TS_TC = {}
        self.dicPowerOutput_YR_TS_TC = {}
        self.dicStrgInput_YR_TS_ST = {}
        self.dicStrgOutput_YR_TS_ST = {}

        self.dicGenCAPEX_YR_TC = {}
        self.dicGenOPEX_YR_TC = {}
        self.dicEmissionCost_YR_TC = {}
        self.dicFuelCost_YR_TC = {}
        self.dicRunningCost_YR_TC = {}
        self.dicYearInvest_YR_TC = {}

        self.dicFuelConsum_YR_TS_TC = {}

        ##### model endogenous output

        self.dicGeneration_YR_TS = {}
        self.dicGenTechCost_YR_TC = {}
        self.dicGenCost_YR_TS = {}
        self.dicGenWholeSalePrice_YR_TS = {}

        self.dicCO2Emission_YR = {}
        self.dicCO2Emission_YR_TS = {}
        self.dicEmissionCaptured_YR_TS = {}
        self.dicFuelConsum_YR_TS_CR = {}       

        ##### ABM model
        self.dicDAMNodalPrice_YR_TS = {}
        self.dicRTMNodalPrice_YR_TS = {}

        return





