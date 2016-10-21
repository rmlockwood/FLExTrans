target_text.aper: bilingual.bin transfer_rules.t1x.bin source_text.aper
	cat source_text.aper | apertium-transfer -t tr.t1x transfer_rules.t1x.bin bilingual.bin > target_text.aper 2>err_log
bilingual.bin: bilingual.dix
	lt-comp lr bilingual.dix bilingual.bin
transfer_rules.t1x.bin: transfer_rules.t1x
	python fix.py transfer_rules.t1x tr.t1x
	apertium-preprocess-transfer tr.t1x transfer_rules.t1x.bin
clean:
	rm -f target_text.aper bilingual.bin transfer_rules.t1x.bin
