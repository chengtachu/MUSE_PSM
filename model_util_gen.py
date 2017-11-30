# -*- coding: utf-8 -*-



def calNonDispatchGeneration(instance, objZone, objProcess, indexYS):
    ''' calculate non-dispatchable process hourly generation '''
    
    if "REW_WND_ON" in objProcess.sProcessName:
        if objProcess.sProcessName == "REW_WND_ON_2025":
            objProcess.fHourlyPowerOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReWindOutput2025_TS[:] / 100
        elif objProcess.sProcessName == "REW_WND_ON_2530":
            objProcess.fHourlyPowerOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReWindOutput2530_TS[:] / 100
        elif objProcess.sProcessName == "REW_WND_ON_3035":
            objProcess.fHourlyPowerOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReWindOutput3035_TS[:] / 100
        elif objProcess.sProcessName == "REW_WND_ON_3540":
            objProcess.fHourlyPowerOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReWindOutput3540_TS[:] / 100
        elif objProcess.sProcessName == "REW_WND_ON_40UP":
            objProcess.fHourlyPowerOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReWindOutput40UP_TS[:] / 100

    elif "REW_WND_OFF" in objProcess.sProcessName:
        if objProcess.sProcessName == "REW_WND_OFF_2025":
            objProcess.fHourlyPowerOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReOffWindOutput2025_TS[:] / 100
        elif objProcess.sProcessName == "REW_WND_OFF_2530":
            objProcess.fHourlyPowerOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReOffWindOutput2530_TS[:] / 100
        elif objProcess.sProcessName == "REW_WND_OFF_3035":
            objProcess.fHourlyPowerOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReOffWindOutput3035_TS[:] / 100
        elif objProcess.sProcessName == "REW_WND_OFF_3540":
            objProcess.fHourlyPowerOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReOffWindOutput3540_TS[:] / 100
        elif objProcess.sProcessName == "REW_WND_OFF_4045":
            objProcess.fHourlyPowerOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReOffWindOutput4045_TS[:] / 100
        elif objProcess.sProcessName == "REW_WND_OFF_4550":
            objProcess.fHourlyPowerOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReOffWindOutput4550_TS[:] / 100
        elif objProcess.sProcessName == "REW_WND_OFF_50UP":
            objProcess.fHourlyPowerOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReOffWindOutput50UP_TS[:] / 100

    elif objProcess.sProcessName in ["REW_PV_UTI","REW_PV_RFT"] :
        objProcess.fHourlyPowerOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aRePVOutput_TS[:] / 100

    elif "CSP" in objProcess.sProcessName:
        objProcess.fHourlyPowerOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aRePVOutput_TS[:] * 1.1 / 100

    # assume geothermal is 80% of all time
    elif "REW_GEO" in objProcess.sProcessName:
        objProcess.fHourlyPowerOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * 0.8

    # small hydro (non-dispatchable)
    elif "REW_HYD_SM" in objProcess.sProcessName:
        objProcess.fHourlyPowerOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReHydroOutput_TS[:] / 100
        
    return



def calLimitedDispatchGeneration(instance, objZone, objProcess, indexYS):
    ''' calculate non-dispatchable process hourly generation '''

    # dispatch hydro to fit load shape
    if "REW_HYD_LG" in objProcess.sProcessName in ["REW_HYD_LG"]:
        # find the day time slice
        lsDayTimeSlice = list(instance.lsDayTimeSlice)
        for indexDay, objDay in enumerate(lsDayTimeSlice):
            # get avg CF in a day (get the first time slice)
            fDayCF =  objZone.aReHydroOutput_TS[objDay.lsDiurnalTS[0].iTimeSliceIndex] / 100
            # adjust CF according to residual demand
            fTotalDemand = 0
            for indexTS, objDayTS in enumerate(objDay.lsDiurnalTS):
                fTotalDemand += objZone.fPowerDemand_TS_YS[objDayTS.iTimeSliceIndex, indexYS]
            fAvgDayDemand = fTotalDemand / len(objDay.lsDiurnalTS)

            for indexTS, objDayTS in enumerate(objDay.lsDiurnalTS):
                objProcess.fHourlyPowerOutput_TS_YS[objDayTS.iTimeSliceIndex, indexYS] = objProcess.fDeratedCapacity * fDayCF \
                * objZone.fPowerDemand_TS_YS[objDayTS.iTimeSliceIndex, indexYS] / fAvgDayDemand

    return



def updatePowerResidualDemand_Yearly(instance, objMarket, indexYS):
    ''' update power residual demand '''

    for indexZone, objZone in enumerate(objMarket.lsZone):
        objZone.fPowerResDemand_TS_YS[:,indexYS] = objZone.fPowerDemand_TS_YS[:,indexYS] \
        - objZone.fPowerOutput_TS_YS[:,indexYS] - objZone.fPowerImport_TS_YS[:,indexYS]
        
        objZone.fPowerResDemand_TS_YS[ objZone.fPowerResDemand_TS_YS[:,indexYS] < 0 ,indexYS] = 0

    return



