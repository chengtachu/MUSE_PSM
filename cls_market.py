# -*- coding: utf-8 -*-


import model_util
import model_util_trans
import model_VI_dispatch
import model_VI_plan

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
        
            # update ancillary service requirement
        
        
        # save modelling result
        
        
        return
  
    
    def modelrun_WM(instance):
        """ run wholesale market model """
        
        print("WM model run")
        
        return



class MarketOutput:

    def __init__(self):

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

        ## transmission
        self.dicTransCapacity_YR_TR = {}
        self.dicTransNewCapacity_YR_TR = {}
        self.dicTransUsage_YR_TS_TR = {}
        self.dicTransCAPEX_YR_TR = {}
        self.dicTransOPEX_YR_TR = {}

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
        self.dicGeneratorProfit_YR_GR = {}
        self.dicGeneratorCapacity_YR_TC_GR = {}

        return



