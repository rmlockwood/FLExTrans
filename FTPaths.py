#
#   FTPaths.py
#
#   Define all the paths used by FlexTrans in one place.
#

import os

# *** I suggest replacing all occurences of CONFIG_PATH with the relevant
# paths below. ***
CONFIG_PATH = os.path.join(os.getcwd(), "flextools.ini")

WORK_DIR    = os.path.dirname(os.path.dirname(CONFIG_PATH))
ROOT_DIR    = os.path.dirname(os.path.dirname(WORK_DIR))

CONFIG_DIR  = os.path.join(WORK_DIR, "Config")
BUILD_DIR   = os.path.join(WORK_DIR, "Build")
OUTPUT_DIR  = os.path.join(WORK_DIR, "Output")

TOOLS_DIR   = os.path.join(ROOT_DIR, "FlexTools", "Tools")
HELP_DIR    = os.path.join(ROOT_DIR, "FLExTrans Documentation")

MAKE_EXE    = os.path.join(TOOLS_DIR, 'make.exe')
STAMP_EXE   = os.path.join(TOOLS_DIR, 'stamp32.exe')
