# -*- coding: utf-8 -*-

import copy
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
    
            #--------------------------------------------------------------
            # update ancillary service requirement
            for objZone in objMarket.lsZone:
                # keep the same level for now
                objZone.fASRqrRegulation_TS_YS[:,indexYS] = objZone.fASRqrRegulation_TS_YS[:,indexYS-1]
                objZone.fASRqr10MinReserve_TS_YS[:,indexYS] = objZone.fASRqr10MinReserve_TS_YS[:,indexYS-1]
                objZone.fASRqr30MinReserve_TS_YS[:,indexYS] = objZone.fASRqr30MinReserve_TS_YS[:,indexYS-1]
                
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
                
                
            # compile(copy) a operational power generation process list
            for objZone in objMarket.lsZone:
                objZone.lsProcessOperTemp = model_util.getOperationalProcessList(objZone.lsProcess, objZone.lsProcessPlanned, iYearStep)
            
            #--------------------------------------------------------------
            # CHP investment (we assume heat does not trade cross-zone)
            
            # initial dispatch for CHP planning
            model_VI_dispatch.dispatch_Plan(instance, objMarket, indexYear)            
            
            for objZone in objMarket.lsZone:
                bFinishCHPPlanning = False
                while (not bFinishCHPPlanning):
                    
                    # dispatch CHP generation
                    model_VI_dispatch.dispatch_Init(objMarket, indexYear, "PlanMode")
                    model_VI_dispatch.dispatch_ProcessIndexListInit(instance, objMarket, indexYear, "PlanMode")
                    model_VI_dispatch.dispatch_CHP(instance, objMarket, indexYear, "PlanMode")
                    
                    # calculate the residual heat in the year
                    # model_util.updateHeatResidualDemand_Yearly(instance, objZone, indexYear)
                    
                    # select the time-slice index with lowest demand (variable part will be served with heat plant)
                    indexValleyDemandTS = np.argmin(objZone.fHeatResDemand_TS_YS[:, indexYear])
                    
                    if objZone.fHeatResDemand_TS_YS[indexValleyDemandTS, indexYear] > 0:
                        
                        # calculate the LCOE of all CHP plant (we assume the generaton only serve fixed part)
                        calAllNewCHPPlantLCOE(instance, objZone, indexValleyDemandTS, indexYear)    
                        # install the CHP plant with least LCOE
                        installNewCHP(instance, objZone, indexYear)
                    else:
                        bFinishCHPPlanning = True
                    
            #--------------------------------------------------------------
            # calculated the required renewable generation with target


            #--------------------------------------------------------------
            # install new plant to serve residual demand (include renewables)
            
            # initial dispatch for planning
            model_VI_dispatch.dispatch_Plan(instance, objMarket, indexYear)
            
            bFinishYearPlanning = False
            while (not bFinishYearPlanning):
            
                fPreInstallSystemResDemand = 0
                for objZone in objMarket.lsZone:
                    fPreInstallSystemResDemand += np.average(objZone.fPowerResDemand_TS_YS[:,indexYear])
                if fPreInstallSystemResDemand < 0.001:
                    bFinishYearPlanning = True
                    break   # break the while loop if there is not residual demand
                
                # update available transfer capacity of all connection path
                model_util_trans.updateConnectionPathAvailCapacity(instance, objMarket, indexYear)
                
                # calculate the LCOE of all plant
                calAllNewPowerPlantLCOE(instance, objMarket, indexYear)

                # install the process with least LCOE
                iZoneIdx, iProcessIdx = installNewProcess(instance, objMarket, indexYear)

                # re-dispatch
                model_VI_dispatch.dispatch_Plan(instance, objMarket, indexYear)

                # check and upgrade transmission capacity
                model_util_trans.updateTransCapacity(instance, objMarket, indexYear)

                # check all residual demand
                if checkAllDemandServed(instance, objMarket, indexYear):
                    bFinishYearPlanning = True
                    
                # remove the candidate from the list if it doesnt reduce residual demand (necessary for the algorithm)
                fPostInstallSystemResDemand = 0
                for objZone in objMarket.lsZone:
                    fPostInstallSystemResDemand += np.average(objZone.fPowerResDemand_TS_YS[:,indexYear])
                if fPostInstallSystemResDemand + 1 >= fPreInstallSystemResDemand:
                    objMarket.lsZone[iZoneIdx].lsNewProcessCandidate[iProcessIdx].fMaxAllowedNewBuildCapacity = 0
                    
                for objZone in objMarket.lsZone:
                    print(objZone.sZone,np.average(objZone.fPowerResDemand_TS_YS[:,indexYear]))
                    
                print("")

            #--------------------------------------------------------------
            # install new plant to reach ancillary service requirement
            
            # initial dispatch for planning
            model_VI_dispatch.dispatch_Plan(instance, objMarket, indexYear)      
            
            for objZone in objMarket.lsZone:
                bReachASReruirement = False
                while (not bReachASReruirement):

                    # check the deficit and install new units
                    bInstallNewUnit = checkAndInstallAncillaryService(instance, objZone, indexYear)

                    if bInstallNewUnit == True:
                        # re-dispatch
                        model_VI_dispatch.dispatch_Plan(instance, objMarket, indexYear)
                    else:
                        bReachASReruirement = True
                        break 
        
    return



