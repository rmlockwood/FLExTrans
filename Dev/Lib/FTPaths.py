#
#   FTPaths.py
#
#   Define all the paths used by FlexTrans in one place. 
#
#   Version 3.14.1 - 8/8/25 - Ron Lockwood
#   Fixes #1017. Support cluster projects.
#
#   Version 3.14 - 5/29/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.11.2 - 6/3/24 - Ron Lockwood
#    RA folder and exe names now have no spaces.
#
#   Version 3.11.1 - 5/16/24 - Ron Lockwood
#    Change the folder name too.
#
#   Version 3.11 - 5/15/24 - Ron Lockwood
#    Changed the value of RULE ASSISTANT.
#
#   Version 3.9 - 12/19/23 - Ron Lockwood
#    Addded constants for the Rule Assistant program.
#
#   Version 3.8 - 4/20/23 - Ron Lockwood
#    Use Status Bar callback function
#
#   Version 3.8.1 - 4/24/23 - Ron Lockwood
#    Constant for TreeTran.exe
#
#   Version 3.8.2 - 5/9/23 - Ron Lockwood
#    Changed HermitCrab constants to just the executable names
#

import os

CONFIG_PATH = os.path.join(os.getcwd(), "flextools.ini")
WORK_DIR    = os.path.dirname(os.path.dirname(CONFIG_PATH))
WORK_PROJECTS_DIR = os.path.dirname(WORK_DIR)
ROOT_DIR    = os.path.dirname(os.path.dirname(WORK_DIR))
WORK_PROJECT= os.path.basename(WORK_DIR)

CONFIG_DIR  = os.path.join(WORK_DIR, "Config")
BUILD_DIR   = os.path.join(WORK_DIR, "Build")
OUTPUT_DIR  = os.path.join(WORK_DIR, "Output")

TOOLS_DIR   = os.path.join(ROOT_DIR, "FlexTools", "Tools")
MODUL_FT_DIR= os.path.join(ROOT_DIR, "FlexTools", "Modules", "FLExTrans")
TRANSL_DIR  = os.path.join(MODUL_FT_DIR, "translations")
HELP_DIR    = os.path.join(ROOT_DIR, "FLExTrans Documentation")
SAMPLE_PROJECTS_DIR  = os.path.join(ROOT_DIR, "SampleFLExProjects")

MAKE_EXE    = os.path.join(TOOLS_DIR, 'make.exe')
STAMP_EXE   = os.path.join(TOOLS_DIR, 'stamp64.exe')
TREETRAN_EXE= os.path.join(TOOLS_DIR, 'TreeTran.exe')

HC_DIR             = os.path.join(TOOLS_DIR, 'HermitCrabSynthesis')
GENERATE_HC_CONFIG = 'GenerateHCConfigForFLExTrans.exe'
HC_SYNTHESIZE      = 'HCSynthByGloss.exe'
RULE_ASSISTANT_DIR = 'FLExTransRuleAssistant'
RULE_ASSISTANT     = 'FLExTransRuleAssistant.exe'