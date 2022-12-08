import sys
import re

if len(sys.argv) < 3:
  print('usage: py -3 updateVersion.py <flextools-version> <flextrans-version>')
  exit()
  
myFileName = f'Install{sys.argv[1]}\\FLExTrans\\FlexTools\\Version.py'

try:
    f = open(myFileName, 'r')
except:
    print ('Error opening: ' + myFileName)

lines = f.readlines()
f.close()

f = open(myFileName, 'w')

for line in lines:
    
    if line.find('number') >= 0:
    
        line = re.sub(sys.argv[1], sys.argv[1] + ' (FLExTrans ' + sys.argv[2] + ')', line)
        f.write(line)
    else:
        f.write(line)

f.close()