def calHPSOperation(instance, objZone, objProcess, indexYS):
    ''' calculate hydro pump storage operation '''

    lsDayTimeSlice = list(instance.lsDayTimeSlice)
    for indexDay, objDay in enumerate(lsDayTimeSlice):

        fDayStorageOutput = objProcess.fDeratedCapacity * 6                     # MW -> MWh (assume ouput as 6 hour equivilent capacity every day)
        fDayStorageInput = fDayStorageOutput / (objProcess.EffPowerCM / 100)    # MWh
       
        fTotalResidualDemand = 0

        # local residual demand
        for indexTS, objDayTS in enumerate(objDay.lsDiurnalTS):
            fLocalResidualDemand = objZone.fPowerResDemand_TS_YS[objDayTS.iTimeSliceIndex, indexYS]
            objDayTS.fValue = fLocalResidualDemand
            fTotalResidualDemand += fLocalResidualDemand * objDayTS.iRepHoursInDay

        fAvgResidualDemand = fTotalResidualDemand / 24

        if fAvgResidualDemand < 1:
            objProcess.fHourlyPowerOutput_TS_YS[objDayTS.iTimeSliceIndex, indexYS] = 0
        else:
        # calculate intra-day operation - output
            intradayTS = objDay.lsDiurnalTS
            intradayTS = sorted(intradayTS, key=lambda intradayTS: intradayTS.fValue, reverse=True) # sort desc by residual demand
            for indexTS, objDayTS in enumerate(intradayTS):

                if objDayTS.fValue - objProcess.fDeratedCapacity >= fAvgResidualDemand:
                    # full generate (cut off at average)
                    if fDayStorageOutput > objProcess.fDeratedCapacity * objDayTS.iRepHoursInDay:
                        # full generation hour, the max output is its derated capacity
                        objProcess.fHourlyPowerOutput_TS_YS[objDayTS.iTimeSliceIndex, indexYS] = objProcess.fDeratedCapacity
                        fDayStorageOutput -= objProcess.fDeratedCapacity * objDayTS.iRepHoursInDay
                    else:
                        # partially generatoin (cut off at all demand served)
                        objProcess.fHourlyPowerOutput_TS_YS[objDayTS.iTimeSliceIndex, indexYS] = fDayStorageOutput / objDayTS.iRepHoursInDay
                        fDayStorageOutput = 0
                        break
                elif objDayTS.fValue > fAvgResidualDemand and (objDayTS.fValue - fAvgResidualDemand) < objProcess.fDeratedCapacity:
                    # partially generatoin (cut off at average)
                    if fDayStorageOutput > (objDayTS.fValue - fAvgResidualDemand) * objDayTS.iRepHoursInDay:
                        # full generation hour, the max output is its derated capacity
                        objProcess.fHourlyPowerOutput_TS_YS[objDayTS.iTimeSliceIndex, indexYS] = (objDayTS.fValue - fAvgResidualDemand)
                        fDayStorageOutput -= (objDayTS.fValue - fAvgResidualDemand) * objDayTS.iRepHoursInDay
                    else:
                        # partially generatoin (cut off at all demand served)
                        objProcess.fHourlyPowerOutput_TS_YS[objDayTS.iTimeSliceIndex, indexYS] = fDayStorageOutput / objDayTS.iRepHoursInDay
                        fDayStorageOutput = 0
                        break

            # calculate intra-day operation - input
            intradayTS = sorted(intradayTS, key=lambda intradayTS: intradayTS.fValue)   # sort asc by residual demand
            for indexTS, objDayTS in enumerate(intradayTS):

                if fAvgResidualDemand - objProcess.fDeratedCapacity >= objDayTS.fValue:
                    # full generate (cut off at average)
                    if fDayStorageInput > objProcess.fDeratedCapacity * objDayTS.iRepHoursInDay:
                        # full generation hour
                        objProcess.fHourlyPowerOutput_TS_YS[objDayTS.iTimeSliceIndex, indexYS] = - objProcess.fDeratedCapacity
                        fDayStorageInput -= objProcess.fDeratedCapacity * objDayTS.iRepHoursInDay
                    else:

                        objProcess.fHourlyPowerOutput_TS_YS[objDayTS.iTimeSliceIndex, indexYS] = - (fDayStorageInput / objDayTS.iRepHoursInDay)
                        fDayStorageInput = 0
                        break
                elif fAvgResidualDemand > objDayTS.fValue and (fAvgResidualDemand - objDayTS.fValue) < objProcess.fDeratedCapacity:
                    # partially generatoin (cut off at average)
                    if fDayStorageInput > (fAvgResidualDemand - objDayTS.fValue) * objDayTS.iRepHoursInDay:
                        # full generation hour
                        objProcess.fHourlyPowerOutput_TS_YS[objDayTS.iTimeSliceIndex, indexYS] = - (fAvgResidualDemand - objDayTS.fValue)
                        fDayStorageInput -= (fAvgResidualDemand - objDayTS.fValue) * objDayTS.iRepHoursInDay
                    else:
                        # partially generatoin (cut off at all demand served)
                        objProcess.fHourlyPowerOutput_TS_YS[objDayTS.iTimeSliceIndex, indexYS] = - (fDayStorageInput / objDayTS.iRepHoursInDay)
                        fDayStorageInput = 0
                        break

    return








