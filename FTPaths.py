#
#   FTPaths.py
#
#   Define all the paths used by FlexTrans in one place.
#
#   Version 3.8 - 4/20/23 - Ron Lockwood
#    Use Status Bar callback function
#

import os

CONFIG_PATH = os.path.join(os.getcwd(), "flextools.ini")

WORK_DIR    = os.path.dirname(os.path.dirname(CONFIG_PATH))
ROOT_DIR    = os.path.dirname(os.path.dirname(WORK_DIR))
WORK_PROJECT= os.path.basename(WORK_DIR)

CONFIG_DIR  = os.path.join(WORK_DIR, "Config")
BUILD_DIR   = os.path.join(WORK_DIR, "Build")
OUTPUT_DIR  = os.path.join(WORK_DIR, "Output")

TOOLS_DIR   = os.path.join(ROOT_DIR, "FlexTools", "Tools")
HELP_DIR    = os.path.join(ROOT_DIR, "FLExTrans Documentation")

MAKE_EXE    = os.path.join(TOOLS_DIR, 'make.exe')
STAMP_EXE   = os.path.join(TOOLS_DIR, 'stamp64.exe')

HC_DIR             = os.path.join(TOOLS_DIR, 'HermitCrabSynthesis')
GENERATE_HC_CONFIG = os.path.join(HC_DIR, 'GenerateHCConfig4FLExTrans', 'GenerateHCConfigForFLExTrans.exe')
HC_SYNTHESIZE      = os.path.join(HC_DIR, 'HCSynthByGloss', 'HCSynthByGloss.exe')
