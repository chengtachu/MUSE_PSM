# -*- coding: utf-8 -*-


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
        self.iYearSteps_YS = io_import_instance.get_AllYearSteps(_objInstanceConfig)

        # time slice
        self.lsTimeSlice = io_import_instance.get_TimeSlice(_objInstanceConfig)

        # energy commodity
        self.lsCommodity = io_import_instance.get_Commodity(_objInstanceConfig)

        # process list
        #self.lsProcessDefObjs = io_import_instance.get_ProcessDef(_objInstanceConfig)


        '''
        # default current year is base year
        self.iCurrentYear = self.iBaseYear

        # year steps in foresignt period
        self.aTimePeriod = io_import_instance.get_CurrentTimePeriod(self)

        # array offset to current year
        self.iTimePeriodOffset = 0
        
        
        # region and subregion
        self.listRegionObjs = io_import_instance.get_RegionList(_objInstanceConfig)
        self.listSubregionObjs = io_import_instance.get_SubregionList(_objInstanceConfig)
        io_import_instance.UpdateRegionIndex(self)
        
        
        '''

        print("")

        return





