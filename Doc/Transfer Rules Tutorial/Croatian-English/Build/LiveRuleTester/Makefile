target_text.txt: bilingual.bin transfer_rules.t1x.bin source_text.txt
	${FLEXTOOLS_PATH}\lt-proc -b -N1 -L1 bilingual.bin source_text.txt | ${FLEXTOOLS_PATH}\apertium-transfer -b -t transfer_rules.t1x transfer_rules.t1x.bin > target_text.txt 2>apertium_log.txt
bilingual.bin: bilingual.dix
	${FLEXTOOLS_PATH}\lt-comp lr bilingual.dix bilingual.bin
transfer_rules.t1x.bin: transfer_rules.t1x
	${FLEXTOOLS_PATH}\apertium-preprocess-transfer transfer_rules.t1x transfer_rules.t1x.bin
clean:
	del target_text.txt bilingual.bin transfer_rules.t1x.bin
