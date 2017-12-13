# -*- coding: utf-8 -*-

import numpy as np

import model_util
import model_util_gen
import model_util_trans
import model_VI_dispatch

def calInvestmentPlanning(objMarket, instance):
    ''' investment planning of VI model '''
    
    # empty the future plant list, for a new planning iteration later (because this iteration will produce new list)
    for objZone in objMarket.lsZone:
        objZone.lsProcessPlanned = list()

    for indexYS, iYearStep in enumerate(instance.iFSYearSteps_YS):
        
        # get the year index
        if iYearStep > instance.iForesightStartYear:
            indexYear = indexYS + instance.iFSBaseYearIndex
    
            # update ancillary service requirement
    
            # CHP investment
    
            # generate zonal price projection (using the same capacity mix but new fuel and carbon cost)
    
            #--------------------------------------------------------------
            # creat candidate new technology plant list
            for objZone in objMarket.lsZone:

                # creat candidate new technology plant list
                objZone.lsNewProcessCandidate = model_util.getNewProcessCandidate(instance, objZone, indexYear)
                lsProcessCandidate = objZone.lsNewProcessCandidate
                # initialize attributes
                model_util.createProcessVar(instance, lsProcessCandidate)
                # calculate fixed cost of each technology
                model_util.ZoneProcess_Init(lsProcessCandidate)
                # calculate generation cost of each technology
                model_util.processVarCost_Init(instance, objMarket, objZone, lsProcessCandidate)
                
                # total allowed new build capacity according to capacity constraints
                model_util.getNewBuildCapacityLimit(instance, objZone, objZone.lsProcess, objZone.lsProcessPlanned, lsProcessCandidate, indexYear)
                
                # separate storage candidate technology
                objZone.lsNewStorageCandidate = model_util.getNewStorageCandidate(lsProcessCandidate)
                # separate CHP candidate technology
                objZone.lsNewCHPCandidate = model_util.getNewCHPCandidate(lsProcessCandidate)
                
            # compile(copy) a operational process list
            for objZone in objMarket.lsZone:
                objZone.lsProcessOperTemp = model_util.getOperationalProcessList(objZone.lsProcess, objZone.lsProcessPlanned, iYearStep)
                
            # initial dispatch for planning
            model_VI_dispatch.dispatch_Plan(instance, objMarket, indexYear)
            
            
            #--------------------------------------------------------------
            # calculated the required renewable generation with target
            # capacity planning for renewable (LCOE)
            #bRenewableTargetPlanning = False
            #while (not bRenewableTargetPlanning):
            
                # update available transfer capacity of all connection path

                # calculate the LCOE of renewables

                # install the new plant with lowest LCOE (add to objSubregion.listGenPlantFuture and objSubregion.listGenPlantOperTemp)

                # re-dispatch

                # check transmission line and update

                # calculate all renewable generation level
            
                # biomass(?)
            
            
            #--------------------------------------------------------------
            # install new plant to serve residual demand (include renewables)
            bFinishYearPlanning = False
            while (not bFinishYearPlanning):
            
                # update available transfer capacity of all connection path
                model_util_trans.updateConnectionPathAvailCapacity(instance, objMarket, iYearStep)
                
                # calculate the LCOE of all plant
                calAllNewPlantLCOE(instance, objMarket, iYearStep)

                # install the new plant with lowest LCOE (add to objSubregion.listGenPlantFuture and objSubregion.listGenPlantOperTemp)


                # re-dispatch


                # check transmission line and update


                # check all residual demand

                
                
            #--------------------------------------------------------------
            # install new plant to reach ancillary service requirement
                
            
            
            #--------------------------------------------------------------
            # remove over investment
            
            
            print("")

    return



