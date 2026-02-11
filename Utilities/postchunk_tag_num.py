# Add zzz to any tags that begin with a number and have something other than the closing > after the number
# E.g. <3sg> changes to <zzz3sg>, but <3> doesn't get changed.
# The reason for doing this is that the apertium_postchunk tool treats <3sg> as <3>. This gives us a workaround.
# After the postchunk tool is run a clean up script called postchunk_tag_num_reset.py removes the zzz.
import re
import sys
f = open(sys.argv[1],"r")
lines = f.readlines()
f.close()
f = open(sys.argv[1],"w")
for line in lines:
	line = re.sub(r'<(\d[^>])',r'<zzz\1',line)
	f.write(line)
f.close()
