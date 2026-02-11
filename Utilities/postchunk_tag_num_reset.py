# Remove the zzz added to any tags
import re
import sys
f = open(sys.argv[1],"r")
lines = f.readlines()
f.close()
f = open(sys.argv[1],"w")
for line in lines:
	line = re.sub(r'<zzz',r'<',line)
	f.write(line)
f.close()
