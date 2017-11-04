import sys
from PyQt4 import QtGui, QtCore
"""
app = QtGui.QApplication(sys.argv)
window = QtGui.QWidget()

window.setGeometry(50,50,300,500)
window.setWindowTitle('My Motor Control')
window.show()
app.exec_()

"""
class Window(QtGui.QMainWindow):
	def __init__(self):
		super(Window, self).__init__()
		self.setGeometry(50,50,500,300)
		self.setWindowTitle('DC motor control')
		self.setWindowIcon(QtGui.QIcon('logoBueno.png'))

		extractAction = QtGui.QAction('&SALIR', self)
		extractAction.setShortcut('Ctrl+Q')
		extractAction.setStatusTip('Leave the app')
		extractAction.triggered.connect(self.closeApplication)

		# Editor
		openEditor = QtGui.QAction("&Editor",self)
		openEditor.setShortcut("Control+O")
		openEditor.setStatusTip('Abrir Archivo')
		openEditor.triggered.connect(self.editor)

		openFile = QtGui.QAction("&Open File",self)
		openFile.setShortcut("Control+E")
		openFile.setStatusTip('Abrir Archivo')
		openFile.triggered.connect(self.abrirArchivo)
		
		saveFile = QtGui.QAction("&Save File",self)
		saveFile.setShortcut("Control+S")
		saveFile.setStatusTip('Guardar Archivo')
		saveFile.triggered.connect(self.guardarArchivo)

		self.statusBar()
		
		mainMenu = self.menuBar()
		fileMenu = mainMenu.addMenu('&File')
		fileMenu.addAction(extractAction)

		editorMenu = mainMenu.addMenu("&Editor")
		editorMenu.addAction(openEditor)
		editorMenu.addAction(openFile)
		editorMenu.addAction(saveFile)

		self.home()

	def home(self):
		boton = QtGui.QPushButton('Quit',self)
		boton.clicked.connect(self.closeApplication)
		
		boton.resize(100,100)
		#boton.minimumSizeHint()
		boton.move(100,100)

		otraAction = QtGui.QAction(QtGui.QIcon('logoBueno.png'), 'Flee',self)
		otraAction.triggered.connect(self.closeApplication)
		self.toolBar = self.addToolBar('Extracition')
		self.toolBar.addAction(otraAction)

		# Font

		fontChoice = QtGui.QAction('Fonty',self)
		fontChoice.triggered.connect(self.seleccionFuente)
		#self.toolBar = self.addToolBar('Font')	# Crear otra barra o hacer todo en una
		self.toolBar.addAction(fontChoice)

		# Colour
		color = QtGui.QColor(0,0,0)
		fontColor = QtGui.QAction('Accion para el color',self)
		fontColor.triggered.connect(self.seleccionColor)

		self.toolBar.addAction(fontColor)

		checkBox = QtGui.QCheckBox('Alargar Ventana',self)
		checkBox.move(100,100)
		checkBox.toggle()
		checkBox.stateChanged.connect(self.alargarVentana)

		self.progress = QtGui.QProgressBar(self)
		self.progress.setGeometry(200,80,250,20)
		self.miBoton = QtGui.QPushButton('Descargar',self)
		self.miBoton.move(200,120)
		self.miBoton.clicked.connect(self.download)
		print(self.style().objectName())

		self.styleChoice = QtGui.QLabel('Windows', self)

		comboBox = QtGui.QComboBox(self)
		comboBox.addItem('motif')
		comboBox.addItem('Windows')
		comboBox.addItem('cde')
		comboBox.addItem('Plastique')
		comboBox.addItem('Cleanlooks')
		comboBox.addItem('windowsvista')

		comboBox.move(50,250)
		self.styleChoice.move(50,150)
		comboBox.activated[str].connect(self.style_choice)

		calendario = QtGui.QCalendarWidget(self)
		calendario.move(200,120)
		calendario.resize(200,200)

		self.show()

	def abrirArchivo(self):
		name = QtGui.QFileDialog.getOpenFileName(self,'Open File')
		file = open(name,'r')
		self.editor()
		with file:
			text = file.read()
			self.textEdit.setText(text)

	def guardarArchivo(self):
		name = QtGui.QFileDialog.getSaveFileName(self,'Save File')
		file = open(name,'w')
		text = self.textEdit.toPlainText()
		file.write(text)
		file.close()

	def seleccionColor(self):
		color = QtGui.QColorDialog.getColor()
		self.styleChoice.setStyleSheet("QWidget { background-color: %s}" % color.name())

	def editor(self):
		self.textEdit = QtGui.QTextEdit()
		self.setCentralWidget(self.textEdit)

	def seleccionFuente(self):
		font,valid = QtGui.QFontDialog.getFont()
		if valid:
			self.styleChoice.setFont(font)

	def style_choice(self,text):
		self.styleChoice.setText(text)
		QtGui.QApplication.setStyle(QtGui.QStyleFactory.create(text))

	def download(self):
		self.completed = 0
		while(self.completed<100):
			self.completed+=0.0001
			self.progress.setValue(self.completed)


	def alargarVentana(self,state):
		if state == QtCore.Qt.Checked:
			self.setGeometry(50,50,1000,120)
		else:
			self.setGeometry(50,50,500,120)

	def closeApplication(self):
		choice = QtGui.QMessageBox.question(self,'Leaving so soon?','Are you sure you want to exit the program?',QtGui.QMessageBox.Yes | QtGui.QMessageBox.No)
		if choice == QtGui.QMessageBox.Yes:
			print('Adios')
			sys.exit()
		else:
			pass
		

def run():
	app = QtGui.QApplication(sys.argv)
	GUI = Window()
	sys.exit(app.exec_())

run()
#window.mainloop()
