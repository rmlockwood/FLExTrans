target_text.aper: bilingual.bin transfer_rules.t1x.bin source_text.aper
	${FLEXTOOLS_PATH}\apertium-transfer -t transfer_rules.t1x transfer_rules.t1x.bin bilingual.bin source_text.aper > target_text.aper 2>apertium_log.txt
bilingual.bin: bilingual.dix
	${FLEXTOOLS_PATH}\lt-comp lr bilingual.dix bilingual.bin
transfer_rules.t1x.bin: transfer_rules.t1x
	${FLEXTOOLS_PATH}\apertium-preprocess-transfer transfer_rules.t1x transfer_rules.t1x.bin
clean:
	del target_text.aper bilingual.bin transfer_rules.t1x.bin
	