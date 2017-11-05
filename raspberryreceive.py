import sys
import time
import serial
import random
import threading
from PyQt4 import QtGui
import matplotlib.pyplot as plt
from multiprocessing import Queue
from matplotlib.figure import Figure
from tarjetaadquisicion import TarjetaAdquisicion
from matplotlib.backends.backend_qt4agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt4agg import NavigationToolbar2QT as NavigationToolbar

class Example(QtGui.QWidget):
    
    def __init__(self):
        super(Example, self).__init__()
        self.tituloDeGrafica = 'Todos'
        self.ejeX = 'Todos'
        self.ejeY = 'Tiempo'
        self.miFilaAuxiliar = Queue()
        self.miTarjetaAdquisicion = TarjetaAdquisicion(self.miFilaAuxiliar)
        time.sleep(2)
        self.initUI()
        self.estadoAuxiliar = False
        self.indices = {'Todos':[0,'$[V] [A] [C] [rpm]$'],'Tiempo':[0,'$t [s]$'],'Voltaje':[1,'v [V]'],'Corriente':[2,'$I [A]$'],'Temperatura':[3,'$T [C]$'],'rpm':[4,'$\omega [rpm]$']}
        
    def initUI(self):
        ## PARAMETROS DEL MOTOR
        self.miTituloIzquierdo = QtGui.QLabel('Datos de Placa')
        self.parametrosOrganizacionales = QtGui.QHBoxLayout()
        self.parametrosDePlaca1 = QtGui.QHBoxLayout()
        self.parametrosDePlaca2 = QtGui.QHBoxLayout()
        self.parametrosDePlaca3 = QtGui.QHBoxLayout()
        self.miMotor = QtGui.QLabel('Motor:')
        self.miDataMotor = QtGui.QLineEdit('Motor-001')
        self.parametrosOrganizacionales.addWidget(self.miMotor)
        self.parametrosOrganizacionales.addWidget(self.miDataMotor)
        self.miPotenciaPlaca = QtGui.QLabel('Potencia Nominal [HP]:')
        self.miDatoPotenciaPlaca = QtGui.QLineEdit(str(85))
        self.parametrosDePlaca1.addWidget(self.miPotenciaPlaca)
        self.parametrosDePlaca1.addWidget(self.miDatoPotenciaPlaca)
        self.miTensionNominal = QtGui.QLabel('Voltaje Nominal [V]:')
        self.miDataTensionNominal = QtGui.QLineEdit(str(350))
        self.parametrosDePlaca2.addWidget(self.miTensionNominal)
        self.parametrosDePlaca2.addWidget(self.miDataTensionNominal)
        self.miVelocidadNominal = QtGui.QLabel('Velocidad Nominal [rpm]:')
        self.miDataVelocidadNominal = QtGui.QLineEdit(str(3500))
        self.parametrosDePlaca3.addWidget(self.miVelocidadNominal)
        self.parametrosDePlaca3.addWidget(self.miDataVelocidadNominal)

        ## CONTROL EJECUCIÓN

        self.botonDeInicio = QtGui.QPushButton("Importar Datos")
        self.cancelButton = QtGui.QPushButton("Detener")
        self.botonDeInicializacion = QtGui.QPushButton("Descartar Prueba")
        self.botonParaPDF = QtGui.QPushButton("Crear PDF")
        #self.botonParaPDF.setStyleSheet("background-color: green")
        #self.botonParaPDF.setEnabled(False)
        self.botonDeInicio.resize(100,100)
        self.cancelButton.resize(100,100)
        self.botonDeInicio.setMinimumHeight(80)
        self.cancelButton.setMinimumHeight(80)

        self.barraControlPrograma = QtGui.QHBoxLayout()
        self.barraControlPrograma.addWidget(self.botonDeInicio)
        self.barraControlPrograma.addWidget(self.cancelButton)

        self.barraControlPostPrograma = QtGui.QHBoxLayout()
        self.barraControlPostPrograma.addWidget(self.botonDeInicializacion)
        self.barraControlPostPrograma.addWidget(self.botonParaPDF)

        ## Control de Botones
        self.botonDeInicio.clicked.connect(self.importarDatos)
        self.cancelButton.clicked.connect(self.detenerDatos)
        self.botonDeInicializacion.clicked.connect(self.inicializarTodo)
        self.botonParaPDF.clicked.connect(self.crearPDF)

        # a figure instance to plot on
        #self.figure = Figure()
        self.figure = plt.figure(figsize = (15,5))

        # this is the Canvas Widget that displays the `figure`
        # it takes the `figure` instance as a parameter to __init__
        self.canvas = FigureCanvas(self.figure)
        self.canvas.resize(500,800)
        self.canvas.setMinimumWidth(600)
        self.canvas.setMinimumHeight(300)

        # this is the Navigation widget
        # it takes the Canvas widget and a parent
        self.toolbar = NavigationToolbar(self.canvas, self)

        ### CONTROL DE GRAFICA:
        self.miTituloControlGrafica = QtGui.QLabel('Graficar:')
        self.miLegendaVS = QtGui.QLabel('vs')

        self.seleccionDeOrdenada = QtGui.QComboBox(self)
        self.seleccionDeOrdenada.addItem('Todos')
        self.seleccionDeOrdenada.addItem('Voltaje')
        self.seleccionDeOrdenada.addItem('Corriente')
        self.seleccionDeOrdenada.addItem('Temperatura')
        self.seleccionDeOrdenada.addItem('rpm')

        self.seleccionDeAbsisa = QtGui.QComboBox(self)
        self.seleccionDeAbsisa.addItem('Tiempo')
        self.seleccionDeAbsisa.addItem('Voltaje')
        self.seleccionDeAbsisa.addItem('Corriente')
        self.seleccionDeAbsisa.addItem('Temperatura')
        self.seleccionDeAbsisa.addItem('rpm')

        self.seleccionDeOrdenada.activated[str].connect(self.actualizarOrdenada)
        self.seleccionDeAbsisa.activated[str].connect(self.actualizarAbsisa)

        self.barraControlGrafica = QtGui.QHBoxLayout()
        self.barraControlGrafica.addWidget(self.seleccionDeOrdenada)
        self.barraControlGrafica.addWidget(self.miLegendaVS)
        self.barraControlGrafica.addWidget(self.seleccionDeAbsisa)

        ## GRAFICA IZQUIERDA

        capaVerticalAuxiliar = QtGui.QVBoxLayout()
        capaVerticalAuxiliar.addWidget(self.miTituloIzquierdo)
        capaVerticalAuxiliar.addLayout(self.parametrosOrganizacionales)
        capaVerticalAuxiliar.addLayout(self.parametrosDePlaca1)
        capaVerticalAuxiliar.addLayout(self.parametrosDePlaca2)
        capaVerticalAuxiliar.addLayout(self.parametrosDePlaca3)
        capaVerticalAuxiliar.addWidget(self.miTituloControlGrafica)
        capaVerticalAuxiliar.addLayout(self.barraControlGrafica)
        capaVerticalAuxiliar.addStretch(1)
        capaVerticalAuxiliar.addLayout(self.barraControlPostPrograma)
        capaVerticalAuxiliar.addLayout(self.barraControlPrograma)

        graficaV = QtGui.QVBoxLayout()

        graficaV.addWidget(self.toolbar)
        graficaV.addWidget(self.canvas)

        layoutHorizontalPrincipal = QtGui.QHBoxLayout()
        #layoutHorizontalPrincipal.addStretch(1)
        layoutHorizontalPrincipal.addLayout(capaVerticalAuxiliar)
        layoutHorizontalPrincipal.addLayout(graficaV)
        self.setMinimumHeight(500)
        
        self.setLayout(layoutHorizontalPrincipal)    
        
        self.setGeometry(300, 300, 300, 150)
        self.setWindowTitle('Adquisición de datos de Motor DC')    
        self.show()

    def actualizarOrdenada(self,text):
        self.refrescarGrafica(self.seleccionDeOrdenada.currentText(),self.seleccionDeAbsisa.currentText(),self.miTarjetaAdquisicion.obtenerUltimosDatos())

    def actualizarAbsisa(self,text):
        self.refrescarGrafica(self.seleccionDeOrdenada.currentText(),self.seleccionDeAbsisa.currentText(),self.miTarjetaAdquisicion.obtenerUltimosDatos())

    def importarDatos(self):
        self.botonDeInicio.setText("Importando Datos")
        self.estadoAuxiliar = True
        self.miTarjetaAdquisicion.recibirInformacion()
        self.botonDeInicio.setText("Importar Datos*")
        self.botonDeInicio.setStyleSheet("background-color: red")
        self.miTareaGraficaParalela = threading.Thread(target=self.actualizacionAutomaticaGrafica, args=("task",))
        self.miTareaGraficaParalela.start()

    def inicializarTodo(self):
        self.miTarjetaAdquisicion.inicializar()
        self.refrescarGrafica('Todos','Tiempo',self.miTarjetaAdquisicion.actualizarDatos())

    def crearPDF(self):
        pass

    def detenerDatos(self):
        self.estadoAuxiliar = False
        self.miTarjetaAdquisicion.detenerInformacion()
        self.botonDeInicio.setText("Importar Datos")
        self.botonDeInicio.setStyleSheet("background-color: gray")
        self.miTareaGraficaParalela.do_run = False
        self.miTareaGraficaParalela.join()

    def actualizacionAutomaticaGrafica(self,argumento):
        self.miTareaGraficaParalela = threading.currentThread()
        while getattr(self.miTareaGraficaParalela, "do_run", True):
            self.refrescarGrafica('Todos','Tiempo',self.miTarjetaAdquisicion.actualizarDatos())
            #print(len(self.miTarjetaAdquisicion.actualizarDatos()[0]))
        #print('Finalizando grafica desde adentro')

    def refrescarGrafica(self,argumentoOrdenada,argumentoAbsisa,listaDatos):
        titulo = self.miDataMotor.text()
        if argumentoOrdenada == 'Todos':
            plt.cla()
            ax1 = self.figure.add_subplot(111)
            t = listaDatos[0]#range(len(listaDatos[0]))
            v = listaDatos[1]
            c = listaDatos[2]
            T = listaDatos[3]
            r = listaDatos[4]
            plt.title(self.tituloDeGrafica)
            plt.ylabel('$[V] [A] [C] [rpm]$')
            plt.xlabel('$t [s]$')
            plt.grid()
            plt.plot(t,v,label='v')
            plt.plot(t,c,label='i')
            plt.plot(t,T,label='T')
            plt.plot(t,r,label='rpm')
            #plt.plot(t,v,'b.-',label='v',t,c,'y.-',label='i',t,T,'r.-',label='T',t,r,'g.-',label='rpm')
            plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.05),ncol=4, fancybox=True, shadow=True)
            plt.savefig(titulo+'.pdf', bbox_inches='tight')
            self.canvas.draw()
            plt.gcf().clear()
        else:
            plt.cla()
            ax1 = self.figure.add_subplot(111)
            a = listaDatos[self.indices[argumentoAbsisa][0]]
            o = listaDatos[self.indices[argumentoOrdenada][0]]
            titulo += '_'+argumentoOrdenada +'_vs_'+ argumentoAbsisa
            plt.title(titulo)
            plt.xlabel(self.indices[argumentoAbsisa][1])
            plt.ylabel(self.indices[argumentoOrdenada][1])
            plt.grid()
            plt.plot(a,o)
            plt.savefig(titulo+'.pdf', bbox_inches='tight')
            self.canvas.draw()
        
def main():
    app = QtGui.QApplication(sys.argv)
    ex = Example()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
