# -*- coding: utf-8 -*-


import model_util
import model_util_trans
import model_VI_dispatch
import model_VI_plan
import model_solution_main

class Market:
    """ create an region object  """

    def __init__(self, Market):
        self.sMarket = Market
        self.lsZone = list()                    # a list of zone objects in this market
        self.lsGenCo = list()                   # a list of generation companies in this market
        self.lsTransmission = list()            # a list of zone objects in this market
        self.lsDispatchProcessIndex = list() # a list all dispatchable plants in the market (key information) index to zone.lsProcess
        self.MarketOutput = MarketOutput()
        
        ''' assumptions '''
        # fRegulationRequire_YS
        # f10mReserve_YS
        # f30mReserve_YS
        # fCO2EmissionLimit_YS        
        
        return


    def modelrun_VI(self, instance):
        """ run vertical integrated system model """
        
        print("VI model run")
        
        # model initiation (create variables)
        model_util.model_fisrt_Init(self, instance)
        
        # model initiation
        model_util.model_iter_Init(self, instance)
        
        # construct transmission
        iHopLimit = 2
        model_util_trans.constructTrans(self, instance, iHopLimit)
        
        # zone process initiation and calculate variable generation cost
        model_util.processVarCost_Init_model(self, instance)
                
        # base year dispatch
        model_VI_dispatch.dispatch_Main(self, instance, instance.iFSBaseYearIndex)
        
        # future investment
        model_VI_plan.calInvestmentPlanning(self, instance)
        
        # final dispatch
        for indexTS, iYearStep in enumerate(instance.iAllYearSteps_YS):
            if iYearStep > instance.iForesightStartYear:    # loop for each time step from next time step
                for objZone in self.lsZone:
                    objZone.lsProcessOperTemp = model_util.getOperationalProcessList_ShallowCopy(objZone.lsProcess, objZone.lsProcessPlanned, iYearStep)
                model_VI_dispatch.dispatch_Plan(instance, self, indexTS)
        
        print(" model run completed")
        
        # save modelling result
        self.ResultOutput(instance)
        
        return
  
    
    def modelrun_WM(instance):
        """ run wholesale market model """
        
        print("WM model run")
        
        return


    def ResultOutput(self, instance):
        """ # save the model result to instance (for next iteration) and files """
        
        model_solution_main.updateZoneSolution(instance, self)
        model_solution_main.updateMarketSolution(instance, self)
        '''
        model_util_output.outputZoneSolution(instance, self)
        model_util_output.outputMarketSolution(instance, self)
        model_util_output.outputCountrySolution(instance, self)
        model_util_output.outputRegionSolution(instance, self)
        '''
        print(" model output finish")
        
        return


class MarketOutput:

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
        self.dicTransCapacity_YS_TR = {}
        self.dicTransNewCapacity_YS_TR = {}
        self.dicTransUsage_YS_TS_TR = {}
        self.dicTransCAPEX_YS_TR = {}
        self.dicTransOPEX_YS_TR = {}

        ##### model endogenous output

        self.dicMarketPowerGen_YS_TS = {}
        self.dicMarketHeatGen_YS_TS = {}
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