def calAllNewCHPPlantLCOE(instance, objZone, indexValleyTS, indexYear):
    ''' calculate the LCOE of new CHP candidata plant '''
    
    for objNewCHPCandidate in objZone.lsNewCHPCandidate:

        if objNewCHPCandidate.Capacity > objNewCHPCandidate.fMaxAllowedNewBuildCapacity:
            # reach capacity limit
            objNewCHPCandidate.fLCOE = 9999         
        else:
            #-------------------------------------------------------
            # annual generation MWh
            fMaxGeneration = objNewCHPCandidate.fDeratedCapacity / objNewCHPCandidate.fCHPPowerToHeatRate # MW
            if fMaxGeneration > objZone.fHeatResDemand_TS_YS[indexValleyTS, indexYear]:
                # partial generation
                fMaxGeneration = objZone.fHeatResDemand_TS_YS[indexValleyTS, indexYear]
                
            fPlantTotalGeneration = np.zeros(len(instance.lsTimeSlice))   # MWh
            fPlantTotalGeneration[:] = fMaxGeneration * np.fromiter((objTimeSlice.iRepHoursInYear for objTimeSlice in instance.lsTimeSlice), float)
 
            #-------------------------------------------------------
            # annual fixed investment (MillionUSD / year)
            fNewPlantCost = objNewCHPCandidate.fAnnualFixedCost
            # total generation cost = total generation (MWh) *  unit generation cost (USD/kWh) / 1000 = M.USD
            fNewPlantCost += np.sum(fPlantTotalGeneration[:] * objNewCHPCandidate.fVariableGenCost_TS_YS[:,indexYear]) / 1000        

            # LCOE = M.USD / MWh * 1000 = USD/kWh
            if np.sum(fPlantTotalGeneration[:]) < 1:
                fLCOE = 9999
            else:
                fLCOE = fNewPlantCost / np.sum(fPlantTotalGeneration[:]) * 1000
                
            objNewCHPCandidate.fLCOE = fLCOE
                
    return



