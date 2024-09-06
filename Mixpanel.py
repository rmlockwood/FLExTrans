#   MixPanel
#
#   Daniel Swanson
#   SIL International
#   9/6/2024
#
#   Version 3.11 - 9/6/24 - Ron Lockwood
#    Enhanced the functions to check for an opt out question. Use the Write Config Value function
#
#   Usage statistics logging with the online service Mixpanel
#
import ReadConfig
import functools

# Only retrieve the IP address once per session
@functools.cache
def GetIPAddress():
    import urllib
    return urllib.request.urlopen('http://ifconfig.me/ip').read().decode('utf-8')

def GetUserID(configMap, report):

    got_answer = False

    opt_out_asked = ReadConfig.getConfigVal(configMap, ReadConfig.LOG_STATISTICS_OPT_OUT_QUESTION,
                                          None, giveError=False)
    if opt_out_asked == 'n':

        from System.Windows.Forms import (MessageBox, MessageBoxButtons, MessageBoxIcon, DialogResult)

        result = MessageBox.Show("FLExTrans would like to send usage statistics to FLExTrans developers. "+\
                                    "No personally identifiable information is sent. These anonymous statistics will help with future development. "+\
                                    "Do you want to opt out of sending usage statistics?", "FLExTrans Usage",
                                    MessageBoxButtons.YesNo, MessageBoxIcon.Question)

        if result == DialogResult.Yes:

            ReadConfig.writeConfigValue(report, ReadConfig.LOG_STATISTICS, 'n')
            ReadConfig.writeConfigValue(report, ReadConfig.LOG_STATISTICS_OPT_OUT_QUESTION, 'y')
            return None
        else:
            ReadConfig.writeConfigValue(report, ReadConfig.LOG_STATISTICS_OPT_OUT_QUESTION, 'y')
            ReadConfig.writeConfigValue(report, ReadConfig.LOG_STATISTICS, 'y')
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
        ReadConfig.writeConfigValue(report, ReadConfig.LOG_STATISTICS_USER_ID, userid)

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
