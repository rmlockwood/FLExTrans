import sys
f = open(sys.argv[1],"r")
lines = f.readlines()
f.close()
f = open(sys.argv[2],"w")
for line in lines:
	strippedLine = line.strip()
	if strippedLine != '<!DOCTYPE transfer PUBLIC "-//XMLmind//DTD transfer//EN"' and \
           strippedLine != '<!DOCTYPE interchunk PUBLIC "-//XMLmind//DTD interchunk//EN"' and \
           strippedLine != '<!DOCTYPE postchunk PUBLIC "-//XMLmind//DTD postchunk//EN"' and \
           strippedLine != '"transfer.dtd">' and \
           strippedLine != '"interchunk.dtd">' and \
           strippedLine != '"postchunk.dtd">':
		f.write(line)
f.close()
