# -*- coding: utf-8 -*-

import numpy as np

import io_import_instance

class Create:
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
        
        # process technical assumptions
        for objRegion in self.lsRegion:
        
        
            print("")

        return














