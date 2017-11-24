# -*- coding: utf-8 -*-

import time

import cls_instance

def _MainFunction(instance):

    # import external data from other module (Data/Input)
    instance.update_MUSEInput()
    print('{:f}'.format(time.time() - start_time) + " external data loaded")

    # run the models
    instance.run()



if __name__ == '__main__':

    start_time = time.time()

    # create instance and import instance configs (Data/nstanceConfig.xlsx)
    instance = cls_instance.Instance()
    print('{:f}'.format(time.time() - start_time) + " instance created")

    # import regiom assumptions (Data/ExoAssumption)
    instance.get_RegionAssumption()

    # import country assumptions (Data/ExoAssumption)
    instance.get_CountryAssumption()
    print('{:f}'.format(time.time() - start_time) + " region and country assumption loaded")

    # imort market settings (Data/ExoAssumption)
    instance.get_MarketSettings()

    # import zone assumptions (Data/ExoAssumption)
    instance.get_ZoneAssumption()
    print('{:f}'.format(time.time() - start_time) + " market and zone data loaded")

    # flag for iterative execution, set it false to stop program
    bContinune = True

    while( bContinune == True):

        # first run with base year, then continue util the bContinune is false
        _MainFunction(instance)

        sNewStartYear = input("New foresight start year: ")     # get the first time period of current iteration

        if sNewStartYear in str(instance.iAllYearSteps_YS):     # input should be within defined time period
            instance.iForesightStartYear = int(sNewStartYear)   # update the first time period in current iteration
            # update modelling year steps and start index
            instance.get_FSYearSteps()
        else:
            print("input year not in selected year steps.")
            bContinune = False





