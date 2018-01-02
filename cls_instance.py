# -*- coding: utf-8 -*-

import numpy as np

import cls_misc
import io_import_instance
import io_import_regionNcountry
import io_import_market
import model_solution_main
import model_solution_output

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
        
        # structure day time slice
        self.lsDayTimeSlice = self.set_DayTimeSlice()

        # energy commodity
        self.lsCommodity = io_import_instance.get_Commodity(_objInstanceConfig)

        # process list
        self.lsProcessDefObjs = io_import_instance.get_ProcessDef(_objInstanceConfig)

        # default current year is base year
        self.iForesightStartYear = self.iBaseYear

        # new year steps and start year index in foresignt period  (iFSYearSteps_YS, iFSBaseYearIndex)
        self.get_FSYearSteps()

        # Region structure
        self.lsRegion = io_import_instance.get_Region(_objInstanceConfig)

        # market structure
        self.lsMarket = io_import_instance.get_Market(_objInstanceConfig)
        
        return



    def set_DayTimeSlice(self):
        """ structure day time slice """
        
        lsDayTimeSlice = list()
        iDaySliceStart = 0
        iDaySliceEnd = 0
    
        while( iDaySliceStart < len(self.lsTimeSlice)):
    
            # find Day Start Slice and End Slice
            sDay = ""
            for iIndex in range(iDaySliceStart, len(self.lsTimeSlice)):
                if self.lsTimeSlice[iIndex].iDayIndex == self.lsTimeSlice[iDaySliceStart].iDayIndex:
                    iDaySliceEnd = iIndex
                    sDay = self.lsTimeSlice[iIndex].sMonth + self.lsTimeSlice[iIndex].sDay
                else:
                    break
    
            lsDayTimeSlice.append(cls_misc.DayTimeSlice( MonthDay = sDay ))
    
            for iIndex in range(iDaySliceStart, iDaySliceEnd+1):
                lsDayTimeSlice[-1].lsDiurnalTS.append(cls_misc.DiurnalTimeSlice( \
                iTimeSliceIndex = iIndex, iRepHoursInYear = self.lsTimeSlice[iIndex].iRepHoursInYear, iRepHoursInDay = self.lsTimeSlice[iIndex].iRepHoursInDay ))
                
            # to next segement of time slice 
            iDaySliceStart = iDaySliceEnd + 1

        return lsDayTimeSlice



    def get_FSYearSteps(self):
        """ get/update a array of current foresight year steps """
        
        aFSYearSteps = []
        for iYear in self.iAllYearSteps_YS:
            if iYear >= self.iForesightStartYear and iYear <= (self.iForesightStartYear + self.iForesight):
                aFSYearSteps.append(iYear)
    
        self.iFSYearSteps_YS = np.array(aFSYearSteps)  
        for index, iYearStep in enumerate(self.iAllYearSteps_YS):
            if iYearStep == self.iFSYearSteps_YS[0]:
                self.iFSBaseYearIndex = index
                break
    
        return



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
        """ load market settings """
        
        for objMarket in self.lsMarket:
            
            # import market policy
            io_import_market.get_MarketPolicy(objMarket, self.iAllYearSteps_YS)
            
            # import market transmission
            io_import_market.get_MarketTransmission(objMarket)
            
        return



    def get_ZoneAssumption(self):
        """ load zone assumptions """
        
        for indexMarket, objMarket in enumerate(self.lsMarket):
            for objZone in objMarket.lsZone:
                
                # import zone technical assumptoin
                io_import_market.get_ZoneTechAssump(objZone, self.iAllYearSteps_YS)
            
                # update index to region and country
                for indexRegion, objRegion in enumerate(self.lsRegion):
                    for indexCountry, objCountry in enumerate(objRegion.lsCountry):
                        if objZone.sZone in objCountry.sZone_ZN:
                            objZone.iRegionIndex = indexRegion
                            objZone.iCountryIndex = indexCountry
                            objZone.iMarketIndex = indexMarket
                
                # copy available process
                io_import_market.get_ZoneProcessAvail(self, objZone)
                
                # import exist process
                io_import_market.get_ZoneExistProcess(self, objZone)
                
                # import process develop limit
                io_import_market.get_ZoneProcessLimit(objZone, self.iAllYearSteps_YS)
                
                # import renewable output
                io_import_market.get_ZoneVREOutput(objZone, self.lsTimeSlice)
            
        return



    def update_MUSEInput(self):
        """ update external data from MUSE """
        
        for objRegion in self.lsRegion:
            for objCountry in objRegion.lsCountry:
                
                # carbon price
                io_import_regionNcountry.get_CountryCarbonPrice(objCountry, self.iAllYearSteps_YS)
                
                # fuel price
                io_import_regionNcountry.get_CountryFuelPrice(self, objCountry)
            
        for objMarket in self.lsMarket:
            for objZone in objMarket.lsZone:
            
                # power demand and heat demand
                io_import_market.update_ZonePowerHeatDemand(objZone, self.lsTimeSlice, self.iAllYearSteps_YS)

                # import/export
                io_import_market.update_ZonePowerImport(objZone, self.lsTimeSlice, self.iAllYearSteps_YS)
            
        return



    def run(self):
        """ run the models """

        for objMarket in self.lsMarket:
            
            if objMarket.sModel == "VI":
                objMarket.modelrun_VI(self)
                
            elif objMarket.sModel == "WM":
                objMarket.modelrun_WM(self)
                
        # result aggregation into country and region
        model_solution_main.updateCountrySolution(self)
        model_solution_main.updateRegionSolution(self)
                
        for objRegion in self.lsRegion:
            for objCountry in objRegion.lsCountry:
                model_solution_output.outputCountrySolution(self, objCountry)
        
        for objRegion in self.lsRegion:
            model_solution_output.outputRegionSolution(self, objRegion)

        return
    
    
    
    
