Rem convert_translation_files.bat [ts file name without extension, e.g. Linker]
Rem TODO: update once we know the actual format from CrowdIn
qt-tools lconvert %1.ts -o %1.qm
