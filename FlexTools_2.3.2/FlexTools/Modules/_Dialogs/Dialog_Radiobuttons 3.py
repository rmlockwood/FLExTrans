import clr
clr.AddReference("System.Windows.Forms")
clr.AddReference("System.Drawing")

from System.Windows.Forms import Application, Form, GroupBox, RadioButton, Button, DialogResult, MessageBox, FlowLayoutPanel, DockStyle
from System.Drawing import Size

class RadioChooserDialog(Form):
    def __init__(self):
        super().__init__()  # Call base class constructor
        self.Text = "Radio Chooser Dialog"
        self.InitializeComponent()

    def InitializeComponent(self):
        self.groupBox1 = GroupBox()
        self.groupBox1.Text = "Choose an option"
        self.groupBox1.Dock = DockStyle.Top  # Dock to the top to resize with the form
        self.Controls.Add(self.groupBox1)

        self.flowLayoutPanel = FlowLayoutPanel()
        self.flowLayoutPanel.Dock = DockStyle.Fill  # Fill the entire area of the GroupBox
        self.groupBox1.Controls.Add(self.flowLayoutPanel)

        self.radioButton1 = RadioButton()
        self.radioButton1.Text = "Option 1"
        self.flowLayoutPanel.Controls.Add(self.radioButton1)

        self.radioButton2 = RadioButton()
        self.radioButton2.Text = "Option 2"
        self.flowLayoutPanel.Controls.Add(self.radioButton2)

        self.okButton = Button()
        self.okButton.Text = "OK"
        self.okButton.Dock = DockStyle.Bottom  # Dock to the bottom
        self.okButton.Click += self.okButton_Click
        self.Controls.Add(self.okButton)

        self.cancelButton = Button()
        self.cancelButton.Text = "Cancel"
        self.cancelButton.Dock = DockStyle.Bottom  # Dock to the bottom
        self.cancelButton.Click += self.cancelButton_Click
        self.Controls.Add(self.cancelButton)

    def okButton_Click(self, sender, event):
        if self.radioButton1.Checked:
            MessageBox.Show(self, "Option 1 selected")
        elif self.radioButton2.Checked:
            MessageBox.Show(self, "Option 2 selected")
        else:
            MessageBox.Show(self, "Please select an option")

        self.Close()

    def cancelButton_Click(self, sender, event):
        self.Close()

if __name__ == "__main__":
    Application.EnableVisualStyles()
    Application.Run(RadioChooserDialog())
