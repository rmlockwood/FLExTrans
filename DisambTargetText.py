#
#   DisambTargetText
#
#   Beth Bryson
#   SIL International
#   5/11/24
#
#   Version 3.10 - 5/12/24 - Beth Bryson
#    Prepare for adding to FLExTrans
#
#   Version 3.9.8 - 5/11/24 - Beth Bryson
#    Prototype running outside of FLExTrans
#
#
#   Take the text in the synthesis file and display it in a "disambiguation editor".
#   After the user has made changes, save the result back to the synthesis file.
#   Make a backup of the original file before changing.
#
#   TODO:
#  - Right now this crashes FlexTools.  Need to change to an approach for calling the
#    widget, closing it, and getting a return value, that is consistent with other tools in FLExTrans.
#   - Write output to the synthesis text file.  Make a backup of the version we are overwriting?
#   - Use QPalette for setting the colors (or whatever the other FLExTrans modules use)
#   - Read from an actual text file.  (right now it crashes FlexTools)
#   - Decide if this will process one sentence at a time, or a whole text.  Need scrolling.
#   - Determine directionality of text programmatically (it's hard coded for now).
#   - Improve behavior of wrapping of word boxes.
#       - Is this the real FlowLayout? Would HTML make it easier, or does that not allow combo boxes?
#       - Something's weird with the math for vertical spacing in RTL.
#       - Figure out how to limit resizing to reasonable limits, especially for shrinking (so buttons don't cover text).
#       - Use actual PyQT5 approaches for putting the buttons there--this is pretty kludgy.
#   - Put punctuation back together with words, after it was split off.
#   - Make the font size bigger?
#   - Decide if we need to allow reducing the choices to a number greater than 1
#     (that is, reduce the ambiguities, but not eliminate them).
#   - Is there an easy way to do some of this work, exit, and then come back and edit it again?
#     As long as they don't do other runs on other texts in between, that would work.
#   - Still need to figure out how STAMP makes it possible to generate ambiguities.

import sys
import re
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, QFrame
from PyQt5.QtCore import Qt, QSize, QRect, pyqtSignal

from flextoolslib import *                                                 

import ReadConfig
import Utils

from SIL.LCModel import *                                                   
#from SIL.LCModel.Core.KernelInterfaces import ITsString, ITsStrBldr         
#from SIL.LCModel.Core.Text import TsStringUtils


#----------------------------------------------------------------
# Configurables:


#----------------------------------------------------------------
# Documentation that the user sees:

docs = {FTM_Name       : "Disambiguate Target Text",
        FTM_Version    : "3.10",
        FTM_ModifiesDB : True,
        FTM_Synopsis   : "Disambiguate a translated text before inserting into the target application.",
        FTM_Help       : "",
        FTM_Description:
"""
This module will take the results of the synthesis process and open it in the Disambiguation Editor.
For each word/phrase that is ambiguous, the user can choose from among the possibilities.
The user can save the file even if not all the ambiguities are resolved.  The module could be run
again on the result of saving this text when it is only partially resolved, to finish the job in multiple runs.
""" }
                 
#----------------------------------------------------------------
# Functions and classes

