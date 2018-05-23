#
#   ReadConfig
#
#   Ron Lockwood
#   University of Washington, SIL International
#   12/4/14
#
#   Version 1.1 - 3/7/18 - Ron Lockwood
#    Give an error only if the report object is not None 
#
#   Functions for reading a configuration file

import re
CONFIG_FILE = 'FlexTrans.config'

def readConfig(report):
    try:
        f_handle = open(CONFIG_FILE)
    except:
        if report is not None:
            report.Error('Error reading the file: "' + CONFIG_FILE + '". Check that it is in the FlexTools folder.')
        return None
    
    my_map = {}
    for line in f_handle:
        if len(line) < 2:
            if report is not None:
                report.Error('Error reading the file: "' + CONFIG_FILE + '". No blank lines allowed.')
            return
        # Skip commented lines
        if line[0] == '#':
            continue
        # We expect lines in the form -- property=value
        if not re.search('=',line):
            if report is not None:
                report.Error('Error reading the file: "' + CONFIG_FILE + '". A line without "=" was found.')
            return
        (prop, value) = line.split('=')
        value = value.rstrip()
        # if the value has commas, save it as a list
        if re.search(',',value):
            my_list = value.split(',')
            my_map[prop] = my_list
        else:
            my_map[prop] = value
    
    return my_map

def getConfigVal(my_map, key, report):
    if key not in my_map:
        if report is not None:
            report.Error('Error in the file: "' + CONFIG_FILE + '". A value for "'+key+'" was not found.')
        return None
    else:
        return my_map[key]

def configValIsList(my_map, key, report):    
    if type(my_map[key]) is not list:
        if report is not None:
            report.Error('Error in the file: "' + CONFIG_FILE + '". The value for "'+key+'" is supposed to be a comma separated list. For a single value, end it with a comma.')
        return False
    else:
        return True
    