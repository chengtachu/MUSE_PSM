# -*- coding: utf-8 -*-

import time

import cls_instance



if __name__ == '__main__':

    start_time = time.time()

    # create instance and import instance configs (Data/nstanceConfig.xlsx)
    instance = cls_instance.Instance()
    print('{:f}'.format(time.time() - start_time) + " instance created")

    # import regiom assumptions (Data/ExoAssumption)
    instance.get_RegionAssumption()

    # import country assumptions (Data/ExoAssumption)
    instance.get_CountryAssumption()

    # imort market settings (Data/ExoAssumption)
    instance.get_MarketSettings()

    # import zone assumptions (Data/ExoAssumption)
    instance.get_ZoneAssumption()



    # flag for iterative execution, set it false to stop looping
    bContinune = True

    '''
    while( bContinune == True):

        # first run with base year, then continue util the bContinune is false
        #_MainFunction(instance)

        inputCurrentYear = input("Current year: ")              # get the first time period of current iteration

        if inputCurrentYear in str(instance.aAllTimePeriod):    # input should be within defined time period
            instance.iCurrentYear = int(inputCurrentYear)       # update the first time period in current iteration
            # update current modelling period
            instance.aTimePeriod = io_import_instance.get_CurrentTimePeriod(instance)   # get updated time period list for current iteration
            instance.iTimePeriodOffset = io_import_instance.get_CurrentTimePeriodOffset(instance)   # the number of years offset from base year to current year
        else:
            print("Current year not in time horizon.")
            bContinune = False

    '''