def calAllNewPowerPlantLCOE(instance, objMarket, indexYear):
    ''' calculate the LCOE of each new candidata plant (storage and CHP has removed)'''
    
    # this algorithm apply for all dispatchable and non-dispatchable power plant
    for objZone in objMarket.lsZone:

        for objNewProcessCandidate in objZone.lsNewProcessCandidate:

            if objNewProcessCandidate.Capacity > objNewProcessCandidate.fMaxAllowedNewBuildCapacity:
                # reach capacity limit
                objNewProcessCandidate.fLCOE = 9999

            elif "CHP" in objNewProcessCandidate.sProcessName:
                # exclude CHP
                objNewProcessCandidate.fLCOE = 9999
            
            elif objNewProcessCandidate.sOperationMode in ["Dispatch", "NonDispatch", "LimitDispatch"]:

                if objNewProcessCandidate.sOperationMode == "NonDispatch":
                    model_util_gen.calNonDispatchGeneration(instance, objZone, objNewProcessCandidate, indexYear)
                elif objNewProcessCandidate.sOperationMode == "LimitDispatch":
                    model_util_gen.calLimitedDispatchGeneration(instance, objZone, objNewProcessCandidate, indexYear)
                    
                fPlantTotalGeneration = np.zeros(len(instance.lsTimeSlice))   # MWh
                for indexTS, objTimeSlice in enumerate(instance.lsTimeSlice): 

                    fMaxGeneration = objNewProcessCandidate.fDeratedCapacity  # MW available dispatch volulme
                    if objNewProcessCandidate.sOperationMode in ["NonDispatch","LimitDispatch"]:
                        fMaxGeneration = objNewProcessCandidate.fHourlyPowerOutput_TS_YS[indexTS, indexYear]

                    if fMaxGeneration <= objZone.fPowerResDemand_TS_YS[indexTS, indexYear]:
                        # full dispatch
                        fPlantTotalGeneration[indexTS] += fMaxGeneration * objTimeSlice.iRepHoursInYear    # MWh
                    else:
                        # partially local dispatch
                        fPlantTotalGeneration[indexTS] += objZone.fPowerResDemand_TS_YS[indexTS, indexYear] * objTimeSlice.iRepHoursInYear
                        fMaxGeneration = fMaxGeneration - objZone.fPowerResDemand_TS_YS[indexTS, indexYear]

                        # calculate max export to all neighbor subregion
                        fMaxExportTS = 0
                        for iPathIndex, objConnPath in enumerate(objZone.lsConnectPath): 
                            if objConnPath.fAvailTransCapacity_TS[indexTS] > 0:
                                fDestZoneNodalPrice = objMarket.lsZone[objConnPath.iDestZoneIndex].fNodalPrice_TS_YS[indexTS, indexYear]
                                if fDestZoneNodalPrice > objNewProcessCandidate.fVariableGenCost_TS_YS[indexTS, indexYear]:
                                    fMaxExportTS += objConnPath.fAvailTransCapacity_TS[indexTS]

                        fExport = min(fMaxExportTS, fMaxGeneration)
                        fPlantTotalGeneration[indexTS] += fExport * objTimeSlice.iRepHoursInYear    # MWh
                        fMaxGeneration = fMaxGeneration - fExport
                        
                        '''
                        # dispatch the rest part if the generation cost is lower than nodal price
                        if fMaxGeneration > 0:
                            if objNewProcessCandidate.fVariableGenCost_TS_YS[indexTS, indexYear] < objZone.fNodalPrice_TS_YS[indexTS, indexYear]:
                                fPlantTotalGeneration[indexTS] += fMaxGeneration * objTimeSlice.iRepHoursInYear    # MWh
                        '''
                                
                #-------------------------------------------------------
                # annual fixed investment (MillionUSD / year)
                fNewPlantCost = objNewProcessCandidate.fAnnualFixedCost
                # total generation cost = total generation (MWh) *  unit generation cost (USD/kWh) / 1000 = M.USD
                fNewPlantCost += np.sum(fPlantTotalGeneration[:] * objNewProcessCandidate.fVariableGenCost_TS_YS[:,indexYear]) / 1000 

                # LCOE = M.USD / MWh * 1000 = USD/kWh
                if np.sum(fPlantTotalGeneration[:]) < 1:
                    fLCOE = 9999
                else:
                    fLCOE = fNewPlantCost / np.sum(fPlantTotalGeneration[:]) * 1000

                    # take into account the back-up cost of non-dispatchable plant
                    if objNewProcessCandidate.sOperationMode == "NonDispatch":
                        # calculate the change of the disparity of peak and flat demand after install the new non-dispatchable plant
                        # find peak and flat demand
                        indexPeakDemand = np.argmax(objZone.fPowerResDemand_TS_YS[:, indexYear])
                        indexValleyDemand = np.argmin(objZone.fPowerResDemand_TS_YS[:, indexYear])
                        iPeakOutput = objNewProcessCandidate.fHourlyPowerOutput_TS_YS[indexPeakDemand,indexYear]
                        iValleyOutput = objNewProcessCandidate.fHourlyPowerOutput_TS_YS[indexValleyDemand,indexYear]
                        fPositiveDisparity = iPeakOutput - iValleyOutput  # MW
                        if fPositiveDisparity < 0:
                            # get the cheapest back-up plant cost
                            fBackUpCost = 99999
                            for indexP, objNewPlant in enumerate(objZone.lsNewProcessCandidate):
                                if objNewPlant.sOperationMode == "Dispatch" and objNewPlant.fAnnualFixedCostPerMW < fBackUpCost:
                                    fBackUpCost = objNewPlant.fAnnualFixedCostPerMW
                            # USD/KW * MW * 1000 = USD
                            fBackUpCost = fBackUpCost * (-fPositiveDisparity) * 1000
                            # USD / MWh / 1000 = USD/kWh
                            fLCOE += fBackUpCost / np.sum(fPlantTotalGeneration[:]) / 1000

                objNewProcessCandidate.fLCOE = fLCOE

            elif objNewProcessCandidate.sOperationMode == "Storage":
                # consider new storage only when residual demand is 0 in more than half of the TS
                iZeroDemandTSCount = 0
                for indexTS, objTimeSlice in enumerate(instance.lsTimeSlice): 
                    if objZone.fPowerResDemand_TS_YS[indexTS, indexYear] < 1:
                        iZeroDemandTSCount = iZeroDemandTSCount + 1
                if iZeroDemandTSCount <= len(instance.lsTimeSlice) / 2 or iZeroDemandTSCount == len(instance.lsTimeSlice): 
                    objNewProcessCandidate.fLCOE = 9999
                else:
                    objNewProcessCandidate.fLCOE = _calHPSOperationLCOE(instance, objMarket, objZone, objNewProcessCandidate, indexYear)

    return



