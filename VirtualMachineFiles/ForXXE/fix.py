import sys
f = open(sys.argv[1],"r")
lines = f.readlines()
f.close()
f = open(sys.argv[2],"w")
for line in lines:
	if line != '<!DOCTYPE transfer PUBLIC "-//XMLmind//DTD transfer//EN"'+'\n' and \
           line != '<!DOCTYPE interchunk PUBLIC "-//XMLmind//DTD interchunk//EN"'+'\n' and \
           line != '<!DOCTYPE postchunk PUBLIC "-//XMLmind//DTD postchunk//EN"'+'\n' and \
           line != '"transfer.dtd">'+'\n' and \
           line != '"interchunk.dtd">'+'\n' and \
           line != '"postchunk.dtd">'+'\n':
		f.write(line)
f.close()
