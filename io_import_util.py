# -*- coding: utf-8 -*-

import pandas as pd
import numpy as np


def getDataFrame(strFilePath , strSheetName):
    """import instance config"""

    fFile = pd.ExcelFile(strFilePath)
    if strSheetName != "":
        dfData = fFile.parse(strSheetName)
    else:
        dfData = fFile.parse()

    return dfData