def _calHPSOperationLCOE(instance, objMarket, objZone, objProcess, indexYear):
    ''' calculate hydro-pump storage operation and LCOE '''

    model_util_gen.calHPSOperation(instance, objZone, objProcess, indexYear)

    # calculate LCOE
    fOperationProfit = 0
    for indexTS, objTimeSlice in enumerate(instance.lsTimeSlice): 
        # total generation (MWh) *  unit generation cost (USD/kWh) / 1000 = M.USD
        fOperationProfit += objProcess.fHourlyPowerOutput_TS_YS[indexTS, indexYear] * objTimeSlice.iRepHoursInYear * \
        objZone.fNodalPrice_TS_YS[indexTS,indexYear] / 1000

    fLCOE = objProcess.fAnnualFixedCost + fOperationProfit
    fLCOE = 9999 if fLCOE < 0 else fLCOE

    return fLCOE



def installNewCHP(instance, objZone, indexYear):
    ''' install new CHP '''
    
    iPlantIndex = -1
    fLowestLCOE = 9999
    for indexPlant, objNewPlantCandidate in enumerate(objZone.lsNewCHPCandidate):
        if objNewPlantCandidate.fLCOE < fLowestLCOE:
            iPlantIndex = indexPlant
            fLowestLCOE = objNewPlantCandidate.fLCOE

    if iPlantIndex != -1:
        
        print("install CHP", indexYear, objZone.sZone, objZone.lsNewCHPCandidate[iPlantIndex].sProcessName, \
              objZone.lsNewCHPCandidate[iPlantIndex].Capacity)   
                
        installNewPlant(instance, objZone, objZone.lsNewCHPCandidate[indexPlant], indexYear)
        return True
    else:
        return False



def installNewProcess(instance, objMarket, indexYear):
    ''' install new Process '''
    
    iLCOEZoneIdx = 0
    iProcessIndex = -1
    fLowestLCOE = 9999
    for iZoneIndex, objZone in enumerate(objMarket.lsZone):
        for indexPlant, objNewPlantCandidate in enumerate(objZone.lsNewProcessCandidate):
            if objNewPlantCandidate.fLCOE < fLowestLCOE:
                iLCOEZoneIdx = iZoneIndex
                iProcessIndex = indexPlant
                fLowestLCOE = objNewPlantCandidate.fLCOE

    if iProcessIndex != -1:
        objZone = objMarket.lsZone[iLCOEZoneIdx]
        
        
        print("install LCOE", indexYear, objZone.sZone, objZone.lsNewProcessCandidate[iProcessIndex].sProcessName, \
              objZone.lsNewProcessCandidate[iProcessIndex].Capacity, objZone.lsNewProcessCandidate[iProcessIndex].fLCOE)
        
        
        installNewPlant(instance, objZone, objZone.lsNewProcessCandidate[iProcessIndex], indexYear)
        
    return iLCOEZoneIdx, iProcessIndex



