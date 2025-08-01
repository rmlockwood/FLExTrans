#
#   Namedtuple Demo
#

from flextoolslib import *

import os
import csv
from collections import namedtuple

#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Namedtuple Demo",
        FTM_Version    : 1,
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Illustrate how to use a namedtuple",
        FTM_Help       : None,
        FTM_Description:
"""
"""
}
                 
Feature = namedtuple("Feature", "feature, VSPs, TPs, val1, val2, desc")

#----------------------------------------------------------------
def Main(project, report, modifyAllowed=False):

    moduleFolder = os.path.dirname(__file__)
    inputCSV = os.path.join(moduleFolder, "FeaturesInput.csv")
    
    headerRow = True
    with open(inputCSV, mode="r", encoding="utf-8") as csv_file:
        for row in map(Feature._make, csv.reader(csv_file)):
            if headerRow:
                headerRow = False
                continue
            report.Info(f"Feature: {row.feature}")
            report.Info(f"   {row.desc}")
            report.Info(f"   VSPs: {row.VSPs}")
            report.Info(f"   TPs:  {row.TPs}")
            report.Info(f"   vals: {row.val1}, {row.val2}")


#----------------------------------------------------------------
FlexToolsModule = FlexToolsModuleClass(Main, docs)
            

#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
