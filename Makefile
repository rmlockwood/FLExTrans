target_text.aper: bilingual.bin transfer_rules.t1x.bin source_text.aper
	cat source_text.aper | apertium-transfer -t tr.t1x transfer_rules.t1x.bin bilingual.bin > target_text.aper 2>apertium_log.txt
bilingual.bin: bilingual.dix
	lt-comp lr bilingual.dix bilingual.bin
transfer_rules.t1x.bin: ../../transfer_rules.t1x
	python3 fix.py ../../transfer_rules.t1x tr.t1x
	apertium-preprocess-transfer tr.t1x transfer_rules.t1x.bin
clean:
	rm -f target_text.aper bilingual.bin transfer_rules.t1x.bin
