<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE TS>
<TS version="2.1" language="de" sourcelanguage="en">
<context>
    <name>WorkOnRulesWithAI</name>
    <message>
        <location filename="../WorkOnRulesWithAI.py" line="49"/>
        <source>This module uses AI to create new Apertium transfer rules or modify existing ones in the transfer rules file. You describe the rule you want; the AI drafts it, it is validated, and you review and approve it before it is written.</source>
        <translation>Dieses Modul verwendet KI, um neue Apertium-Transferregeln zu erstellen oder bestehende in der Transferregeldatei zu ändern. Sie beschreiben die gewünschte Regel; die KI entwirft sie, sie wird validiert, und Sie überprüfen und genehmigen sie, bevor sie geschrieben wird.</translation>
    </message>
    <message>
        <location filename="../WorkOnRulesWithAI.py" line="50"/>
        <source>Work on Rules with AI</source>
        <translation>Regeln mit KI bearbeiten</translation>
    </message>
    <message>
        <location filename="../WorkOnRulesWithAI.py" line="53"/>
        <source>Create or modify Apertium transfer rules with AI assistance.</source>
        <translation>Apertium-Transferregeln mit KI-Unterstützung erstellen oder ändern.</translation>
    </message>
    <message>
        <location filename="../WorkOnRulesWithAI.py" line="101"/>
        <source>This module sends your rule description, the transfer file's categories, attributes, and the project's grammatical categories, features, and affixes to your configured AI provider ({provider}) to generate transfer rules. Also, if you chose to include example language data, that will be sent as well. Your lexicon entries and texts are not sent (except for what is in the example data). Do you want to allow this?
There is a separate setting for sending FLEx project names.</source>
        <translation>Dieses Modul sendet Ihre Regelbeschreibung, die Kategorien und Attribute der Transferdatei sowie die grammatischen Kategorien, Merkmale und Affixe des Projekts an Ihren konfigurierten KI-Anbieter ({provider}), um Transferregeln zu generieren. Wenn Sie außerdem sprachliche Beispieldaten einbezogen haben, werden diese ebenfalls gesendet. Ihre Lexikoneinträge und Texte werden nicht gesendet (außer dem, was in den Beispieldaten enthalten ist). Möchten Sie dies erlauben?
Für das Senden der FLEx-Projektnamen gibt es eine separate Einstellung.</translation>
    </message>
    <message>
        <location filename="../WorkOnRulesWithAI.py" line="147"/>
        <source>AI rule assistance was declined. No data was sent.</source>
        <translation>Die KI-Regelunterstützung wurde abgelehnt. Es wurden keine Daten gesendet.</translation>
    </message>
    <message>
        <location filename="../WorkOnRulesWithAI.py" line="139"/>
        <source>Before you can use this module, choose the AI Provider and AI Model in the FLExTrans Settings tool, in the AI Assistant section (shown in the Full view). Then come back to this module; it will ask for your API key.

Do you want to open the Settings tool now?</source>
        <translation>Bevor Sie dieses Modul verwenden können, wählen Sie den KI-Anbieter und das KI-Modell im FLExTrans-Einstellungswerkzeug im Abschnitt KI-Assistent (sichtbar in der Ansicht Vollständig). Kommen Sie dann zu diesem Modul zurück; es wird nach Ihrem API-Schlüssel fragen.

Möchten Sie das Einstellungswerkzeug jetzt öffnen?</translation>
    </message>
    <message>
        <location filename="../WorkOnRulesWithAI.py" line="161"/>
        <source>No API key provided for {provider}; nothing was done.</source>
        <translation>Kein API-Schlüssel für {provider} angegeben; es wurde nichts getan.</translation>
    </message>
    <message>
        <location filename="../WorkOnRulesWithAI.py" line="172"/>
        <source>Transfer rules file not found: {path}</source>
        <translation>Transferregeldatei nicht gefunden: {path}</translation>
    </message>
    <message>
        <location filename="../WorkOnRulesWithAI.py" line="182"/>
        <source>Missing WorkOnRulesWithAI-Conventions.md and/or transfer.dtd in {libDir}. Reinstall FLExTrans or copy those files there.</source>
        <translation>WorkOnRulesWithAI-Conventions.md und/oder transfer.dtd fehlen in {libDir}. Installieren Sie FLExTrans neu oder kopieren Sie diese Dateien dorthin.</translation>
    </message>
    <message>
        <location filename="../WorkOnRulesWithAI.py" line="194"/>
        <source>AI prompt logging is on. Prompts and responses are appended to: {path}</source>
        <translation>Die Protokollierung der KI-Prompts ist eingeschaltet. Prompts und Antworten werden angehängt an: {path}</translation>
    </message>
    <message>
        <location filename="../WorkOnRulesWithAI.py" line="150"/>
        <source>The configured AI model ({model}) goes with {owner}, not {provider}. Fix the AI Model setting in the FLExTrans Settings tool.</source>
        <translation>Das konfigurierte KI-Modell ({model}) gehört zu {owner}, nicht zu {provider}. Korrigieren Sie die Einstellung KI-Modell im FLExTrans-Einstellungswerkzeug.</translation>
    </message>
    <message>
        <location filename="../WorkOnRulesWithAI.py" line="223"/>
        <source>Could not open the target FLEx project. Check the target-project setting and try again.</source>
        <translation>Das Ziel-FLEx-Projekt konnte nicht geöffnet werden. Prüfen Sie die Einstellung für das Zielprojekt und versuchen Sie es erneut.</translation>
    </message>
</context>
</TS>