class FlowLayout(QLayout):
#    def __init__(self, parent=None, margin=0, spacing=-1):
    def __init__(self, parent=None, margin=20, spacing=10):
        super().__init__(parent)
        if parent is not None:
            self.setMargin(margin)
        self.setSpacing(spacing)
        self.itemList = []

    def addItem(self, item):
        self.itemList.append(item)

    def count(self):
        return len(self.itemList)

    def itemAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList[index]
        return None

    def takeAt(self, index):
        if 0 <= index < len(self.itemList):
            return self.itemList.pop(index)
        return None

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()
        for item in self.itemList:
            size = size.expandedTo(item.minimumSize())
        return size

    def setGeometry(self, rect):
        super().setGeometry(rect)
        layout_direction = self.parentWidget().layoutDirection()  # Get layout direction from parent widget
        self.arrangeWidgets(rect, layout_direction)

    def arrangeWidgets(self, rect, layout_direction):
        if not self.itemList:
            return

        #print("x = ", rect.x(), "y = ", rect.y())
        # Set the borders for the rectangle the widgets will be drawn within
        hpad = 10
        vpad = 5
        new_x = rect.x()+hpad
        # This would change the size of the rectangle we're doing the layout in,
        # but I haven't changed the code yet to actually use it below.
        #rect.setRect(rect.x() + hpad, rect.y() +vpad, rect.width() - (2*hpad), rect.height() - (2*vpad) - 40)
        new_right =  rect.right()-hpad
        # new_height = rect.height() - btn_height
        new_height = rect.height() - 40
        


        x = new_x if layout_direction == Qt.LeftToRight else new_right
        y = rect.y()
        lineHeight = 0
        spacing = self.spacing()
        # Have we transitioned from words to buttons?  If the next button we see will be
        # the first, this will be true.  Once we have passed the first button, it will be false.
        first_button = 1
        for item in self.itemList:
            wid = item.widget()
            if wid is not None:
                # For laying out the buttons on the bottom
                if isinstance(wid, QPushButton) and first_button:
                    x = new_x
                    ## If RTL, this changes the value by double the amount of space  Why?
                    ## lineHeight is 46 and spacing is 10.  
                    #y = rect.bottom() - lineHeight - spacing
                    #print ("Bottom = ", rect.bottom())
                    if layout_direction == Qt.RightToLeft:
                        # For some reason, I have to subtract an extra 56 when it's RTL.  Why?
                        y = rect.bottom() - 96
                    else:
                        y = rect.bottom() - 40
                    first_button = 0
                    
                width = item.sizeHint().width()
                height = item.sizeHint().height()
                # Wrapping
                if (layout_direction == Qt.RightToLeft and x - width < new_x) or \
                        (layout_direction == Qt.LeftToRight and x + width > new_right):
                    x = new_x if layout_direction == Qt.LeftToRight else new_right  # Adjust x position for alignment
                    #print("lineHeight = ", lineHeight, "spacing = ", spacing)
                    y += lineHeight + spacing
                    lineHeight = 0
                #print("x = ", x, "y = ", y)
                if layout_direction == Qt.RightToLeft:
                    item.setGeometry(QRect(x-width, y, width, height))
                else:
                    item.setGeometry(QRect(x, y, width, height))
                # Adjust the x,y for the item to draw on the next time through the loop
                # x is the "beginning" of the box;
                # we compensate for the current item's width when we draw it
                if layout_direction == Qt.LeftToRight:
                    x += width + spacing
                else:
                   x -= width + spacing
                lineHeight = max(lineHeight, height)

        return QSize(rect.width(), y + lineHeight - rect.y())

class WordWidget(QWidget):
    def __init__(self, uniq_word):
        super().__init__()
        self.uniq_word = uniq_word
        self.initUI()

    def initUI(self):
        self.layout = QHBoxLayout()
        self.label = QLabel(self.uniq_word)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

        self.label.setText(self.uniq_word)

    def selectedWord(self):
        return self.uniq_word

class WordEditWidget(QWidget):
    def __init__(self, ambig_bundle):
        super().__init__()
        self.ambig_string = ambig_bundle.display
        self.ambig_orig = ambig_bundle.orig
        self.ambig_list = self.ambig_string.split('%')
        self.ambig_list.insert(0,self.ambig_string)
        self.initUI()

    def initUI(self):
        self.layout = QHBoxLayout()
        self.label = QLabel(self.ambig_string)

        self.combo_box = QComboBox()
        self.combo_box.addItems(self.ambig_list)
        self.combo_box.setStyleSheet("padding: 5px;")
        self.combo_box.currentIndexChanged.connect(self.updateLabel)

        self.layout.addWidget(self.combo_box)
        self.setLayout(self.layout)

    def updateLabel(self, index):
        self.label.setText(self.combo_box.currentText())

    def selectedWord(self):
        if '%' in self.combo_box.currentText():
            # When returning the whole ambiguity, use the original version
            #print("    Ambig currentText = ", self.combo_box.currentText())
            return self.ambig_orig
        else:
            #print("    Unique currentText = ", self.combo_box.currentText())
            return self.combo_box.currentText()
            

class WordBundle():
    def __init__(self, orig_string, display_string):
        self.orig = orig_string
        self.display = display_string
        