def calAllNewPlantLCOE(instance, objMarket, indexYear):
    ''' calculate the LCOE of each new candidata plant '''
    
    # this algorithm apply for all dispatchable and non-dispatchable plant
    for objZone in objMarket.lsZone:

        for objNewProcessCandidate in objZone.lsNewProcessCandidate:

            if objNewProcessCandidate.Capacity > objNewProcessCandidate.fMaxAllowedNewBuildCapacity:
                # reach capacity limit
                objNewProcessCandidate.fLCOE = 9999

            elif objNewProcessCandidate.sOperationMode == "Dispatch" or objNewProcessCandidate.sOperationMode == "NonDispatch":

                if objNewProcessCandidate.sOperationMode == "NonDispatch":
                    model_util_gen.calNonDispatchGeneration(instance, objZone, objNewProcessCandidate, indexYear)

                fPlantTotalGeneration = 0   # MW
                for indexTS, objTimeSlice in enumerate(instance.listTimeSlice):

                    fMaxGeneration = objNewPlantCandidate.fDeratedCapacity  # MW
                    if objNewPlantCandidate.sOperationMode == "NonDispatch":
                        fMaxGeneration = objNewPlantCandidate.fHourNetGeneration_TS_YR[indexTS, indexYear]

                    if fMaxGeneration <= objZone.aResidualDemand_TS_YR[indexTS, indexYear]:
                        # full dispatch
                        fPlantTotalGeneration += fMaxGeneration * objTimeSlice.RepresentHours    # MWh
                    else:
                        # partially local dispatch
                        fPlantTotalGeneration += objZone.aResidualDemand_TS_YR[indexTS, indexYear] * objTimeSlice.RepresentHours
                        fMaxGeneration = fMaxGeneration - objZone.aResidualDemand_TS_YR[indexTS, indexYear]

                        # calculate max export to all neighbor subregion
                        fMaxExportTS = 0
                        for iPathIndex, objConnPath in enumerate(objZone.listConnectPath): 
                            if objConnPath.fAvailTransCapacity[indexTS] > 0:
                                fDestSubregionNodalPrice = instance.listSubregionObjs[objConnPath.iDestSubregionIndex].aNodalPrice_TS_YR[indexTS, indexYear]
                                if fDestSubregionNodalPrice > objNewPlantCandidate.fGenCostPerUnit_YR[indexYear]:
                                    fMaxExportTS += objConnPath.fAvailTransCapacity[indexTS]

                        fExport = min(fMaxExportTS, fMaxGeneration)
                        fPlantTotalGeneration += fExport * objTimeSlice.RepresentHours    # MWh
                        
                        if fMaxGeneration > 0:
                            if objNewPlantCandidate.fGenCostPerUnit_YR[indexYear] < objZone.aNodalPrice_TS_YR[indexTS, indexYear]:
                                fPlantTotalGeneration += fMaxGeneration * objTimeSlice.RepresentHours    # MWh
                        
                # annual fixed investment (MillionUSD / year)
                fNewPlantCost = objNewPlantCandidate.fAnnualFixedCost
                # total generation cost = total generation (MWh) *  unit generation cost (USD/kWh) / 1000 = M.USD
                fNewPlantCost += fPlantTotalGeneration * objNewPlantCandidate.fGenCostPerUnit_YR[indexYear] / 1000

                # LCOE = M.USD / MWh * 1000 = USD/kWh
                if fPlantTotalGeneration < 1:
                    fLCOE = 9999
                else:
                    fLCOE = fNewPlantCost / fPlantTotalGeneration * 1000

                    # take into account the back-up cost of non-dispatchable plant
                    if objNewPlantCandidate.sOperationMode == "NonDispatch":
                        # calculate the change of the disparity of peak and flat demand after install the new non-dispatchable plant
                        # find peak and flat demand
                        indexPeakDemand = np.argmax(objZone.aResidualDemand_TS_YR[:, indexYear])
                        indexFlatDemand = np.argmin(objZone.aResidualDemand_TS_YR[:, indexYear])
                        iPeakOutput = objNewPlantCandidate.fHourNetGeneration_TS_YR[indexPeakDemand,indexYear]
                        iFlatOutput = objNewPlantCandidate.fHourNetGeneration_TS_YR[indexFlatDemand,indexYear]
                        fPositiveDisparity = iPeakOutput - iFlatOutput  # MW
                        if fPositiveDisparity < 0:
                            # get the cheapest back-up plant cost
                            fBackUpCost = 99999
                            for indexP, objNewPlant in enumerate(objZone.listNewPlantCandidate):
                                if objNewPlant.sOperationMode == "Dispatch" and objNewPlant.fAnnualFixedCostPerMW < fBackUpCost:
                                    fBackUpCost = objNewPlant.fAnnualFixedCostPerMW
                            # USD/KW * MW * 1000 = USD
                            fBackUpCost = fBackUpCost * (-fPositiveDisparity) * 1000
                            # USD / MWh / 1000 = USD/kWh
                            fLCOE += fBackUpCost / fPlantTotalGeneration / 1000

                objNewPlantCandidate.fLCOE = fLCOE

            elif objNewPlantCandidate.sOperationMode == "Storage":
                # consider new storage only when residual demand is 0 in more than half of the TS
                iZeroDemandTSCount = 0
                for indexTS, objTimeSlice in enumerate(instance.listTimeSlice):
                    if objZone.aResidualDemand_TS_YR[indexTS, indexYear] < 1:
                        iZeroDemandTSCount = iZeroDemandTSCount + 1
                if iZeroDemandTSCount <= len(instance.listTimeSlice) / 2 or iZeroDemandTSCount == len(instance.listTimeSlice): 
                    objNewPlantCandidate.fLCOE = 9999
                else:
                    objNewPlantCandidate.fLCOE = _calHPSOperationLCOE(instance, objMarket, objSubregion, objNewPlantCandidate, indexYear)

    return




