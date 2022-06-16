target_text.aper: transfer_rules.t3x.bin target_text2.aper
	cat target_text2.aper | apertium-postchunk tr.t3x transfer_rules.t3x.bin > target_text.aper 2>>err_log
target_text2.aper: transfer_rules.t2x.bin target_text1.aper
	cat target_text1.aper | apertium-interchunk tr.t2x transfer_rules.t2x.bin > target_text2.aper 2>>err_log
target_text1.aper: bilingual.bin transfer_rules.t1x.bin source_text.aper
	cat source_text.aper | apertium-transfer tr_a.t1x transfer_rules.t1x.bin bilingual.bin > target_text1.aper 2>>err_log
bilingual.bin: bilingual.dix
	lt-comp lr bilingual.dix bilingual.bin
transfer_rules.t1x.bin: transfer_rules_a.t1x
	python fix.py transfer_rules_a.t1x tr_a.t1x
	apertium-preprocess-transfer tr_a.t1x transfer_rules.t1x.bin
transfer_rules.t2x.bin: transfer_rules.t2x
	python fix.py transfer_rules.t2x tr.t2x
	apertium-preprocess-transfer tr.t2x transfer_rules.t2x.bin
transfer_rules.t3x.bin: transfer_rules.t3x
	python fix.py transfer_rules.t3x tr.t3x
	apertium-preprocess-transfer tr.t3x transfer_rules.t3x.bin
clean:
	rm -f *.bin target_*.aper *log
clean_all:
	rm -f *.bin target_*.aper source_text.aper tr.t*x tr_a.t*x log err_log bilingual.dix
trace2: transfer_rules.t2x.bin target_text1.aper
	cat target_text1.aper | apertium-interchunk -t tr.t2x transfer_rules.t2x.bin > target_text2.aper 
trace1: bilingual.bin transfer_rules.t1x.bin source_text.aper
	cat source_text.aper | apertium-transfer -t tr_a.t1x transfer_rules.t1x.bin bilingual.bin > target_text1.aper

