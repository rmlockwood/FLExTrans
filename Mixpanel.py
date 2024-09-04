def GetUserID():
    import ReadConfig
    config = ReadConfig.readConfig(None)
    should_stat = ReadConfig.getConfigVal(config, ReadConfig.LOG_STATISTICS,
                                          None, giveError=False)
    if should_stat != 'y':
        return None

    userid = ReadConfig.getConfigVal(config, ReadConfig.LOG_STATISTICS_USER_ID,
                                     None, giveError=False)
    if not userid:
        import uuid
        userid = str(uuid.uuid1())
        fout = ReadConfig.openConfigFile(None, 'a')
        fout.write(f'{ReadConfig.LOG_STATISTICS_USER_ID}={userid}\n')

    return userid

def LogModuleStarted(module_name):
    TOKEN = '6ff276f1801f0d98cb8d73ce12355c83'
    try:
        userid = GetUserID()
        if userid is None:
            return

        import mixpanel
        mp = mixpanel.Mixpanel(TOKEN)

        import Version
        mp.people_set(userid, {'FLExTrans Version': Version.Version})

        mp.track(userid, 'Started Module', {'Module': module_name})
    except:
        # fail silently
        pass
