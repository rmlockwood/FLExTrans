#   MixPanel
#
#   Daniel Swanson
#   SIL International
#   9/6/2024
#
#   Version 3.14 - 5/29/25 - Ron Lockwood
#    Added localization capability.
#
#   Version 3.13 - 3/10/25 - Ron Lockwood
#    Bumped to 3.13.
#
#   Version 3.12 - 11/2/24 - Ron Lockwood
#    Bumped to 3.12.
#
#   Version 3.11.1 - 9/11/24 - Ron Lockwood
#    Use new write config parameter to create setting if missing.
#
#   Version 3.11 - 9/6/24 - Ron Lockwood
#    Enhanced the functions to check for an opt out question. Use the Write Config Value function
#
#   Usage statistics logging with the online service Mixpanel
#
import ReadConfig
import functools

from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QMessageBox, QApplication

# Define _translate for convenience
_translate = QCoreApplication.translate

# Only retrieve the IP address once per session
@functools.cache
def GetIPAddress():
    import urllib
    return urllib.request.urlopen('http://ifconfig.me/ip').read().decode('utf-8')

def GetUserID(configMap, report):

    got_answer = False

    opt_out_asked = ReadConfig.getConfigVal(configMap, ReadConfig.LOG_STATISTICS_OPT_OUT_QUESTION,
                                          None, giveError=False)
    if opt_out_asked == 'n' or opt_out_asked is None:

        msgBox = QMessageBox()
        msgBox.setIcon(QMessageBox.Question)
        msgBox.setText(_translate('Mixpanel', "FLExTrans would like to send usage statistics to FLExTrans developers. "+\
                                    "No personally identifiable information is sent. These anonymous statistics will help with future development. "+\
                                    "Do you want to opt out of sending usage statistics?"))
        msgBox.setWindowTitle("FLExTrans Usage")
        msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)

        result = msgBox.exec_()
        
        if result == QMessageBox.Yes:

            ReadConfig.writeConfigValue(report, ReadConfig.LOG_STATISTICS, 'n', createIfMissing=True)
            ReadConfig.writeConfigValue(report, ReadConfig.LOG_STATISTICS_OPT_OUT_QUESTION, 'y', createIfMissing=True)
            return None
        else:
            ReadConfig.writeConfigValue(report, ReadConfig.LOG_STATISTICS_OPT_OUT_QUESTION, 'y', createIfMissing=True)
            ReadConfig.writeConfigValue(report, ReadConfig.LOG_STATISTICS, 'y', createIfMissing=True)
            got_answer = True

    if not got_answer:

        should_stat = ReadConfig.getConfigVal(configMap, ReadConfig.LOG_STATISTICS,
                                            None, giveError=False)
        if should_stat != 'y':
            return None

    userid = ReadConfig.getConfigVal(configMap, ReadConfig.LOG_STATISTICS_USER_ID,
                                     None, giveError=False)
    if not userid:
        import uuid
        userid = str(uuid.uuid1())
        ReadConfig.writeConfigValue(report, ReadConfig.LOG_STATISTICS_USER_ID, userid, createIfMissing=True)

    return userid

def LogModuleStarted(configMap, report, module_name, module_version):

    TOKEN = '6ff276f1801f0d98cb8d73ce12355c83'
    try:
        userid = GetUserID(configMap, report)
        if userid is None:
            return

        import mixpanel
        mp = mixpanel.Mixpanel(TOKEN)

        import Version
        mp.people_set(userid, {'FLExTrans Version': Version.Version})

        mp.track(userid, 'Started Module',
                 {'Module': module_name, 'Module Version': module_version,
                  'ip': GetIPAddress()})
    except:
        # fail silently
        pass
