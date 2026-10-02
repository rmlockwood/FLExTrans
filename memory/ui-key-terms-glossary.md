---
name: ui-key-terms-glossary
description: "EN→ES→FR glossary of recurring FLExTrans UI terms as human translators settled them (crowdin-ft, Oct 2026); use when translating new .ts strings"
metadata:
  node_type: memory
  type: reference
  originSessionId: 1b2e70a8-7cf9-4823-9fc8-20eb9e9c76c4
  modified: 2026-10-02T09:29:23.745Z
---

Key-term glossary built 2026-10-02 from every `*_es.ts` / `*_fr.ts` on the **crowdin-ft** branch (commit ac00a11b, 1,240 unique English source strings), after a French and a Spanish translator
reviewed the AI-generated translations. Use it to keep new translations consistent with theirs (see [[new-strings-translate-workflow]]). Counts in parentheses = number of strings using that rendering.
Where two renderings compete, the **first one listed is the majority / preferred** form; minority forms are noted so you can recognise them, not to copy them.

## Register and regional conventions

- **Spanish = Latin American, informal tú.** Imperatives are tú forms: *selecciona* (50), *verifica* (18), *revisa* (15), *asegúrate*, *haz clic*, *ingresa*; possessive *tu/tus* (*tu clave API*).
  Usted forms (*seleccione, verifique*) essentially never appear (1 hit). No *vosotros*. Latin-American vocabulary: *archivo* (never *fichero*), *carpeta* (never *directorio*), *agregar* (26) over
  *añadir* (7), *respaldo* over *copia de seguridad*, *clúster*, *ingresar*. "Please" → *Por favor, …* (often dropped).
- **French = formal vous.** "Please …" → *Veuillez …* (40/40). Imperatives in vous form (*vérifiez, sélectionnez, exécutez le module*). French typographic space before `:` `?` `!` (*Texte source :*).
  Skipped-item log lines use a past participle: "Skipping." → *Ignoré.* Tooltips and module descriptions use the infinitive (*Ouvrir le fichier…*, *Lier les sens…*), not 3rd person (*Ouvre…*).
  Straight apostrophes and straight double quotes (`'`, `"`), not `’` or « ». Abbreviation "e.g." → *p. ex.*
- Spanish "Skipping." → *Omitiendo.*; "e.g." → *p. ej.*; straight double quotes.
- Product / module names stay in English in both: FLEx, FLExTrans, HermitCrab, STAMP, Apertium, TreeTran, Paratext, XAMPLE, MSA, GUID, API, the Build folder. Spanish sometimes leaves a tool name in
  English in running text (*la herramienta Sense Linker*, *Live Rule Tester*); French always translates it.

## Core project vocabulary

