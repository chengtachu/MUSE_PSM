# -*- coding: utf-8 -*-


class Zone:
    """ create an country object  """

    def __init__(self, Zone):
        self.sZone = Zone
        self.iRegionIndex = 0
        self.iCountryIndex = 0
        self.iMarketIndex = 0
        self.lsProcessAssump = list()       # a list of process assumption in this zone
        self.lsProcess = list()             # a list of exist process in current modelling
        self.lsProcessPlanned = list()       # a list of planned process
        self.lsProcessDecomm = list()       # a list of decommited process
        self.lsProcessOperTemp = list()     # a list of temporate processes for planning
        self.lsCHPProcessIndex = list()     # a list of index to dispatchable CHP process
        self.lsConnectPath = list()
        self.lsNewProcessCandidate = list() # new power plant technology candidate list only for capacity plannign/investment simulation
        self.lsNewStorageCandidate = list() # new storage technology candidate list only for capacity plannign/investment simulation
        self.lsNewCHPCandidate = list()     # new CHP technology candidate list only for capacity plannign/investment simulation
        self.fMarginalGenCost_TS_YS = None
        self.fNodalPrice_TS_YS = None
        self.ZoneOutput = ZoneOutput()
        
        ''' assumptions '''
        # fPowerDistLossRate_YS         # %
        # fHeatDistLossRate_YS          # %          
        # fPowerDemand_TS_YS            # MW
        # fHeatDemand_TS_YS             # GJ/h
        # fCrossMarketPowerImport_TS_YS # MW
        
        # fMaxCapacity_YS               # MW
        # fMaxBuildRate_YS              # MW
            
        # aReWindOutput2025_TS          # %
        # aReWindOutput40UP_TS          # %
        # aReOffWindOutput2025_TS       # %
        # aReOffWindOutput50UP_TS       # %
        
        # aRePVOutput_TS                # %
        # aReHydroOutput_TS             # %
        
        ''' variables '''
        # fPowerOutput_TS_YS            # (MW) power output at the time-slice 
        # fPowerResDemand_TS_YS         # (MW) residulal power demand at the time-slice    
        # fHeatOutput_TS_YS             # (MW) power output at the time-slice
        # fHeatResDemand_TS_YS          # (MW) residulal heat demand at the time-slice  
        
        # fASRqrRegulation_TS_YS        # MW required regulation ability
        # fASRqr10MinReserve_TS_YS      # MW required reserve for 10 minutes
        # fASRqr30MinReserve_TS_YS      # MW required reserve for 30 minutes
        # fASDfcRegulation_TS_YS        # MW deficit regulation ability
        # fASDfc10MinReserve_TS_YS      # MW deficit reserve for 10 minutes
        # fASDfc30MinReserve_TS_YS      # MW deficit reserve for 30 minutes
        
        return


class ZoneOutput:

    def __init__(self):

        ##### model variable output

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

        ##### model endogenous output

        self.dicZonePowerOutput_YS_TS = {}
        self.dicZonePowerGen_YS_TS = {}
        self.dicZoneHeatOutput_YS_TS = {}
        self.dicZoneHeatGen_YS_TS = {}
        self.dicProcessLCOE_YS_PR = {}
        self.dicPowerGenCost_YS_TS = {}
        self.dicPowerWholeSalePrice_YS_TS = {}

        self.dicCO2Emission_YS = {}
        self.dicCO2Emission_YS_TS = {}
        self.dicEmissionCaptured_YS_TS = {}
        self.dicFuelConsum_YS_TS_CM = {}       

        '''
        ##### ABM model
        self.dicDAMNodalPrice_YS_TS = {}
        self.dicRTMNodalPrice_YS_TS = {}
        '''

        return





