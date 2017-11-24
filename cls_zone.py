# -*- coding: utf-8 -*-


import model_util

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