class DisambDialog(QDialog):
    exitedDialog = pyqtSignal(str)  # Signal for emitting edited text

    def __init__(self, text):
        super().__init__()
        self.text = text
        self.initUI()

    def initUI(self):
        # Apply stylesheet to the widget
#        self.setStyleSheet("background-color: gainsboro;")
        self.setStyleSheet("background-color: lavender;")

        layout = FlowLayout()  
#        layout = QHBoxLayout()
        self.setLayout(layout)

        self.setWindowTitle('Disambiguation Editor')
        self.setGeometry(100, 100, 800, 300)

        # Set layout direction to Right-to-Left
        self.setLayoutDirection(Qt.RightToLeft)
        # Set layout direction to Left-to-Right
#        self.setLayoutDirection(Qt.LeftToRight)
        
        self.add_words(layout)
        
        self.add_buttons(layout)
        self.show()


    def add_words(self, layout):
        # Divide the sentence into a list consisting of unique words and ambiguity bundles,
        # and reformat the ambiguity bundles
        self.currBundleList = []
        self.currBundleList = self.split_string(self.text, self.currBundleList)
        # Initialize list that will store the edited version of the string.
        self.word_edits = []

        #for word in words:
        for bundle in self.currBundleList:
            # Ambiguities
            if '%' in bundle.orig:
                # Use the widget that allows editing
                # Send it a bundle; get back just a string (the original version with %N%, not the display version without that)
                wordbox = WordEditWidget(bundle)
                wordbox.setStyleSheet("background-color: yellow; selection-background-color: lightYellow; selection-color: black; padding: 5px;")
            # No ambiguities
            else:
                # These don't need editing, so it uses a different widget
                # (Would it help to be able to edit them?)
                # This sends a string and gets back a string
                wordbox = WordWidget(bundle.display)
                wordbox.setStyleSheet("background-color: white; padding: 5px;")
            # Add each word to the display
            layout.addWidget(wordbox)
            # Build the list that reflects the current string and will store any edits made
            #print("Appending: selectedWord = ", wordbox.selectedWord() )
            self.word_edits.append(wordbox)

    def split_string(self, text, bundle_list):
        # Step 1: Separate punctuation from words (and other punct)
        # TODO: How will we reattach it after it's been edited?
        # Word-initial punctuation
        new_text = re.sub(r'([\"\(])([^\s])', r'\1 \2', self.text)
        # Word-final punctuation
        new_text = re.sub(r'([^\s])([,;:\.\?\!\"\)])', r'\1 \2', new_text)
        #print("New text: \n", new_text)
        
        # Step 2: Split text into clusters.  
        # findall returns a set of tuples correlating to the groups in the match expression.
        # First grouping matches ambiguity clusers; second matches unique words.
        # Only one will match; the other will be empty.
        clusters = re.findall(r'(%\d+%[^\d]+[^\d\s,;:\.\?\!\"\)]%)|(\S+)', new_text)
        
        # Step 3: Process clusters, to flatten the list
        # Then iterate through the clusters, adding the one with contents to the list
        for i, cluster in enumerate(clusters):
            # Ambiguity cluster matched
            if cluster[0]:
                #print("Processing ambig: ", cluster[0])
                #orig_list.append(cluster[0])
                # Remove the count
                new_cluster = cluster[0]
                new_cluster = re.sub(r'%\d+%(.+)%', r'\1', new_cluster)
                # For now, let's keep the % as the divider, even in the display
                # If we want a different divider, we could do it here
                #new_cluster = re.sub(r'%', r'|', new_cluster)
                # Make this into a bundle to be added to the list of what will display
                thisWord = WordBundle(cluster[0], new_cluster)
                
            # Unique word matched
            else:
                #print("Processing uniq: ", cluster[1])
                thisWord = WordBundle(cluster[1], cluster[1])

            # Now add the bundle to the list
            bundle_list.append(thisWord)
        
        # Step 4: Return the list of bundles
        return bundle_list

            
    def add_buttons(self, layout):
        save_button = QPushButton('Save')
        save_button.clicked.connect(self.save)
        cancel_button = QPushButton('Cancel')
        cancel_button.clicked.connect(self.cancel)
        exit_button = QPushButton('Save and Exit')
        # Do an initial save, to get the words into the editable string, so we can Exit and Save in a single click
        exit_button.clicked.connect(self.save)
        exit_button.clicked.connect(self.exit_steps)

        layout.addWidget(save_button)
        layout.addWidget(exit_button)
        layout.addWidget(cancel_button)

    # Save without exiting
    # TODO: Should we write to the output file here, or in the calling function?
    def save(self):
        edited_text = ' '.join(wordbox.selectedWord() if isinstance(wordbox, WordEditWidget) else wordbox.selectedWord() for wordbox in self.word_edits)
        print("Current version of edited text:", edited_text)
