#
#   Reports.Student_Project_Report
#    - A FlexTools Module -
#
#   Produces a report on the FLEx lexicon.
#
#   C D Farrow
#   July 2024
#

from flextoolslib import *

from SIL.LCModel import (
    ILexEntry,
    ILexSense,
    )
    
#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Student Project Report (Missing glosses)",
        FTM_Version    : 2,
        FTM_ModifiesDB : False,
        FTM_Synopsis   : "Give a summary report of a student's Flex project",
        FTM_Help       : None,
        FTM_Description:
"""
""" }


#----------------------------------------------------------------

ALLENTRIES_Heading = "All entries listed alphabetically: %d"
ALLENTRIES_Help = \
"""
This listing is provided for a quick scan of inconsistency in spelling, etc.
"""

MULTISENSE_Heading = "Entries with multiple senses: %d"
MULTISENSE_Help = \
"""
This listing is provided for a quick scan of entries with multiple senses (subsenses of senses are not treated).
Be sure that you are representing the vernacular senses and not equivalents from other languages that you speak (use reversal entries to capture equivalence - not sense glosses/definitions).
Merge senses where necessary and cleanup.
If there are multiple senses belonging to the same entry but no common semantic thread of meaning, then Move Sense to New Entry (click to the left of the sense).
"""
    
LEXICALRELATIONS_Heading = "All used lexical relations: %d"
LEXICALRELATIONS_Help = \
"""
These are all the lexical relations defined in this project.
"""

MISSINGGLOSSES_Heading = "Senses with empty glosses: %d"
MISSINGGLOSSES_Help = \
"""
This listing shows all senses that need glosses to be added.
"""
#================================================================
class ReportSection:
    def __init__(self, project, report):
        self.Section = self.__class__.__name__.upper()
        self.p = project
        self.r = report
        
    def Heading(self, value = None):
        heading = eval(self.Section + "_Heading")
        if value != None:
            self.r.Info(heading % value)
        else:
            self.r.Info(heading)
        
    def Help(self):
        helpstr = eval(self.Section + "_Help")
        for line in helpstr.strip("\n").split("\n"):
            self.r.Info(f"  * {line}")
        self.r.Blank()

    def Entry(self, entry):
        for sense in entry.SensesOS:
            gloss = self.p.LexiconGetSenseGloss(sense)
            self.r.Info(f"  {entry.HeadWord} '{gloss}'",
                         self.p.BuildGotoURL(entry))

    def Sense(self, sense):
        gloss = self.p.LexiconGetSenseGloss(sense)
        POS = self.p.LexiconGetSensePOS(sense)
        Number = self.p.LexiconGetSenseNumber(sense)
        self.r.Info(f"   {Number}. '{gloss}' {POS}",
                    self.p.BuildGotoURL(sense))

    def SenseWithHeadword(self, sense):
        gloss = self.p.LexiconGetSenseGloss(sense)
        POS = self.p.LexiconGetSensePOS(sense)
        Headword = ILexEntry(sense.Owner).HeadWord
        self.r.Info(f"   {Headword}: '{gloss}' {POS}",
                    self.p.BuildGotoURL(sense))
        
    def EntryWithSenses(self, entry):
        self.r.Info(f"* {entry.HeadWord}")
        for sense in entry.SensesOS:
            self.Sense(sense)
            
    def LexicalRelation(self, lrt):
        self.r.Info(f"* {lrt}")
        for lr in lrt.MembersOC:
            for target in lr.TargetsRS:
                if target.ClassName == "LexEntry":
                    entry = ILexEntry(target)
                    self.Entry(entry)
                else: # Relations have only LexEntry or LexSense
                    sense = ILexSense(target)
                    self.SenseWithHeadword(sense)
            self.r.Blank()

#================================================================
class AllEntries(ReportSection):       

    def Run(self):
        self.Heading(self.p.LexiconNumberOfEntries())
        self.Help()
 
        for e in self.p.LexiconAllEntriesSorted():
            self.Entry(e)

class MultiSense(ReportSection):       

    def Run(self):
        multisense = []
        for e in self.p.LexiconAllEntriesSorted():
            if e.SensesOS.Count > 1:
                multisense.append(e)
        
        self.Heading(len(multisense))
        self.Help()
        for e in multisense:
            self.EntryWithSenses(e)

class LexicalRelations(ReportSection):       

    def Run(self):
        LRTs = []
        for lrt in self.p.GetLexicalRelationTypes():
            if (lrt.MembersOC.Count > 0):
                LRTs.append(lrt)
        
        self.Heading(len(LRTs))
        self.Help()
        for lrt in LRTs:
            self.LexicalRelation(lrt)

class MissingGlosses(ReportSection):       

    def Run(self):
        missingGlosses = []
        for e in self.p.LexiconAllEntriesSorted():
            for s in e.SensesOS:
                if not self.p.LexiconGetSenseGloss(s):
                    missingGlosses.append(e)
        
        self.Heading(len(missingGlosses))
        self.Help()
        for e in missingGlosses:
            self.EntryWithSenses(e)
            
#----------------------------------------------------------------

AllSections = (
    # AllEntries,
    MultiSense,
    LexicalRelations,
    None,
    MissingGlosses,
    )
    
    
#----------------------------------------------------------------

def Main(project, report, modifyAllowed):
    
    report.Info("=== Student report ===")
    report.Info(f"    {project.ProjectName()}")
    report.Info(f"    {project.LexiconNumberOfEntries()} entries")
    
    report.ProgressStart(len(AllSections))
    
    for step, sectionClass in enumerate(AllSections):
        report.ProgressUpdate(step)
        if sectionClass is None:
            report.Info("-----------------------------------------------------------")
            continue
        else:
            section = sectionClass(project, report)
        section.Run()
        report.Blank()
    
#----------------------------------------------------------------

FlexToolsModule = FlexToolsModuleClass(Main, docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    print(FlexToolsModule.Help())