def installNewPlant(instance, objZone, objCandidate, indexYear):
    ''' install the new plant '''

    # change fMaxAllowedNewBuildCapacity
    objCandidate.fMaxAllowedNewBuildCapacity -= objCandidate.Capacity

    # copy the plant to objZone.lsProcessPlanned and objZone.lsProcessOperTemp. Combine the plants with same tech and commit time.
    bCombinExist = False
    for indexP, objPlant in enumerate(objZone.lsProcessPlanned):
        if objPlant.sProcessName == objCandidate.sProcessName and objPlant.CommitTime == objCandidate.CommitTime:
            # update plant in objZone.lsProcessPlanned
            objPlant.Capacity += objCandidate.Capacity
            objPlant.fAnnualCapex += objCandidate.fAnnualCapex
            objPlant.fAnnualFixedCost += objCandidate.fAnnualFixedCost
            objPlant.fDeratedCapacity += objCandidate.fDeratedCapacity
            # update plant in objZone.lsProcessOperTemp
            for indexPlantTemp, objPlantTemp in enumerate(objZone.lsProcessOperTemp):
                if objPlantTemp.sProcessName == objCandidate.sProcessName and objPlantTemp.CommitTime == objCandidate.CommitTime:
                    objPlantTemp.Capacity += objCandidate.Capacity
                    objPlantTemp.fAnnualCapex += objCandidate.fAnnualCapex
                    objPlantTemp.fAnnualFixedCost += objCandidate.fAnnualFixedCost
                    objPlantTemp.fDeratedCapacity += objCandidate.fDeratedCapacity
                    break
            bCombinExist = True
            break
        
    if bCombinExist is False:
        objZone.lsProcessPlanned.append(copy.deepcopy(objCandidate))
        objZone.lsProcessOperTemp.append(copy.deepcopy(objCandidate))
        
    return
    
    

def checkAllDemandServed(instance, objMarket, indexYear):
    ''' check all residual demand '''
    
    bAllDemandServed = True
    for objZone in objMarket.lsZone:
        for indexTS, objTimeSlice in enumerate(instance.lsTimeSlice):
            if objZone.fPowerResDemand_TS_YS[indexTS, indexYear] > 1:
                bAllDemandServed = False
                break

    return bAllDemandServed



def checkAndInstallAncillaryService(instance, objZone, indexYear):
    ''' check the deficit and install new units '''

    fMaxDefRegulationPerM = np.max(objZone.fASDfcRegulation_TS_YS[:, indexYear]) * 2  # 30 second regulation
    fMaxDef10MinReservePerM = np.max(objZone.fASDfc10MinReserve_TS_YS[:, indexYear]) / 10  # 10 second regulation
    fMaxDef30MinReservePerM = np.max(objZone.fASDfc30MinReserve_TS_YS[:, indexYear]) / 30  # 30 second regulation

    # sort variable generation cost of the day (by the first timeslice of the day)
    objZone.lsNewProcessCandidate = sorted(objZone.lsNewProcessCandidate, key=lambda lsNewProcessCandidate: lsNewProcessCandidate.RampRatePerM, reverse=True)

    indexNewInstall = -1
    for indexProcess, objNewProcess in enumerate(objZone.lsNewProcessCandidate):
        if objNewProcess.fMaxAllowedNewBuildCapacity > objNewProcess.Capacity:
            if fMaxDefRegulationPerM > 0.001:
                # exclude nuclear and CHP for regulation
                if "NUK" not in objNewProcess.sProcessName and "CHP" not in objNewProcess.sProcessName:
                    indexNewInstall = indexProcess
                        
            elif fMaxDef10MinReservePerM > 0.001:
                # exclude nuclear and CHP for regulation
                if "NUK" not in objNewProcess.sProcessName and "CHP" not in objNewProcess.sProcessName:
                    indexNewInstall = indexProcess
                        
            elif fMaxDef30MinReservePerM > 0.001:
                # exclude nuclear and CHP for regulation
                if "CHP" not in objNewProcess.sProcessName:
                    indexNewInstall = indexProcess
            if indexNewInstall != -1:
                break
                
    if indexNewInstall != -1:
        
        print("DM", indexYear, objZone.sZone, np.average(objZone.fPowerOutput_TS_YS[:, indexYear]), np.average(objZone.fPowerResDemand_TS_YS[:, indexYear]))
        print("Res AS", indexYear, objZone.sZone, fMaxDefRegulationPerM, fMaxDef10MinReservePerM, fMaxDef30MinReservePerM)
        
        print("install AS", indexYear, objZone.sZone, objZone.lsNewProcessCandidate[indexNewInstall].sProcessName, \
              objZone.lsNewProcessCandidate[indexNewInstall].Capacity)
        
        installNewPlant(instance, objZone, objZone.lsNewProcessCandidate[indexNewInstall], indexYear)
        bInstallNewUnit = True
    else:
        bInstallNewUnit = False

    return bInstallNewUnit



