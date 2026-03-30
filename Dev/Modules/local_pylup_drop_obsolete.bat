set FILENAME=%~n1
pylupdate5 -verbose -noobsolete %FILENAME%.py -ts translations\%FILENAME%_de.ts
pylupdate5 -verbose -noobsolete %FILENAME%.py -ts translations\%FILENAME%_es.ts
pylupdate5 -verbose -noobsolete %FILENAME%.py -ts translations\%FILENAME%_fr.ts
