${TARGET_PATH}: bilingual.bin transfer_rules.t1x.bin ${SOURCE_PATH}
	cat ${SOURCE_PATH} | apertium-transfer -t tr.t1x transfer_rules.t1x.bin bilingual.bin > ${TARGET_PATH} 2>apertium_log.txt
bilingual.bin: ${DICTIONARY_PATH}
	lt-comp lr ${DICTIONARY_PATH} bilingual.bin
transfer_rules.t1x.bin: ${TRANSFER_RULE_PATH}
	python3 fix.py ${TRANSFER_RULE_PATH} tr.t1x
	apertium-preprocess-transfer tr.t1x transfer_rules.t1x.bin
clean:
	rm -f ${TARGET_PATH} bilingual.bin transfer_rules.t1x.bin
