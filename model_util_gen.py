# -*- coding: utf-8 -*-



def calNonDispatchGeneration(instance, objZone, objProcess, indexYS):
    ''' calculate non-dispatchable process hourly generation '''
    
    if "REW_WND_ON" in objProcess.sProcessName:
        if objProcess.sProcessName == "REW_WND_ON_2025":
            objProcess.fHourlyNetOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReWindOutput2025_TS[:] / 100
        elif objProcess.sProcessName == "REW_WND_ON_2530":
            objProcess.fHourlyNetOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReWindOutput2530_TS[:] / 100
        elif objProcess.sProcessName == "REW_WND_ON_3035":
            objProcess.fHourlyNetOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReWindOutput3035_TS[:] / 100
        elif objProcess.sProcessName == "REW_WND_ON_3540":
            objProcess.fHourlyNetOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReWindOutput3540_TS[:] / 100
        elif objProcess.sProcessName == "REW_WND_ON_40UP":
            objProcess.fHourlyNetOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReWindOutput40UP_TS[:] / 100

    elif "REW_WND_OFF" in objProcess.sProcessName:
        if objProcess.sProcessName == "REW_WND_OFF_2025":
            objProcess.fHourlyNetOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReOffWindOutput2025_TS[:] / 100
        elif objProcess.sProcessName == "REW_WND_OFF_2530":
            objProcess.fHourlyNetOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReOffWindOutput2530_TS[:] / 100
        elif objProcess.sProcessName == "REW_WND_OFF_3035":
            objProcess.fHourlyNetOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReOffWindOutput3035_TS[:] / 100
        elif objProcess.sProcessName == "REW_WND_OFF_3540":
            objProcess.fHourlyNetOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReOffWindOutput3540_TS[:] / 100
        elif objProcess.sProcessName == "REW_WND_OFF_4045":
            objProcess.fHourlyNetOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReOffWindOutput4045_TS[:] / 100
        elif objProcess.sProcessName == "REW_WND_OFF_4550":
            objProcess.fHourlyNetOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReOffWindOutput4550_TS[:] / 100
        elif objProcess.sProcessName == "REW_WND_OFF_50UP":
            objProcess.fHourlyNetOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReOffWindOutput50UP_TS[:] / 100

    elif objProcess.sProcessName in ["REW_PV_UTI","REW_PV_RFT"] :
        objProcess.fHourlyNetOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aRePVOutput_TS[:] / 100

    elif "CSP" in objProcess.sProcessName:
        objProcess.fHourlyNetOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aRePVOutput_TS[:] * 1.1 / 100

    # assume geothermal is 80% of all time
    elif "REW_GEO" in objProcess.sProcessName:
        objProcess.fHourlyNetOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * 0.8

    # small hydro (non-dispatchable)
    elif "REW_HYD_SM" in objProcess.sProcessName:
        objProcess.fHourlyNetOutput_TS_YS[:,indexYS] = objProcess.fDeratedCapacity * objZone.aReHydroOutput_TS[:] / 100
        
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
                objProcess.fHourlyNetOutput_TS_YS[objDayTS.iTimeSliceIndex, indexYS] = objProcess.fDeratedCapacity * fDayCF \
                * objZone.fPowerDemand_TS_YS[objDayTS.iTimeSliceIndex, indexYS] / fAvgDayDemand

        print("")
        
    return