#        self.exitedDialog.emit(edited_text)  # Emit edited text signal

    # Close the widget and retain any saved edits
    # TODO: Should we write to the output file here, or in the calling function?
    def exit_steps(self):
        edited_text = ' '.join(wordbox.selectedWord() if isinstance(wordbox, WordEditWidget) else wordbox.selectedWord() for wordbox in self.word_edits)
        print("Saved text: \n", edited_text)
        print("Saving current version of edited text")
        self.exitedDialog.emit(edited_text)  # Emit edited text signal
        self.close()

    # Close the widget and discard any edits made since it was opened
    # TODO: Should we write to the output file here, or in the calling function?
    def cancel(self):
        print("Reverting to original text: \n", self.text)
        self.close()
        
def handleEditedText(text):
    print("Resulting text: \n", text)
    # This is where we would write to the output file if we want to do it after the widget closes
    return()

#----------------------------------------------------------------
# The main processing function

def MainFunction(DB, report, modify=True):
    
    if not modify:
        report.Error('You need to run this module in "modify mode."')
        return
    
    # Read the configuration file which we assume is in the current directory.
    configMap = ReadConfig.readConfig(report)
    if not configMap:
        return

    # I don't think we actually need the sourceTextName
    sourceTextName = ReadConfig.getConfigVal(configMap, ReadConfig.SOURCE_TEXT_NAME, report)
    targetSynthesis = ReadConfig.getConfigVal(configMap, ReadConfig.TARGET_SYNTHESIS_FILE, report)
    if not (sourceTextName and targetSynthesis):
        report.Error('Could not find values for the Source Text Name or Target Synthesis File"'+synFile+'".')
        return
    
    # Allow the synthesis and ana files to not be in the temp folder if a slash is present
    synFile = Utils.build_path_default_to_temp(targetSynthesis)

    try:
        f = open(synFile, encoding='utf-8')
    except:
        TargetDB.CloseProject()
        report.Error('Could not open the file: "'+synFile+'".')

    # Here are some examples of what the text might look like, for testing
#    text = "I %3%saw%thought I saw%liked% the big %2%puppy dog%cat% last year.  \nI %3%ate%tried to eat%swallowed% \"some\" %2%cotton candy%popcorn%.  \nI %2%walked%ran% \"to (the)\" %4%store%school%five-and-dime%yard% yesterday.  \n%2%He%She% %2%said%exclaimed% that %2%he%she% was %2%happy%sad%."
#    text = "%2%لرکا%لرکی% %2%خوشا%خوشی% ہے۔ \nمیں %2%چھوٹا%چھوٹی% چھائے %2%پیا%پی%۔  \nمیں %2%چھوٹا%چھوٹی% پانی %2%پیا%پی%۔"
    
    # Edit one line at a time.  This starts the disambiguator for each sentence.
    # TODO: Do we want to edit the whole text at the same time?  Is that practical?
    # We probably do need it for context, and if we didn't, we'd need more navigation controls.
    # We would need a scrollable window, not what we have now.
    for line in f:
        dialog = DisambDialog(line)
        dialog.exitedDialog.connect(handleEditedText)  # Connect signal to slot
        sys.exit(app.exec_())
    
    
    report.Info('Saved current version of "'+sourceTextName+'" after disambiguation.')

 
#----------------------------------------------------------------
# The name 'FlexToolsModule' must be defined like this:
FlexToolsModule = FlexToolsModuleClass(runFunction = MainFunction,
                                       docs = docs)
            
#----------------------------------------------------------------
if __name__ == '__main__':
    FlexToolsModule.Help()
