'''
Created on Nov 26, 2014

@author: Ron Lockwood

Read the configuration file in the current folder and parse it
into property, value pairs. If the value has a comma, save it as a list.

'''
import re
CONFIG_FILE = 'FlexTrans.config'

def readConfig(report):
    try:
        f_handle = open(CONFIG_FILE)
    except:
        report.Error('Error reading the file: "' + CONFIG_FILE + '". Check that it is in the FlexTools folder.')
        return None
    
    my_map = {}
    for line in f_handle:
        if len(line) < 2:
            report.Error('Error reading the file: "' + CONFIG_FILE + '". No blank lines allowed.')
            return
        # Skip commented lines
        if line[0] == '#':
            continue
        # We expect lines in the form -- property=value
        if not re.search('=',line):
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
        report.Error('Error in the file: "' + CONFIG_FILE + '". A value for "'+key+'" was not found.')
        return None
    else:
        return my_map[key]

def configValIsList(my_map, key, report):    
    if type(my_map[key]) is not list:
        report.Error('Error in the file: "' + CONFIG_FILE + '". The value for "'+key+'" is supposed to be a comma separated list. For a single value, end it with a comma.')
        return False
    else:
        return True
    