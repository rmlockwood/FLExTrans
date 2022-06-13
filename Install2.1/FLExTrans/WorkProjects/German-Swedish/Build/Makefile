${TARGET_PATH}: bilingual.bin transfer_rules.t1x.bin ${SOURCE_PATH}
	${FLEXTOOLS_PATH}\apertium-transfer -t tr.t1x transfer_rules.t1x.bin bilingual.bin ${SOURCE_PATH} > ${TARGET_PATH} 2> apertium_log.txt
bilingual.bin: ${DICTIONARY_PATH}
	${FLEXTOOLS_PATH}\lt-comp lr ${DICTIONARY_PATH} bilingual.bin
transfer_rules.t1x.bin: tr.t1x
	${FLEXTOOLS_PATH}\apertium-preprocess-transfer tr.t1x transfer_rules.t1x.bin
clean:
	del ${TARGET_PATH} bilingual.bin transfer_rules.t1x.bin