| English | Spanish | French | Notes |
|---|---|---|---|
| file | archivo (230) | fichier (217) | |
| folder | carpeta | dossier | |
| path | ruta | chemin | "path and name of the file" → *la ruta y el nombre del archivo* / *le chemin et le nom du fichier* |
| project | proyecto | projet | "FLEx project" → *proyecto FLEx* / *projet FLEx* |
| source (lang/project/text) | **fuente** or **de origen** (43 each) | source | ES split: *texto fuente, proyecto fuente, palabra fuente* vs *proyecto FLEx de origen, categoría de origen, glosa de origen*. Standalone label "Source" → *Origen* |
| target | de destino (98); objetivo (21, minority) | cible | *proyecto de destino, léxico de destino*; *objetivo* survives mainly in *texto objetivo* |
| text | texto | texte | |
| module | módulo | module | "this module" → *este módulo* / *ce module* |
| tool | herramienta | outil (l'outil) | |
| run (a module/tool) | ejecutar | exécuter | |
| settings (FLExTrans Settings) | configuración (50); *Configuraciones* for the bare title; *ajustes* rare (3) | paramètres | ES collides with "configuration" — context distinguishes |
| setting (a single one) | la configuración (del archivo…) | le paramètre | "check the … setting" → *revisa la configuración …* / *vérifier le paramètre …* |
| configuration file | archivo de configuración | fichier de configuration | |
| output | salida | sortie | "output file" → *archivo de salida* / *fichier de sortie* |
| results | resultados | résultats | |
| log (file) | registro | journal (8); *log* (7) | FR: *journal* for viewer/UI, *fichier de log* for file-name settings |
| error | error ("Error al leer…") | erreur ("Erreur de lecture…", "une erreur s'est produite") | |
| problem | problema ("Problema con…", "Hubo un problema al…") | problème ("Un problème est survenu lors de…") | |
| invalid | inválido (8) / no válido (8) | invalide | ES split evenly |
| could not find X | No se pudo encontrar | Impossible de trouver / introuvable | |
| could not open X | No se pudo abrir | Impossible d'ouvrir | |
| skipping | Omitiendo | Ignoré(e) | |
| check (verb) | verifica / revisa | vérifiez / veuillez vérifier | |
| fix | corregir | corriger | |
| select | selecciona / seleccionar | sélectionnez / sélectionner | |
| add | agregar | ajouter | |
| insert | insertar | insérer | |
| delete / remove | eliminar | supprimer | |
| edit | editar | modifier | |
| save | guardar | enregistrer | |
| overwrite | sobrescribir | écraser | |
| view / show | ver / mostrar | afficher | |
| browse | explorar | parcourir | |
| copy | copia / copiar | copie / copier | |
| backup | respaldo | sauvegarde | |
| default (by default) | por defecto (6); predeterminado (4) | par défaut | |
| value | valor | valeur | |
| list | lista | liste | |
| name | nombre | nom | |
| field / custom field | campo personalizado | champ personnalisé | "entry-level" → *a nivel de entrada* / *au niveau de l'entrée* |
| format | formato ("en formato STAMP") | format ("au format STAMP") | |
| data | datos | données | |
| export | exportar | exporter | "to Paratext" → *a Paratext* / *vers Paratext* |
| abbreviation | abreviatura | abréviation | |
| book / chapter | libro / capítulo | livre / chapitre | |
| search and replace | búsqueda y reemplazo | recherche et remplacement | |
| tag | etiqueta | étiquette (grammatical tag) / balise (XML tag) | |
| API key | clave API | clé API | |
| AI provider | proveedor de IA | fournisseur d'IA | |
| prompt (AI) | prompt | prompt | left in English |

## Linguistic / FLEx vocabulary

| English | Spanish | French | Notes |
|---|---|---|---|
| rule / rules | regla / reglas | règle / règles | |
| transfer rules | reglas de transferencia | règles de transfert | "rules file" → *archivo de reglas* / *fichier de règles* |
| transfer | transferencia | transfert | |
| synthesis | síntesis | synthèse | "HermitCrab synthesis" → *síntesis de HermitCrab* / *synthèse HermitCrab* |
| synthesize | sintetizar | synthétiser | "Synthesize by gloss" → *sintetizar por glosa* (sometimes left English) / *synthétiser par glose* |
| synthesizer | sintetizador | synthétiseur | |
| lexicon | léxico | lexique | |
| bilingual lexicon | léxico bilingüe | lexique bilingue | *diccionario/dictionnaire bilingüe/bilingue* used where English says "dictionary" |
| dictionary | diccionario | dictionnaire | |
| word | palabra | mot | |
| head word (rule element) | palabra principal | mot principal | FR phrase-level "head" → *tête* |
| headword (lexical entry, log lines, Sense Linker columns) | palabra principal / entrada | **entrée de dictionnaire** | Matches FieldWorks (`Headword` → *Entrée de dictionnaire*). *mot-vedette* was corrected out 2026-10-02 |
| dependent word | palabra dependiente | mot dépendant | |
| entry | entrada | entrée ("Manual Entry" → *Saisie manuelle*) | |
| sense | sentido (31); acepción (5, minority) | sens | |
| gloss | glosa | glose | |
| lemma | lema | lemme | |
| lexeme / lexeme form | lexema / forma del lexema | lexème / forme de lexème | |
| lexical unit | unidad léxica | unité lexicale | |
| surface form | forma superficial | forme de surface | |
| grammatical category / POS | categoría gramatical | catégorie grammaticale | "POS" is translated out in both |
| feature (grammatical) | **rasgo** (masc.) | **trait** | Matches FieldWorks (*Rasgo*, *Rasgos de flexión* / *Trait*, *Traits de flexion*). Never *característica* / *fonctionnalité* / *caractéristique* — corrected out 2026-10-02 |
| feature value | valor del rasgo | valeur du trait | |
| co-feature | rasgo asociado | trait associé | |
| split feature set | conjunto de rasgos divididos | ensemble de traits divisés | |
| attribute | atributo | attribut | |
| class / noun class | clase / clase de sustantivo | classe / classe nominale | |
| noun | sustantivo | nom (*nominale* as adj.) | |
| inflection | flexión | flexion | |
| complex form | forma compleja | forme complexe | |
| morpheme / morph(eme) type | morfema / tipo de morfema | morphème / type de morphème (*type morphologique* minority) | |
| allomorph | alomorfo | allomorphe | |
| affix / clitic | afijo / clítico | affixe / clitique | |
| prefix / suffix / infix | prefijo / sufijo / infijo | préfixe / suffixe / infixe | |
| root | raíz | racine | |
| stem | tema | radical | |
| template / slot | plantilla / espacio | modèle / emplacement | |
| parses | análisis | analyses | |
| analyzed text | texto analizado | texte analysé | |
| sentence | oración (26); frase (7, esp. "generate sentences") | phrase | |
| phrase (syntactic) | frase / sintagma | syntagme | |
| semantic domain | dominio semántico | domaine sémantique | |
| vernacular | vernáculo / lengua vernácula | vernaculaire | |
| writing system | sistema de escritura | système d'écriture | |
| macro | macro | macro | |
| interchunk / postchunk | left in English (*interchunk*, *postchunk*) | left in English | Apertium terms; ES *entre bloques* / *fragmentos posteriores* corrected out 2026-10-02 |

## FLExTrans feature / tool names

| English | Spanish | French |
|---|---|---|
| Testbed | banco de pruebas | fichier test (*banc d'essai* corrected out 2026-10-02) |
| Testbed Editor / End Testbed | Editor / Finalizar banco de pruebas | Éditeur du fichier test / Terminer le fichier test |
| Testbed Log | Registro del banco de pruebas | Journal du fichier test |
| Sense Linker (Tool) | Herramienta de enlace de sentidos (or left as *Sense Linker*) | Outil de liaison de sens |
| link / linked / unlinked | enlace, vincular / enlazar; no vinculados | lien, lier; non liés |
| Live Rule Tester | Probador de reglas en vivo / Prueba de reglas en vivo | Testeur / Outil de test de règles en direct |
| Rule Assistant | Asistente de reglas | Assistant de règles |
| AI Rule Studio | Estudio de reglas con IA | Studio de règles IA |
| cluster (projects) | clúster (10); grupo (2) | groupe / projets groupés |
| ad hoc (rules/constraint) | ad hoc | ad hoc |
| Build folder | carpeta Build | dossier Build |
| Texts & Words (FLEx area) | Textos & Palabras | Textes et Mots |
| discourse chart | tabla de discurso | tableau de discours |
| media files | archivos multimedia | fichiers médias |
| merge (texts) | combinar | fusionner |
| Browse... | Explorar... | Parcourir... |
| Bible verse | versículo | verset |

FLEx area names above follow FieldWorks' own `strings-es.xml` / `strings-fr.xml` (in `C:\Program Files\SIL\FieldWorks 9\Language Explorer\Configuration`) — check there first for any FLEx UI term.

## Known inconsistencies worth flagging to translators

- ES **source**: *fuente* vs *de origen* used interchangeably (43/43) — no rule; if new strings sit next to existing ones, match the neighbours.
- ES **target**: residual *objetivo* (mostly *texto objetivo*, *léxico objetivo*) against the dominant *de destino*.
- ES **invalid**: *inválido* vs *no válido*; ES **sense**: occasional *acepción*.
- Fixed 2026-10-02 (Ron's decisions): feature → *rasgo* / *trait*; FR testbed → *fichier test*; FR headword → *entrée de dictionnaire*; ES interchunk/postchunk → English. FR rule-element "head
  word" stays *mot principal* (FieldWorks calls a phrasal head *centre*). Left as is: the format placeholder `mot_vedette<catégorie grammaticale>…` in ExtractSourceText_fr.ts.
