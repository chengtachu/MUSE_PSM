# -*- coding: utf-8 -*-


class Market:
    """ create an region object  """

    def __init__(self, Market):
        self.sMarket = Market
        self.lsZone = list()            # a list of zone objects in this market
        self.lsGenCo = list()           # a list of generation companies in this market
        self.lsTransmission = list()            # a list of zone objects in this market
        #self.RegionOutput = RegionOutput()
        return


class Zone:
    """ create an country object  """

    def __init__(self, Zone):
        self.sZone = Zone
        self.iRegionIndex = 0
        self.iCountryIndex = 0
        self.lsProcessAssump = list()       # a list of country index under this region
        self.lsProcessExist = list()        # a list of country index under this region
        #self.CountryOutput = CountryOutput()
        return



