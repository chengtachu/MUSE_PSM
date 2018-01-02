# -*- coding: utf-8 -*-


class Region:
    """ create an region object  """

    def __init__(self, Region):
        self.sRegion = Region
        self.lsCountry = list()          # a list of country index under this region
        self.lsProcessAssump = list()          # a list of country index under this region
        self.RegionOutput = RegionOutput()
        return


class RegionOutput:

    def __init__(self):

        self.dicGenCapacity_YS_PR = {}
        self.dicGenNewCapacity_YS_PR = {}

        self.dicPowerGen_YS_TS_PR = {}
        self.dicPowerOutput_YS_TS_PR = {}
        self.dicHeatGen_YS_TS_PR = {}
        self.dicHeatOutput_YS_TS_PR = {}
        self.dicStrgInput_YS_TS_ST = {}
        self.dicStrgOutput_YS_TS_ST = {}

        self.dicGenCAPEX_YS_PR = {}
        self.dicGenOPEX_YS_PR = {}
        self.dicEmissionCost_YS_PR = {}
        self.dicFuelCost_YS_PR = {}
        self.dicRunningCost_YS_PR = {}
        self.dicYearInvest_YS_PR = {}

        self.dicFuelConsum_YS_TS_PR = {}

        ##### model endogenous output

        self.dicRegionPowerOutput_YS_TS = {}
        self.dicRegionPowerGen_YS_TS = {}
        self.dicRegionHeatOutput_YS_TS = {}
        self.dicRegionHeatGen_YS_TS = {}
        self.dicProcessLCOE_YS_PR = {}
        self.dicPowerGenCost_YS_TS = {}
        self.dicPowerWholeSalePrice_YS_TS = {}

        self.dicCO2Emission_YS = {}
        self.dicCO2Emission_YS_TS = {}
        self.dicEmissionCaptured_YS_TS = {}
        self.dicFuelConsum_YS_TS_CM = {}        

        '''
        ##### ABM model
        self.dicGeneratorProfit_YS_GR = {}
        self.dicGeneratorCapacity_YS_PR_GR = {}
        '''

        return



class Country:
    """ create an country object  """

    def __init__(self, Country):
        self.sCountry = Country
        self.sZone_ZN = list()              # a list of zone ID under this country
        self.lsProcessAssump = list()       # a list of country index under this region
        self.CountryOutput = CountryOutput()
        # self.lsCommodity                  # a list of commodity in the country
        # self.fCarbonCost_YS
        #self.iZoneIndex_ZN = list()        # a list of zone index under this country
        return


class CountryOutput:

    def __init__(self):

        self.dicGenCapacity_YS_PR = {}
        self.dicGenNewCapacity_YS_PR = {}

        self.dicPowerGen_YS_TS_PR = {}
        self.dicPowerOutput_YS_TS_PR = {}
        self.dicHeatGen_YS_TS_PR = {}
        self.dicHeatOutput_YS_TS_PR = {}
        self.dicStrgInput_YS_TS_ST = {}
        self.dicStrgOutput_YS_TS_ST = {}

        self.dicGenCAPEX_YS_PR = {}
        self.dicGenOPEX_YS_PR = {}
        self.dicEmissionCost_YS_PR = {}
        self.dicFuelCost_YS_PR = {}
        self.dicRunningCost_YS_PR = {}
        self.dicYearInvest_YS_PR = {}

        self.dicFuelConsum_YS_TS_PR = {}

        self.dicAncSerRegulation_YS_TS = {}
        self.dicAncSer10MinReserve_YS_TS = {}
        self.dicAncSer30MinReserve_YS_TS = {}

        self.dicPctCapacityCommit_YS_TS_PR = {}
        self.dicPctCapacityGenerate_YS_TS_PR = {}
        self.dicPctCapacityAncSer_YS_TS_PR = {}
        
        ## transmission
        self.dicCrossBorderTrading_YS_TS = {}
        self.dicDomesticTrading_YS_TS = {}

        ##### model endogenous output

        self.dicCountryPowerOutput_YS_TS = {}
        self.dicCountryPowerGen_YS_TS = {}
        self.dicCountryHeatOutput_YS_TS = {}
        self.dicCountryHeatGen_YS_TS = {}
        self.dicProcessLCOE_YS_PR = {}
        self.dicPowerGenCost_YS_TS = {}
        self.dicPowerWholeSalePrice_YS_TS = {}

        self.dicCO2Emission_YS = {}
        self.dicCO2Emission_YS_TS = {}
        self.dicEmissionCaptured_YS_TS = {}
        self.dicFuelConsum_YS_TS_CM = {}        

        '''
        ##### ABM model
        self.dicGeneratorProfit_YS_GR = {}
        self.dicGeneratorCapacity_YS_PR_GR = {}
        '''

        return




