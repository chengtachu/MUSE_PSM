# -*- coding: utf-8 -*-




def model_Init(objMarket, instance):
    ''' market initiation '''
    
    # first time to run of the model (base year, and no output)
    if instance.iForesightStartYear == instance.iBaseYear and objMarket.Output.dicGenCapacity_YR_TC == {} :

        # initiate subregion plants and parameters
        #_subregionSimInit(instance, objRegion)
        # initial transmission cost
        #model_sim_util.initialTransmissionCost(instance, objRegion)

        print("")

    return




