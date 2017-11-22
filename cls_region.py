# -*- coding: utf-8 -*-


class Region:
    """ create an region object  """

    def __init__(self, Region):
        self.sRegion = Region
        self.lsCountry = list()          # a list of country index under this region
        self.lsProcess = list()          # a list of country index under this region
        #self.RegionOutput = RegionOutput()
        return


class Country:
    """ create an country object  """

    def __init__(self, Country):
        self.sCountry = Country
        self.sZone_ZN = list()              # a list of zone ID under this country
        #self.iZoneIndex_ZN = list()        # a list of zone index under this country       
        #self.CountryOutput = CountryOutput()
        return







