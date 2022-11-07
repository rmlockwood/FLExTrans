target_text.txt: transfer_rules.t3x.bin target_text2.txt
	${FLEXTOOLS_PATH}\apertium-postchunk -t transfer_rules.t3x transfer_rules.t3x.bin target_text2.txt > target_text.txt 2>apertium_log3.txt
target_text2.txt: transfer_rules.t2x.bin target_text1.txt
	${FLEXTOOLS_PATH}\apertium-interchunk -t transfer_rules.t2x transfer_rules.t2x.bin target_text1.txt > target_text2.txt 2>apertium_log2.txt
target_text1.txt: bilingual.bin transfer_rules.t1x.bin source_text.txt
	${FLEXTOOLS_PATH}\apertium-transfer -t transfer_rules.t1x transfer_rules.t1x.bin bilingual.bin source_text.txt > target_text1.txt 2>apertium_log.txt
bilingual.bin: bilingual.dix
	${FLEXTOOLS_PATH}\lt-comp lr bilingual.dix bilingual.bin
transfer_rules.t1x.bin: transfer_rules.t1x
	${FLEXTOOLS_PATH}\apertium-preprocess-transfer transfer_rules.t1x transfer_rules.t1x.bin
transfer_rules.t2x.bin: transfer_rules.t2x
	${FLEXTOOLS_PATH}\apertium-preprocess-transfer transfer_rules.t2x transfer_rules.t2x.bin
transfer_rules.t3x.bin: transfer_rules.t3x
	${FLEXTOOLS_PATH}\apertium-preprocess-transfer transfer_rules.t3x transfer_rules.t3x.bin
clean:
	del *.bin target_*.txt *log
clean_all:
	rm -f *.bin target_*.txt source_text.txt tr.t*x log err_log bilingual.dix
trace2: transfer_rules.t2x.bin target_text1.txt
	cat target_text1.txt | ${FLEXTOOLS_PATH}\apertium-interchunk -t tr.t2x transfer_rules.t2x.bin > target_text2.txt 
trace1: bilingual.bin transfer_rules.t1x.bin source_text.txt
	cat source_text.txt | ${FLEXTOOLS_PATH}\apertium-transfer -t transfer_rules.t1x transfer_rules.t1x.bin bilingual.bin > target_text1.txt

