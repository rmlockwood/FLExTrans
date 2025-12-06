

import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from System.Windows.Forms import Application, Form, GroupBox, RadioButton, Button, DialogResult, MessageBox
from System.Drawing import Point, Size

class RadioChooserDialog(Form):
    def __init__(self):
        super().__init__()  # Call base class constructor
        self.Text = "Radio Chooser Dialog"
        self.InitializeComponent()

    def InitializeComponent(self):
        self.groupBox1 = GroupBox()
        self.groupBox1.Text = "Choose an option"
        # self.groupBox1.Location = Point(26, 24)
        # self.groupBox1.Size = Size(200, 100)
        self.Controls.Add(self.groupBox1)

        self.radioButton1 = RadioButton()
        self.radioButton1.Text = "Option 1"
        # self.radioButton1.Location = Point(18, 35)
        self.groupBox1.Controls.Add(self.radioButton1)

        self.radioButton2 = RadioButton()
        self.radioButton2.Text = "Option 2"
        # self.radioButton2.Location = Point(18, 62)
        self.groupBox1.Controls.Add(self.radioButton2)

        self.okButton = Button()
        self.okButton.Text = "OK"
        # self.okButton.Location = Point(56, 145)
        self.okButton.Click += self.okButton_Click
        self.Controls.Add(self.okButton)

        self.cancelButton = Button()
        self.cancelButton.Text = "Cancel"
        # self.cancelButton.Location = Point(137, 145)
        self.cancelButton.Click += self.cancelButton_Click
        self.Controls.Add(self.cancelButton)

    def okButton_Click(self, sender, event):
        if self.radioButton1.Checked:
            MessageBox.Show("Option 1 selected")
        elif self.radioButton2.Checked:
            MessageBox.Show("Option 2 selected")
        else:
            MessageBox.Show("Please select an option")
            return

        self.Close()

    def cancelButton_Click(self, sender, event):
        self.Close()

if __name__ == "__main__":
    Application.EnableVisualStyles()
    Application.Run(RadioChooserDialog())
