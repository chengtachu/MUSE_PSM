# -*- coding: utf-8 -*-

import numpy as np

import io_import_instance
import io_import_regionNcountry
import io_import_market

class Instance:
    """ create an instance object  """

    def __init__(self):

        ###### import all instance config
        _objInstanceConfig = io_import_instance.Import_Instance_Config()

        ###### check and convert data

        # basic info
        self.iBaseYear, self.sInstanceDesc, self.iForesight = io_import_instance.get_MainInfo(_objInstanceConfig)

        # year steps
        self.iAllYearSteps_YS = io_import_instance.get_AllYearSteps(_objInstanceConfig)

        # time slice
        self.lsTimeSlice = io_import_instance.get_TimeSlice(_objInstanceConfig)

        # energy commodity
        self.lsCommodity = io_import_instance.get_Commodity(_objInstanceConfig)

        # process list
        self.lsProcessDefObjs = io_import_instance.get_ProcessDef(_objInstanceConfig)

        # default current year is base year
        self.iCurrentYear = self.iBaseYear

        # year steps in foresignt period
        self.iFSYearSteps_YS = self.get_FSYearSteps()

        # Region structure
        self.lsRegion = io_import_instance.get_Region(_objInstanceConfig)

        # market structure
        self.lsMarket = io_import_instance.get_Market(_objInstanceConfig)
        
        return



    def get_FSYearSteps(self):
        """ get a array of current foresight year steps """
        
        aFSYearSteps = []
        for iYear in self.iAllYearSteps_YS:
            if iYear >= self.iCurrentYear and iYear <= (self.iCurrentYear + self.iForesight):
                aFSYearSteps.append(iYear)
    
        aCurrentFSYearSteps = np.array(aFSYearSteps)   
    
        return aCurrentFSYearSteps



    def get_RegionAssumption(self):
        """ get assumptions on region level """
        
        for objRegion in self.lsRegion:
            
            # import region technical assumptions
            io_import_regionNcountry.get_RegionTechAssump(objRegion, self.lsProcessDefObjs, self.iAllYearSteps_YS)
            
            # import region cost assumptions
            io_import_regionNcountry.get_RegionCostAssump(objRegion, self.iAllYearSteps_YS)
        
        return



    def get_CountryAssumption(self):
        """ get assumptions on country level """
        
        for objRegion in self.lsRegion:
            
            for objCountry in objRegion.lsCountry:
            
                # copy all process assumption from region
                for objProcess in objRegion.lsProcessAssump :
                    objCountry.lsProcessAssump = objRegion.lsProcessAssump.copy()
                
                # import country technical assumptions (override region)
                io_import_regionNcountry.get_CountryTechAssump(objRegion, objCountry, self.iAllYearSteps_YS)
                
                # import country cost assumptions (override region)
                io_import_regionNcountry.get_CountryCostAssump(objRegion, objCountry, self.iAllYearSteps_YS)
                
        return



    def get_MarketSettings(self):
        """ market settings """
        
        for objMarket in self.lsMarket:
            
            # import market policy
            io_import_market.get_MarketPolicy(objMarket, self.iAllYearSteps_YS)
            
            # import market transmission
            io_import_market.get_MarketTransmission(objMarket)
            
        return



    def get_ZoneAssumption(self):
        """ market settings """
        
        for objMarket in self.lsMarket:
            
            for objZone in objMarket.lsZone:
                
                # import zone technical assumptoin
                io_import_market.get_ZoneTechAssump(objZone, self.iAllYearSteps_YS)
            
                # update index to region and country
                for indexRegion, objRegion in enumerate(self.lsRegion):
                    for indexCountry, objCountry in enumerate(objRegion.lsCountry):
                        if objZone.sZone in objCountry.sZone_ZN:
                            objZone.iRegionIndex = indexRegion
                            objZone.iCountryIndex = indexCountry
                
                # copy available process
                #io_import_market.get_ZoneProcess(self)
                
                # import exist process
                
                # import process develop limit
                
                # import renewable output
                
            
        return






