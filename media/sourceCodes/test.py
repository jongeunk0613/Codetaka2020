import os, subprocess, sys
from datetime import datetime
from PyQt5.QtWidgets import *

class ChangeOldModifiedFileModeIntoReadOnlyWidget(QWidget):

	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		self.label = QLabel()

		label_title = QLabel("****Change old-modified files' mode into read-only****", self)
		label_path = QLabel("Choose Directory to change", self)
		label_days = QLabel("Files older than how many days do you wish to change to read-only mode?", self)

		pushButton_finder = QPushButton("Finder Open")
		#pushButton_change = QPushButton("Enter")

		self.lineEdit_days = QLineEdit(self)
		self.textEdit_output = QTextEdit(self)

		hbox_title = QHBoxLayout()
		hbox_title.addStretch(1)
		hbox_title.addWidget(label_title)
		hbox_title.addStretch(1)

		hbox_path = QHBoxLayout()
		hbox_path.addWidget(label_path)
		hbox_path.addStretch(1)
		hbox_path.addWidget(pushButton_finder)
		self.path = ""
		pushButton_finder.clicked.connect(self.pushFinderOpenButtonClicked)

		hbox_days = QHBoxLayout()
		hbox_days.addWidget(label_days)
		hbox_days.addStretch(1)
		hbox_days.addWidget(self.lineEdit_days)
		#hbox_days.addWidget(pushButton_change)
		self.days = 0
		self.lineEdit_days.returnPressed.connect(self.dayEntered)
		#pushButton_change.clicked.connect(self.dayEntered)
		#pushButton_change.setShortcut("Return")

		hbox_output = QHBoxLayout()
		self.textEdit_output.resize(400, 100)
		hbox_output.addWidget(self.textEdit_output)


		vbox = QVBoxLayout()
		vbox.addLayout(hbox_title)
		vbox.addLayout(hbox_path)
		vbox.addLayout(hbox_days)
		vbox.addLayout(hbox_output)
		vbox.addStretch(5)

		self.setLayout(vbox)

	def pushFinderOpenButtonClicked(self):
		options = QFileDialog.Options()
		options |= QFileDialog.ShowDirsOnly
		self.path = QFileDialog.getExistingDirectory(self, "select directory")

		subprocess.getstatusoutput("chmod 777 " + self.path + "/*")
		#self.textEdit_output.setText("before changing mode")
		self.printCurrentDir()

	def dayEntered(self):
		self.days = int(self.lineEdit_days.text())
		self.changeReadOnly()

	def printCurrentDir(self):
		self.textEdit_output.setText(subprocess.getstatusoutput("ls -l /" + self.path)[1])

	def changeReadOnly(self):
		flist = os.listdir(self.path)
		nowtime = datetime.now()
		#print("\nfiles that have been modified over %d days ago" % days)
		for fname in flist:
			cur_fname = self.path + "/" + fname
			mtime = datetime.fromtimestamp(os.path.getmtime(cur_fname))
			difftime = (nowtime - mtime).days
			if difftime >= self.days:
				#print(subprocess.getstatusoutput("ls -l " + cur_fname)[1])
				os.chmod(cur_fname, 0o444)
		self.printCurrentDir()
		
	def tellStatus(self):
		print("status!")

class ChangeMainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		self.initUI()

	def initUI(self):
		widget = ChangeOldModifiedFileModeIntoReadOnlyWidget()
		self.setCentralWidget(widget)

		self.setWindowTitle('Read-Only Program')
		self.setGeometry(10, 300, 600, 400)
		self.show()

if __name__ == '__main__':
	app = QApplication(sys.argv)
	ex = ChangeMainWindow()
	sys.exit(app.exec_())